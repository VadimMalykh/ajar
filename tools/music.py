"""Ajar's music on trial: pieces written in the manner of Doom's own music and
turned into MIDI files by this script. GZDoom plays them as it plays Doom's.

How they are made follows from looking at the music of Doom II (Bobby Prince)
and of Sigil (James Paddock), 2026-11-23: every piece there was read note by
note for speed, instruments, key, riffs, drums and form. Nothing of theirs is
copied; what is taken is the way such a piece is built:

  - a bass riff ONE bar long with a fixed rhythm, on the key note a third to
    a half of the time, coloured by b3, 4, 5, b7 (and b2, b5 as passing dirt);
  - the riff goes in groups of four bars, the fourth with a turn, and is
    moved whole to the 4th, the flat 6th and the flat 7th, as in a blues;
  - a guitar doubles the riff an octave up, two notes of five as bare fifths;
  - instruments come in and drop out by blocks of 4 or 8 bars, one tune at a
    time, over an organ or strings holding plain triads;
  - drums: even hats or ride, snare on the back beats, the kick stumbling
    after the bass, a tom fill at the end of every fourth bar;
  - everything exactly on the grid; 75 to 140 beats a minute; 1.5 to 4
    minutes, then round again;
  - the instruments Doom uses most: picked bass, overdriven and distorted
    guitar, rock organ, synth bass, strings, harpsichord, pizzicato,
    tubular bells, timpani.

A piece is written as bars of steps (16 to the bar in 4/4). A pattern is one
bar: a token a step.

    1 b2 2 b3 3 4 b5 5 b6 6 b7 7   the note that many steps of the scale above the key note
    ' and ,                        an octave up, an octave down (1' b7,)
    ^ * q m M                      with its fifth; fifth and octave; fourth; minor triad; major triad
    !                              louder
    -                              the note before goes on
    .                              silence

A form is the list of a voice's bars: `A` a pattern, `A+5` the pattern moved
up five semitones, `A<` the pattern backwards, `_` a silent bar.

    python3 tools/music.py DIR    writes the .mid files to DIR and prints what each piece is
    music.make_all()              what tools/build.py puts into the package: music/<LUMP>.mid
                                  and the list ajmusic.txt (LUMP|Title|what it is for), read by
                                  the sound lab (src/zscript/soundlab.zs)

No map plays any of it yet: the set is there to be judged by ear in the sound
lab (MAP=SOUND ./run.sh).
"""
import random
import re
import struct

PPQ = 480
DEG = {"1": 0, "b2": 1, "2": 2, "b3": 3, "3": 4, "4": 5, "b5": 6, "5": 7, "b6": 8, "6": 9, "b7": 10, "7": 11}
SHAPE = {"": (0,), "^": (0, 7), "*": (0, 7, 12), "q": (0, 5), "m": (0, 3, 7), "M": (0, 4, 7)}
TOKEN = re.compile(r"(b?[1-7])([',]*)([\^*qmM]?)(!?)")
BAR = re.compile(r"([A-Za-z]\w*?)(<?)([+-]\d+)?")
DRUMS = 9

# General MIDI programs
PIANO, HARPSI, BELLS, ORGAN, MUTED, OVERDRIVE, DISTORTION = 0, 6, 14, 18, 28, 29, 30
PICKBASS, FRETLESS, SYNBASS, CELLO, CONTRABASS, PIZZ, HARP, TIMPANI = 34, 35, 39, 42, 43, 45, 46, 47
STRINGS, SLOWSTR, CHOIR, SYNBRASS, SQUARE, POLYSYNTH = 48, 49, 52, 62, 80, 90
# percussion keys
KICK, KICK2, SNARE, ESNARE, HAT, OHAT, CRASH, RIDE, RBELL = 36, 35, 38, 40, 42, 46, 49, 51, 53
TOM1, TOM2, TOM3, TOM4, WOOD_HI, WOOD_LO = 48, 47, 45, 41, 76, 77


def parse(pattern, steps):
    """One bar -> (steps the bar's start goes on holding the bar before, [(start, length, semitones, loud)])."""
    toks = pattern.split()
    if len(toks) != steps:
        raise ValueError(f"{len(toks)} steps, not {steps}: {pattern}")
    events, tie = [], 0
    for i, tok in enumerate(toks):
        if tok == ".":
            continue
        if tok == "-":
            if events and events[-1][0] + events[-1][1] == i:
                events[-1][1] += 1
            elif not events and tie == i:
                tie += 1
            else:
                raise ValueError(f"'-' after a silence at step {i + 1}: {pattern}")
            continue
        m = TOKEN.fullmatch(tok)
        if not m:
            raise ValueError(f"not a note: {tok} in {pattern}")
        base = DEG[m[1]] + 12 * (m[2].count("'") - m[2].count(","))
        events.append([i, 1, tuple(base + s for s in SHAPE[m[3]]), bool(m[4])])
    return tie, [tuple(e) for e in events]


class Piece:
    def __init__(self, title, bpm, steps=16, per_beat=4, sig=(4, 4), seed=1):
        self.title, self.bpm, self.steps, self.per_beat, self.sig = title, bpm, steps, per_beat, sig
        self.tick = PPQ // per_beat             # MIDI ticks to a step
        self.voices = []
        self.bars = None
        self.rng = random.Random(seed)

    def _bars(self, form, who):
        form = form.split() if isinstance(form, str) else list(form)
        if self.bars is None:
            self.bars = len(form)
        if len(form) != self.bars:
            raise ValueError(f"{self.title}: {who} has {len(form)} bars, not {self.bars}")
        return form

    def voice(self, name, program, root, patterns, form, vel=90, gate=0.85, volume=100, pan=64, reverb=40):
        """A pitched voice. `root` is the MIDI note of the key note in this voice's register."""
        form = self._bars(form, name)
        notes, open_ = [], []              # [start step, length in steps, pitch, loudness]; indices still sounding
        for b, tok in enumerate(form):
            if tok == "_":
                open_ = []
                continue
            m = BAR.fullmatch(tok)
            if not m or m[1] not in patterns:
                raise ValueError(f"{self.title}: {name}: no pattern for '{tok}'")
            tie, events = parse(patterns[m[1]], self.steps)
            if m[2]:                            # backwards
                tie, events = 0, sorted((self.steps - s - n, n, p, loud) for s, n, p, loud in events)
            shift = int(m[3] or 0)
            for i in open_ if tie else ():
                notes[i][1] += tie
            if not (tie == self.steps and not events):
                open_ = []
            for s, n, ps, loud in events:
                v = max(1, min(127, vel + (14 if loud else 0) + self.rng.randint(-3, 3)))
                first = len(notes)
                for p in ps:
                    p += root + shift
                    if not 12 <= p <= 115:
                        raise ValueError(f"{self.title}: {name}: note {p} out of range in bar {b + 1}")
                    notes.append([b * self.steps + s, n, p, v])
                if s + n == self.steps:
                    open_ = list(range(first, len(notes)))
        used = {v["channel"] for v in self.voices}
        channel = next(c for c in range(16) if c != DRUMS and c not in used)
        self.voices.append(dict(name=name, channel=channel, program=program, volume=volume, pan=pan, reverb=reverb,
                                gate=gate, notes=notes))

    def drums(self, patterns, form, vel=96, volume=105):
        """patterns: name -> {key: 'x..X..o.'}: x a hit, X a loud one, o a soft one."""
        form = self._bars(form, "drums")
        notes = []
        for b, tok in enumerate(form):
            if tok == "_":
                continue
            for key, row in patterns[tok].items():
                if len(row) != self.steps:
                    raise ValueError(f"{self.title}: drums {tok}: {len(row)} steps, not {self.steps}")
                for s, c in enumerate(row):
                    if c != ".":
                        v = vel + {"x": 0, "X": 18, "o": -30}[c] + self.rng.randint(-3, 3)
                        notes.append([b * self.steps + s, 1, key, max(1, min(127, v))])
        self.voices.append(dict(name="drums", channel=DRUMS, program=0, volume=volume, pan=64, reverb=30, gate=0.5,
                                notes=notes))

    def seconds(self):
        return self.bars * self.steps / self.per_beat * 60.0 / self.bpm

    def midi(self):
        def var(n):
            out = [n & 127]
            while n > 127:
                n >>= 7
                out.append(0x80 | (n & 127))
            return bytes(reversed(out))

        def track(events):                      # [(tick, order, bytes)]
            out, last = b"", 0
            for t, _, data in sorted(events, key=lambda e: (e[0], e[1])):
                out += var(t - last) + data
                last = t
            return b"MTrk" + struct.pack(">I", len(out)) + out

        end = self.bars * self.steps * self.tick
        title = self.title.encode("ascii", "replace")
        den = {1: 0, 2: 1, 4: 2, 8: 3}[self.sig[1]]
        tracks = [track([(0, 0, b"\xff\x03" + var(len(title)) + title),
                         (0, 1, b"\xff\x51\x03" + int(60e6 / self.bpm).to_bytes(3, "big")),
                         (0, 2, b"\xff\x58\x04" + bytes([self.sig[0], den, 24, 8])),
                         (end, 9, b"\xff\x2f\x00")])]
        for v in self.voices:
            c = v["channel"]
            ev = [(0, 0, bytes([0xB0 | c, 7, v["volume"]])), (0, 0, bytes([0xB0 | c, 10, v["pan"]])),
                  (0, 0, bytes([0xB0 | c, 91, v["reverb"]])), (0, 0, bytes([0xC0 | c, v["program"]]))]
            for s, n, p, vel in v["notes"]:
                on = s * self.tick
                off = min(end, on + max(self.tick // 4, int((n - 1 + v["gate"]) * self.tick)))
                ev.append((on, 2, bytes([0x90 | c, p, vel])))
                ev.append((off, 1, bytes([0x80 | c, p, 0])))
            ev.append((end, 9, b"\xff\x2f\x00"))
            tracks.append(track(ev))
        return b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), PPQ) + b"".join(tracks)


def rep(*parts):
    """rep('A A A B', 2, 'C', 4) -> the bars 'A A A B' twice, then 'C' four times."""
    out = []
    for text, times in zip(parts[::2], parts[1::2]):
        out += text.split() * times
    return out


# ---------------------------------------------------------------------------------------------------------------------

def hinges():
    """E, 104 a minute. The plain Doom rocker: bass and guitar in one riff, organ stabs, a tune on the guitar."""
    p = Piece("Off Its Hinges", 104)
    riff = "A1 A2 A1 A2"
    four = rep(riff, 2, "A1+5 A2+5 A1+5 A2+5", 1, riff, 1)                      # 16 bars: home, the 4th, home
    chorus = rep("C-4 C-2 C C", 2)                                               # 8 bars: flat 6th, flat 7th, home
    p.voice("bass", PICKBASS, 28, {
        "A1": "1 . 1 1 . 1 . 1 b3 . 1 . 4 . b3 .",
        "A2": "1 . 1 1 . 1 . 1 b3 . 1 . b5 4 b3 1",
        "C": "1 . 1 . 1 . 1 . 1 . 1 . 1 . 1 1",
    }, rep(riff, 2) + four + chorus + four + chorus, vel=104, gate=0.8, volume=115)
    p.voice("guitar", OVERDRIVE, 40, {
        "A1": "1^! . 1 1 . 1 . 1 b3^! . 1 . 4^! . b3^ .",
        "A2": "1^! . 1 1 . 1 . 1 b3^! . 1 . b5^ 4^ b3^ 1",
        "C": "1*! - - - - - 1* - - - - - 1* - 1* -",
    }, rep("_", 4, riff, 1) + four + chorus + four + chorus, vel=84, gate=0.75, volume=92, pan=50)
    p.voice("organ", ORGAN, 64, {
        "S": ". . . . 1m . . . . . . . 1m . 1m .",
        "SM": ". . . . 1M . . . . . . . 1M . 1M .",
    }, rep("_", 8, "S", 8, "S+5", 4, "S", 4, "SM-4 SM-2 S S", 2, "S", 8, "S+5", 4, "S", 4, "SM-4 SM-2 S S", 2),
            vel=66, gate=0.6, volume=78, pan=80)
    p.voice("lead", DISTORTION, 64, {
        "T1": "5 - - - - - 4 - b3 - - - - - 1 -",
        "T2": "2 - - - b3 - - - - - - - . . . .",
        "T3": "5 - - - - - b7 - 5 - - - - - 4 -",
        "T4": "b3 - - - 4 - - - 5 - - - - - - -",
        "T5": "1' - - - - - b7 - 5 - - - - - b7 -",
        "T6": "1' - - - - - - - - - - - . . . .",
        "T7": "b3' - - - 2' - 1' - b7 - - - 5 - - -",
        "T8": "b7 - - - 5 - - - 1' - - - - - - -",
        "K1": "1 - - - - - - - b3 - - - 1 - - -",
        "K2": "2 - - - - - - - 4 - - - 2 - - -",
        "K3": "5 - - - - - - - - - - - 4 - b3 -",
        "K4": "1 - - - - - - - - - - - . . . .",
        "K5": "1 - - - b3 - - - b6 - - - b3 - - -",
        "K6": "2 - - - 4 - - - b7 - - - 4 - - -",
        "K7": "1' - - - - - - - b7 - - - 5 - - -",
        "K8": "1' - - - - - - - - - - - - - - -",
    }, rep("_", 24, "K1 K2 K3 K4 K5 K6 K7 K8", 1, "T1 T2 T3 T4 T5 T6 T7 T8", 1, "_", 8, "K1 K2 K3 K4 K5 K6 K7 K8", 1),
            vel=92, gate=0.97, volume=96, reverb=60)
    p.drums({
        "h": {HAT: "x.x.x.x.x.x.x.x."},
        "a": {KICK: "x.xx...xx.x...x.", ESNARE: "....x.......x...", HAT: "X.x.X.x.X.x.X.x."},
        "f": {KICK: "x.xx...xx.x.....", ESNARE: "....x.......xx..", TOM2: "..............x.", TOM4: "...............x",
              HAT: "X.x.X.x.X.x....."},
        "c": {CRASH: "x...............", RIDE: "x.x.x.x.x.x.x.x.", KICK: "x.....x.x.x.....", ESNARE: "....x.......x..."},
        "r": {RIDE: "x.x.x.x.x.x.x.x.", KICK: "x.....x.x.x.....", ESNARE: "....x.......x..."},
    }, rep("h", 4, "a a a f", 5, "c r r f", 2, "a a a f", 4, "c r r f", 2))
    return p


def far_side():
    """F, 76 a minute. The creeping one: a synth bass in octaves, held organ, a lament on bells, a slow tune."""
    p = Piece("The Far Side", 76)
    p.voice("bass", SYNBASS, 29, {
        "P": "1 - . . 1' . . 1 - . . . b7, . 1 .",
        "Q": "1 - . . 1' . . 1 - . . . b3 . b2 .",
        "V": "1 - . . 1' . . 1 - . . . 5 . 1 .",
    }, rep("P P P Q", 1, "P P V-4 V-2 P Q V+5 Q-2", 4, "P P P Q", 1), vel=104, gate=0.9, volume=112)
    p.voice("organ", ORGAN, 53, {
        "m": "1m - - - - - - - - - - - - - - -",
        "M": "1M - - - - - - - - - - - - - - -",
    }, rep("_", 4, "m m M-4 M-2 m m m+5 M-2", 4, "_", 4), vel=58, gate=1.0, volume=74, pan=76)
    p.voice("bells", BELLS, 65, {
        "L1": "1' - - - - - - - b7 - - - - - - -",
        "L2": "5 - - - - - - - b3 - - - - - - -",
    }, rep("_", 12, "L1 L2 _ _ L1 L2 _ _", 1, "_", 8, "_ _ _ _ L1 L2 _ _", 1, "L1 L2 _ _", 1), vel=78, gate=1.0,
            volume=88, pan=48, reverb=70)
    p.voice("tune", POLYSYNTH, 65, {
        "M1": "5 - - - - - - - b3 - - - 4 - - -",
        "M2": "5 - - - - - - - - - - - . . . .",
        "M3": "b6 - - - - - - - 4 - - - b3 - - -",
        "M4": "b7 - - - - - - - 4 - - - 2 - - -",
        "M5": "1' - - - - - - - b7 - - - 5 - - -",
        "M6": "5 - - - - - - - b3 - - - . . . .",
        "M7": "4 - - - - - - - b6 - - - 1' - - -",
        "M8": "b7 - - - 2' - - - b7 - - - 5 - - -",
    }, rep("_", 20, "M1 M2 M3 M4 M5 M6 M7 M8", 2, "_", 4), vel=86, gate=0.97, volume=92, reverb=60)
    p.drums({
        "h": {HAT: "XoxoXoxoXoxoXoxo"},
        "a": {KICK: "x......x.x......", ESNARE: "....x.......x...", HAT: "XoxoXoxoXoxoXoxo"},
        "f": {KICK: "x......x.x.....x", ESNARE: "....x.......x.x.", HAT: "XoxoXoxoXoxo....", OHAT: "............x..."},
    }, rep("h", 4, "a a a f", 8, "h", 4), vel=92)
    return p


def seven():
    """D, in seven. The baroque one (Doom has them too): harpsichord, plucked strings, a cello; a bar a beat short."""
    p = Piece("One Door Short", 112, steps=14, sig=(7, 8))
    prog = "{0} {1}-4 {0}+5 {1}-5"                                              # home, flat 6th, the 4th, the 5th
    p.voice("harpsichord", HARPSI, 50, {
        "m": "1 . 5 . 1' . b3' . 5 . 1' . 5 .",
        "M": "1 . 5 . 1' . 3' . 5 . 1' . 5 .",
    }, rep(prog.format("m", "M"), 9, "_", 4, prog.format("m", "M"), 2), vel=84, gate=0.7, volume=96, pan=52)
    p.voice("bass", CONTRABASS, 38, {
        "B": "1 - - . 1 - - . 1 - . 1 - .",
    }, rep("_", 4, "B B-4 B+5 B-5", 11), vel=98, gate=0.9, volume=112)
    p.voice("pizzicato", PIZZ, 62, {
        "m": "5 . . . b3 . . . 1 . b3 . 5 .",
        "M": "5 . . . 3 . . . 1 . 3 . 5 .",
        "n": "5 . . 5 b3 . . . 1 . b3 5 1' .",
        "N": "5 . . 5 3 . . . 1 . 3 5 1' .",
    }, rep("_", 12, prog.format("m", "M"), 1, prog.format("n", "N"), 1, prog.format("m", "M"), 1,
           prog.format("n", "N"), 1, "_", 8, prog.format("n", "N"), 3), vel=74, gate=0.5, volume=90, pan=80)
    tune = {
        "C1": "5 - - - - - - - - - 4 - 5 -",
        "C2": "b6 - - - - - - - - - 4 - b6 -",
        "C3": "4 - - - - - - - b6 - - - 4 -",
        "C4": "5 - - - - - - - 7 - - - 2' -",
        "C5": "1' - - - - - - - - - b7 - 1' -",
        "C6": "1' - - - - - - - - - b6 - 4 -",
        "C7": "1' - - - - - - - b6 - - - 4 -",
        "C8": "2' - - - - - - - 7 - - - 5 -",
    }
    p.voice("cello", CELLO, 50, tune, rep("_", 20, "C1 C2 C3 C4 C5 C6 C7 C8", 2, "_", 4, "C1 C2 C3 C4 C5 C6 C7 C8", 1),
            vel=88, gate=1.0, volume=98, reverb=60)
    p.voice("strings", STRINGS, 62, tune, rep("_", 28, "C1 C2 C3 C4 C5 C6 C7 C8", 1, "_", 8, "C5 C6 C7 C8", 1),
            vel=70, gate=1.0, volume=80, pan=44, reverb=70)
    p.drums({
        "a": {KICK: "x.......x.....", ESNARE: "....x......x..", RIDE: "x.x.x.x.x.x.x."},
        "f": {KICK: "x.......x.....", ESNARE: "....x......x.x", TOM4: "............x.", RIDE: "x.x.x.x.x.x..."},
    }, rep("_", 4, "a a a f", 11), vel=88)
    return p


def clock():
    """A, a slow shuffle. The time piece: a woodblock ticks, a bell strikes; the third round is the blues backwards."""
    p = Piece("The Small Hours, Twice", 72, steps=12, per_beat=3, sig=(12, 8))

    def round_(a, b=None, c=None, d=None, major=None):
        """Twelve bars: home x4, the 4th x2, home x2, flat 6th, flat 7th, home x2."""
        b, c, d, major = b or a, c or a, d or (b or a), major or a
        return f"{a} {b} {c} {d} {a}+5 {b}+5 {c} {d} {major}-4 {major}-2 {c} {d}".split()

    def back(bars):
        return [re.sub(r"^(\w+?)([+-]\d+)?$", r"\1<\2", t) for t in reversed(bars)]

    p.voice("bass", FRETLESS, 33, {
        "R": "1 - . 1 . b3 4 - . b5 4 b3",
        "RM": "1 - . 1 . 3 5 - . 6 5 3",
    }, rep("_", 2) + round_("R", major="RM") * 2 + back(round_("R", major="RM")) + round_("R", major="RM") + rep("_", 2), vel=102, gate=0.9, volume=115)
    p.voice("guitar", MUTED, 57, {
        "G": ". . 5,q . . 5,q . . 5,q . . .",
        "H": ". . 5,q . . 5,q . . b7,q . . 5,q",
    }, rep("_", 2) + round_("G", "H") * 2 + back(round_("G", "H")) + round_("G", "H") + rep("_", 2),
            vel=74, gate=0.5, volume=88, pan=78)
    tune = round_("L1", "L2", "L3", "L4", major="LF")
    p.voice("tune", OVERDRIVE, 69, {
        "L1": "5 - - - - b7 - - 5 - - 4",
        "L2": "b3 - - - - 1 - - - . . .",
        "L3": "5 - - - - b7 - - 1' - - b7",
        "L4": "5 - - b5 - 4 b3 - - 1 - -",
        "LF": "5 - - 3 - - 1 - - 3 - -",
    }, rep("_", 14) + tune + back(tune) + tune + rep("_", 2), vel=90, gate=0.97, volume=94, pan=50, reverb=60)
    p.voice("bell", BELLS, 57, {
        "B": "1 - - - - - 5, - - - - -",
        "O": "1 - - - - - - - - - - -",
    }, rep("B B", 1, "_", 24, "O _ _ _", 3, "O _ _ _", 3, "B O", 1), vel=80, gate=1.0, volume=90, pan=40, reverb=80)
    p.drums({
        "t": {WOOD_HI: "x.....x.....", WOOD_LO: "...x.....x.."},
        "a": {WOOD_HI: "x.....x.....", WOOD_LO: "...x.....x..", HAT: "x.ox.ox.ox.o", KICK2: "x.....x....x",
              ESNARE: "...x.....x.."},
        "f": {WOOD_HI: "x.....x.....", WOOD_LO: "...x.....x..", HAT: "x.ox.ox.o...", KICK2: "x.....x.....",
              ESNARE: "...x.....xxx"},
        "b": {WOOD_LO: "x.....x.....", WOOD_HI: "...x.....x..", HAT: "x.ox.ox.ox.o", KICK2: "x.....x....x",
              ESNARE: "...x.....x.."},
        "g": {WOOD_LO: "x.....x.....", WOOD_HI: "...x.....x..", HAT: "x.ox.ox.o...", KICK2: "x.....x.....",
              ESNARE: "...x.....xxx"},
    }, rep("t", 2, "a a a f", 6, "b b b g", 3, "a a a f", 3, "t", 2), vel=90)
    return p


def after_hours():
    """C, 60 a minute. The quiet one: strings and a low drone, timpani far off, a few notes on a piano."""
    p = Piece("After Hours", 60)
    hold = " ".join("-" * 16)
    p.voice("strings", SLOWSTR, 48, {
        "m": "1m - - - - - - - - - - - - - - -", "M": "1M - - - - - - - - - - - - - - -", "T": hold,
    }, rep("m T M-4 T m T M+1 T", 4), vel=70, gate=1.0, volume=92, pan=54, reverb=80)
    p.voice("drone", CONTRABASS, 36, {
        "D": "1 - - - - - - - - - - - - - - -", "T": hold,
    }, rep("D T D-4 T D T D+1 T", 4), vel=84, gate=1.0, volume=104)
    p.voice("timpani", TIMPANI, 36, {
        "a": "1 . . . . . . . . . . . . . 1 1",
        "b": "1 . . . . . . . . . . . 1 . 1 1",
    }, rep("_", 8, "a _ a-4 _ a _ b+1 _", 3), vel=82, gate=0.9, volume=96, pan=72, reverb=70)
    p.voice("piano", PIANO, 60, {
        "Pa": ". . . . 5 - b6 - 5 - - - - - - -",
        "Pb": ". . . . b3 - 2 - 1 - - - - - - -",
        "Pc": ". . . . b3 - 4 - b3 - - - 1 - - -",
        "Pd": ". . . . b6 - 4 - b2 - - - - - - -",
    }, rep("_", 8, "Pa _ Pc _ Pb _ Pd _", 3), vel=78, gate=1.0, volume=96, pan=44, reverb=80)
    p.voice("choir", CHOIR, 60, {
        "a": "5 - - - - - - - - - - - - - - -", "b": "b3 - - - - - - - - - - - - - - -",
        "c": "4 - - - - - - - - - - - - - - -", "T": hold,
    }, rep("_", 16, "a T b T b T c T", 2), vel=62, gate=1.0, volume=80, pan=74, reverb=90)
    p.voice("harp", HARP, 60, {
        "H": "1 . . . 5 . . . 1' . . . 5 . . .",
    }, rep("_", 24, "H H H-4 H-4 H H H+1 H+1", 1), vel=66, gate=1.0, volume=84, pan=36, reverb=80)
    p.drums({
        "a": {KICK2: "x...............", RBELL: "........o......."},
        "b": {RBELL: "........o......."},
    }, rep("_", 8, "a b", 12), vel=84, volume=90)
    return p


def engine():
    """D, 138 a minute. The heavy one, Sigil's way: a guitar chugging on the low string, a brass tune over held fifths."""
    p = Piece("Paradox Engine", 138)
    riff = "X1 X1 X1 X2"
    p.voice("guitar", DISTORTION, 38, {
        "X1": "1! 1 b2' 1 1 b3' 1 1 b2' 1 1 4' 1 b3' 1 1",
        "X2": "1! 1 b2' 1 1 b3' 1 1 b5' 1 1 4' 1 b3' b2' 1",
        "H": "1*! - - - - - - - 1* - - - 1* - 1* -",
    }, rep(riff, 3, "X1+5 X1+5 X1+5 X2+5", 1, riff, 1, "H+8 H+10 H H", 2, riff, 2, "H+8 H+10 H H", 2, "_", 4,
           riff, 2, "H+8 H+10 H H", 2), vel=86, gate=0.8, volume=94, pan=50)
    p.voice("bass", PICKBASS, 26, {
        "p": "1 . 1 . 1 . 1 . 1 . 1 . 1 . 1 .",
        "q": "1 . 1 . 1 . 1 . 1 . 1 . 1 . b3 b2",
        "c": "1 . . 1 . . 1 . 1 . . 1 . . 1 1",
    }, rep("_", 4, "p p p q", 2, "p+5 p+5 p+5 q+5", 1, "p p p q", 1, "c+8 c+10 c c", 2, "p p p q", 2,
           "c+8 c+10 c c", 2, "p p p q", 3, "c+8 c+10 c c", 2), vel=106, gate=0.8, volume=115)
    p.voice("brass", SYNBRASS, 62, {
        "S1": "1' - - - - - - - b6 - - - 1' - - -",
        "S2": "2' - - - - - - - b7 - - - 2' - - -",
        "S3": "4' - - - b3' - - - 1' - - - - - b7 -",
        "S4": "1' - - - - - - - - - - - . . . .",
        "S5": "4' - - - - - - - 1' - - - 4' - - -",
        "S6": "5' - - - - - - - 2' - - - 5' - - -",
        "S7": "5' - - - 4' - - - b3' - - - 4' - 5' -",
        "S8": "1'' - - - - - - - - - - - - - - -",
    }, rep("_", 20, "S1 S2 S3 S4 S5 S6 S7 S8", 1, "_", 8, "S1 S2 S3 S4 S5 S6 S7 S8", 1, "_", 12,
           "S1 S2 S3 S4 S5 S6 S7 S8", 1), vel=90, gate=0.97, volume=96, pan=72, reverb=50)
    p.voice("strings", STRINGS, 50, {
        "m": "1m - - - - - - - - - - - - - - -", "M": "1M - - - - - - - - - - - - - - -",
    }, rep("_", 20, "M+8 M+10 m m", 2, "_", 8, "M+8 M+10 m m", 2, "_", 12, "M+8 M+10 m m", 2), vel=64, gate=1.0,
            volume=78, pan=40, reverb=60)
    p.voice("square", SQUARE, 74, {
        "Q1": "1 - - - - - b2 - 1 - - - b7, - - -",
        "Q2": "1 - - - - - - - . . . . 5, - b7, -",
        "Q3": "1 - - - - - b2 - b3 - - - b2 - - -",
        "Q4": "1 - - - - - - - - - - - . . . .",
        "Q5": "5 - - - - - b6 - 5 - - - 4 - - -",
        "Q6": "b3 - - - - - 4 - b3 - - - b2 - - -",
        "Q7": "1 - - - b2 - - - b3 - - - 4 - - -",
        "Q8": "1' - - - - - - - - - - - - - - -",
    }, rep("_", 28, "Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8", 1, "_", 12, "Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8", 1, "_", 8), vel=78, gate=0.97,
            volume=84, pan=64, reverb=50)
    p.drums({
        "h": {HAT: "x.x.x.x.x.x.x.x."},
        "a": {KICK: "x.xx..x.x.xx..x.", SNARE: "....x.......x...", OHAT: "x...x...x...x...", HAT: "..x...x...x...x."},
        "f": {KICK: "x.xx..x.x.......", SNARE: "....x.....x.xx..", TOM2: "..............x.", TOM4: "...............x",
              OHAT: "x...x...x......."},
        "c": {CRASH: "x...............", KICK: "x..x..x.x..x..x.", SNARE: "....x.......x...", RIDE: "x.x.x.x.x.x.x.x."},
        "r": {KICK: "x..x..x.x..x..x.", SNARE: "....x.......x...", RIDE: "x.x.x.x.x.x.x.x."},
    }, rep("h", 4, "a a a f", 4, "c r r f", 2, "a a a f", 2, "c r r f", 2, "a a a f", 3, "c r r f", 2), vel=98)
    return p


TRACKS = [
    ("AJM_HING", "the plain Doom rocker: bass and guitar in one riff, organ stabs", hinges),
    ("AJM_FARS", "the creeping one: synth bass in octaves, held organ, bells, a slow tune", far_side),
    ("AJM_SEVN", "the baroque one, a bar of seven: harpsichord, plucked strings, a cello", seven),
    ("AJM_CLOK", "the time maps: a slow shuffle, a clock ticks; the third round is the blues backwards", clock),
    ("AJM_AFTR", "the quiet one: strings, a low drone, timpani, a few piano notes", after_hours),
    ("AJM_ENGN", "the heavy one, Sigil's way: a chugging guitar, a brass tune over held fifths", engine),
]


def make_all():
    out, listing = {}, []
    for lump, what, make in TRACKS:
        piece = make()
        out[f"music/{lump}.mid"] = piece.midi()
        listing.append(f"{lump}|{piece.title}|{what}")
    out["ajmusic.txt"] = "\n".join(listing) + "\n"
    return out


if __name__ == "__main__":
    import os
    import sys
    files = make_all()
    for lump, what, make in TRACKS:
        piece = make()
        notes = sum(len(v["notes"]) for v in piece.voices)
        print(f"{lump}  {piece.title}: {piece.bars} bars of {piece.sig[0]}/{piece.sig[1]}, {piece.seconds():.0f} s at "
              f"{piece.bpm} a minute, {len(piece.voices)} voices, {notes} notes, {len(files[f'music/{lump}.mid'])} bytes")
        print(f"    {what}")
    if len(sys.argv) > 1:
        os.makedirs(sys.argv[1], exist_ok=True)
        for name, data in files.items():
            with open(os.path.join(sys.argv[1], os.path.basename(name)), "wb" if isinstance(data, bytes) else "w") as f:
                f.write(data)
        print("written to", sys.argv[1])
