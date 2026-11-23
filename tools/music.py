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

Vadim heard the first six in the sound lab on 2026-11-23 and took them all;
the other six are written the same way. Which map plays which piece is in
src/mapinfo.txt (the quiet one on MAP01 and MAP10 by his word, the rest by
how much fighting a map has). All twelve can be heard in the sound lab
(MAP=SOUND ./run.sh).

Six more quiet ones, 2026-11-23: Vadim asked for more like After Hours (the
piece of MAP01 and MAP10). They are the last six of TRACKS, written the way
that one is: held chords two bars long over a low note, a tune of a few long
notes coming in after eight bars, one more voice every eight bars, hardly any
drums, then round again from the bare beginning. No map plays them yet.
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
PIANO, EPIANO, HARPSI, VIBES, BELLS, ORGAN, MUTED, OVERDRIVE, DISTORTION = 0, 4, 6, 11, 14, 18, 28, 29, 30
ACBASS, FINGER, PICKBASS, FRETLESS, SYNBASS1, SYNBASS, CELLO, CONTRABASS, PIZZ, HARP, TIMPANI = 32, 33, 34, 35, 38, 39, 42, 43, 45, 46, 47
STRINGS, SLOWSTR, CHOIR, SYNBRASS, SQUARE, SAW, POLYSYNTH = 48, 49, 52, 62, 80, 81, 90
GLOCK, MUSICBOX, MARIMBA, CHURCH, TREMOLO, VOICE, HORN, CLARINET, FLUTE, WARMPAD = 9, 10, 12, 19, 44, 53, 60, 71, 73, 89
# percussion keys
KICK, KICK2, SNARE, ESNARE, HAT, OHAT, CRASH, RIDE, RBELL = 36, 35, 38, 40, 42, 46, 49, 51, 53
TOM1, TOM2, TOM3, TOM4, WOOD_HI, WOOD_LO, STICK = 48, 47, 45, 41, 76, 77, 37


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


def porter():
    """G, 96 a minute. The groove: a fingered bass riff, a muted guitar scratching, electric piano, vibes for the tune."""
    p = Piece("Night Porter", 96)
    unit = "N1 N1 N1 N2 N1 N1 N1 N2 N1+5 N2+5 N1 N2 N1-4 N1-2 N1 N2".split()   # 16 bars: home x8, 4th x2, home x2, b6, b7, home x2
    p.voice("bass", FINGER, 31, {
        "N1": "1 . . 1 . . b7, 1 . . b3 . 4 . b3 1",
        "N2": "1 . . 1 . . b7, 1 . . b3 . 4 b5 4 b3",
    }, rep("N1 N1 N1 N2", 1) + unit * 3 + rep("N1 N1 N1 N2", 1), vel=100, gate=0.8, volume=115)
    gt = "G G G H G G G H G+5 H+5 G H G-4 G-2 G H".split()
    p.voice("guitar", MUTED, 55, {
        "G": ". . 5,q . . 5,q . . . . 5,q . . . 5,q .",
        "H": ". . 5,q . . 5,q . . . . 5,q . b7,q . 5,q .",
    }, rep("_", 4) + gt * 3 + rep("_", 4), vel=72, gate=0.5, volume=88, pan=80)
    ep = "m m m m m m m m m+5 m+5 m m M-4 M-2 m m".split()
    p.voice("piano", EPIANO, 55, {
        "m": "1m - - . . . . . . . 1m - . . . .",
        "M": "1M - - . . . . . . . 1M - . . . .",
    }, rep("_", 12) + ep[8:] + ep * 2 + rep("_", 4), vel=66, gate=0.9, volume=84, pan=44)
    tune = "A1 A2 A3 A4 A5 A6 A7 A8 V1 V2 V3 V4 V5 V6 V7 V8".split()
    p.voice("vibes", VIBES, 67, {
        "A1": "5 - - - - - 4 - b3 - - - 1 - - -",
        "A2": "b3 - - - - - - - 1 - - - . . . .",
        "A3": "5 - - - - - b7 - 5 - - - 4 - - -",
        "A4": "5 - - - - - - - - - - - . . . .",
        "A5": "1' - - - - - b7 - 5 - - - b7 - - -",
        "A6": "1' - - - - - - - 5 - - - . . . .",
        "A7": "b3' - - - 1' - b7 - 5 - - - 4 - - -",
        "A8": "5 - - - - - - - - - - - . . . .",
        "V1": "1' - - - - - b6 - 4 - - - - - b6 -",
        "V2": "1' - - - - - - - b6 - - - 4 - - -",
        "V3": "5 - - - - - b3 - 5 - - - - - b7 -",
        "V4": "5 - - - - - - - - - - - . . . .",
        "V5": "b3 - - - - - 1 - b3 - - - b6 - - -",
        "V6": "4 - - - - - 2 - 4 - - - b7 - - -",
        "V7": "1' - - - - - b7 - 5 - - - b3 - - -",
        "V8": "1 - - - - - - - - - - - . . . .",
    }, rep("_", 12) + tune[8:] + tune + tune + rep("_", 4), vel=86, gate=1.0, volume=96, reverb=60)
    p.drums({
        "h": {HAT: "XoxoXoxoXoxoXoxo"},
        "a": {KICK: "x..x......xx....", ESNARE: "....x.......x...", HAT: "XoxoXoxoXoxoXoxo"},
        "f": {KICK: "x..x......x.....", ESNARE: "....x.......x.xx", HAT: "XoxoXoxoXoxo....", OHAT: "............x..."},
    }, rep("h", 4, "a a a f", 12, "h", 4), vel=92)
    return p


def fire_door():
    """A, 126 a minute. The fast rocker: a galloping riff, a chorus of held fifths under a guitar tune."""
    p = Piece("Fire Door", 126)
    riff = "F1 F1 F1 F2"
    verse = rep(riff, 2)
    fourth = rep("F1+5 F1+5 F1+5 F2+5", 1, riff, 1)
    chorus = rep("C C-2 C-4 C-2", 2)
    p.voice("guitar", DISTORTION, 45, {
        "F1": "1! . 1 1 b3^ . 1 1 4^ . 1 1 b3^ . b7,^ .",
        "F2": "1! . 1 1 b3^ . 1 1 4^ . 1 1 5^ . b5^ 4^",
        "C": "1*! - - 1* - - 1* - - - 1* - 1* - - -",
    }, rep(riff, 1) + verse + fourth + chorus + verse + chorus + rep("_", 4) + verse + chorus,
            vel=86, gate=0.8, volume=94, pan=50)
    p.voice("bass", PICKBASS, 33, {
        "F1": "1 . 1 1 b3 . 1 1 4 . 1 1 b3 . b7, .",
        "F2": "1 . 1 1 b3 . 1 1 4 . 1 1 5 . b5 4",
        "C": "1 . . 1 . . 1 . . . 1 . 1 . . .",
    }, rep("_", 4) + verse + fourth + chorus + verse + chorus + rep(riff, 1) + verse + chorus,
            vel=106, gate=0.8, volume=115)
    stabs, pads = rep("S", 8), "m M-2 M-4 M-2".split() * 2
    p.voice("organ", ORGAN, 57, {
        "S": ". . 1m . . . 1m . . . 1m . . . 1m .",
        "m": "1m - - - - - - - - - - - - - - -", "M": "1M - - - - - - - - - - - - - - -",
    }, rep("_", 12, "S+5", 4, "S", 4) + pads + stabs + pads + rep("_", 4) + stabs + pads,
            vel=62, gate=0.7, volume=76, pan=80)
    tune = "K1 K2 K3 K4 K5 K6 K7 K8"
    p.voice("lead", OVERDRIVE, 69, {
        "K1": "5 - - - - - - - 1' - - - b7 - - -",
        "K2": "4 - - - - - - - 2 - - - b7, - - -",
        "K3": "b3 - - - - - - - 1 - - - b6, - - -",
        "K4": "2 - - - - - - - 4 - - - 5 - - -",
        "K5": "1' - - - - - - - 5 - - - 1' - - -",
        "K6": "b7 - - - - - - - 4 - - - b7 - - -",
        "K7": "1' - - - - - - - b6 - - - 1' - - -",
        "K8": "2' - - - - - - - b7 - - - 2' - - -",
    }, rep("_", 20, tune, 1, "_", 8, tune, 1, "_", 12, tune, 1), vel=92, gate=0.97, volume=96, reverb=60)
    p.drums({
        "h": {HAT: "x.x.x.x.x.x.x.x."},
        "a": {KICK: "x.x...x.x.x...x.", SNARE: "....x.......x...", HAT: "X.x.X.x.X.x.X.x."},
        "f": {KICK: "x.x...x.x.......", SNARE: "....x.....x.xx..", TOM2: "..............x.", TOM4: "...............x",
              HAT: "X.x.X.x.X......."},
        "c": {CRASH: "x...............", KICK: "x..x..x...x.....", SNARE: "....x.......x...", RIDE: "x.x.x.x.x.x.x.x."},
        "r": {KICK: "x..x..x...x.....", SNARE: "....x.......x...", RIDE: "x.x.x.x.x.x.x.x."},
    }, rep("h", 4, "a a a f", 4, "c r r f", 2, "a a a f", 2, "c r r f", 2, "a a a f", 3, "c r r f", 2), vel=98)
    return p


def service_lift():
    """E, a heavy shuffle, 96 a minute. Twelve bars round and round: bass and guitar in the riff, organ, a guitar tune."""
    p = Piece("Service Lift", 96, steps=12, per_beat=3, sig=(12, 8))

    def round_(a, b, major=None):
        major = major or a
        return f"{a} {a} {a} {b} {a}+5 {a}+5 {a} {b} {major}-2 {major}-4 {a} {b}".split()

    p.voice("bass", PICKBASS, 28, {
        "S1": "1 . 1 1 . 1 b3 . 1 4 . b3",
        "S2": "1 . 1 1 . 1 b3 . 1 b7, . 7,",
    }, rep("S1 S1 S1 S2", 1) + round_("S1", "S2") * 4, vel=104, gate=0.8, volume=115)
    p.voice("guitar", OVERDRIVE, 40, {
        "S1": "1^! . 1 1^ . 1 b3^ . 1 4^ . b3",
        "S2": "1^! . 1 1^ . 1 b3^ . 1 b7,^ . 7,",
    }, rep("_", 4) + round_("S1", "S2") * 4, vel=84, gate=0.75, volume=92, pan=50)
    p.voice("organ", ORGAN, 64, {
        "m": ". . 1m . . . . . 1m . . .",
        "M": ". . 1M . . . . . 1M . . .",
    }, rep("_", 16) + round_("m", "m", major="M") * 3, vel=64, gate=0.7, volume=78, pan=80)
    tune = "W1 W2 W3 W4 W5 W6 W1 W8 W9 W10 W11 W12".split()
    p.voice("lead", DISTORTION, 64, {
        "W1": "5 - - - - 4 b3 - - 1 - -",
        "W2": "b3 - - 4 - - 5 - - - - -",
        "W3": "b7 - - - - 5 b7 - - 1' - -",
        "W4": "b7 - - 5 - - 4 - - b3 - .",
        "W5": "1' - - - - b6 4 - - b6 - -",
        "W6": "1' - - b7 - - b6 - - 4 - -",
        "W8": "b3 - - 1 - - - - - . . .",
        "W9": "4 - - 2 - - b7, - - 2 - -",
        "W10": "b3 - - 1 - - b6, - - 1 - -",
        "W11": "5 - - b7 - - 1' - - b7 - -",
        "W12": "1' - - - - - - - - . . .",
    }, rep("_", 16) + tune + rep("_", 12) + tune, vel=92, gate=0.97, volume=96, reverb=60)
    p.drums({
        "h": {HAT: "x.xx.xx.xx.x"},
        "a": {KICK: "x....xx....x", ESNARE: "...x.....x..", HAT: "X.xX.xX.xX.x"},
        "f": {KICK: "x....xx.....", ESNARE: "...x.....xxx", HAT: "X.xX.xX.x..."},
    }, rep("h", 4, "a a a f", 12), vel=96)
    return p


def filing():
    """C, 132 a minute. The machine: a synth bass in sixteenths, a saw riff, pads, a square-wave tune."""
    p = Piece("Filing Under Fire", 132)
    p.voice("bass", SYNBASS1, 36, {
        "Y1": "1 1 1 1' 1 1 1' 1 1 1 1' 1 1 1' 1 1",
        "Y2": "1 1 1 1' 1 1 1' 1 1 1 1' 1 b3 b3 b7, b7,",
        "Y3": "1 1 1 1' 1 1 1' 1 1 1 1' 1 3 3 2 2",
    }, rep("Y1 Y1 Y1 Y2", 1, "Y1 Y1 Y1 Y2 Y1-4 Y1-4 Y1-2 Y3-2", 7), vel=100, gate=0.6, volume=110)
    saw = "Z1 Z2 Z1 Z2 ZM-4 ZM-4 ZM-2 ZM-2"
    p.voice("saw", SAW, 48, {
        "Z1": "1 . b3 . 4 . b3 . 1 . b7, . 1 . . .",
        "Z2": "1 . b3 . 4 . b5 . 4 . b3 . 1 . . .",
        "ZM": "1 . 3 . 5 . 3 . 1 . 5, . 1 . . .",
    }, rep("_", 4, saw, 3, "_", 8, saw, 3), vel=88, gate=0.8, volume=90, pan=48)
    p.voice("pad", STRINGS, 60, {
        "m": "1m - - - - - - - - - - - - - - -", "M": "1M - - - - - - - - - - - - - - -", "T": " ".join("-" * 16),
    }, rep("_", 12, "m T m T M-4 T M-2 T", 6), vel=62, gate=1.0, volume=78, pan=78, reverb=70)
    p.voice("tune", SQUARE, 72, {
        "U1": "5 - - - - - - - b3 - - - - - - -",
        "U2": "4 - - - - - - - 5 - - - - - - -",
        "U3": "b7 - - - - - - - 5 - - - - - - -",
        "U4": "1' - - - - - - - - - - - . . . .",
        "U5": "1' - - - - - - - b6 - - - - - - -",
        "U6": "b3 - - - - - - - 1 - - - b3 - - -",
        "U7": "2' - - - - - - - b7 - - - - - - -",
        "U8": "4 - - - - - - - 2 - - - 4 - 5 -",
    }, rep("_", 20, "U1 U2 U3 U4 U5 U6 U7 U8", 2, "_", 8, "U1 U2 U3 U4 U5 U6 U7 U8", 2), vel=80, gate=0.97, volume=86,
            reverb=50)
    p.drums({
        "h": {HAT: "XoxoXoxoXoxoXoxo"},
        "a": {KICK: "x...x...x...x...", SNARE: "....x.......x...", HAT: "xo.oxo.oxo.oxo.o", OHAT: "..x...x...x...x."},
        "f": {KICK: "x...x...x...x...", SNARE: "....x.......x.xx", HAT: "xo.oxo.oxo.o....", OHAT: "..x...x...x....."},
        "b": {KICK: "x...x...x...x...", HAT: "XoxoXoxoXoxoXoxo"},
    }, rep("h", 4, "a a a f", 6, "b b b f", 2, "a a a f", 6), vel=96)
    return p


def carbon_copy():
    """B, 100 a minute. The canon: plucked strings and a woodblock; the tune's copy follows four bars behind, lower."""
    p = Piece("Carbon Copy", 100)
    p.voice("pizzicato", PIZZ, 59, {
        "m": "1 . 5 . b3' . 5 . 1 . 5 . b3' . 5 .",
        "M": "1 . 5 . 3' . 5 . 1 . 5 . 3' . 5 .",
    }, rep("m M-4 m M-2", 13), vel=76, gate=0.5, volume=92, pan=48)
    p.voice("bass", ACBASS, 35, {
        "B": "1 - - . . . 1 . 5 - - . . . 1 .",
    }, rep("_", 4, "B B-4 B B-2", 12), vel=98, gate=0.9, volume=112)
    tune = {
        "P1": "5 - - - - - - - b3 - - - 4 - - -",
        "P2": "b3 - - - - - - - 1 - - - - - - -",
        "P3": "5 - - - - - - - b7 - - - 5 - - -",
        "P4": "4 - - - - - - - 2 - - - - - - -",
        "P5": "1' - - - - - - - b7 - - - 5 - - -",
        "P6": "b6 - - - - - - - b3 - - - - - - -",
        "P7": "b3 - - - - - 4 - 5 - - - - - - -",
        "P8": "4 - - - 2 - - - b7, - - - - - - -",
    }
    whole, half = "P1 P2 P3 P4 P5 P6 P7 P8", "P1 P2 P3 P4"
    p.voice("tune", STRINGS, 71, tune, rep("_", 8, whole, 3, "_", 4, whole, 2), vel=84, gate=1.0, volume=94, pan=40,
            reverb=70)
    p.voice("copy", CELLO, 59, tune, rep("_", 12, whole, 2, half, 1, "_", 8, whole, 1, half, 1), vel=86, gate=1.0,
            volume=96, pan=84, reverb=60)
    p.drums({
        "t": {WOOD_HI: "x.......x.......", WOOD_LO: "....x.......x..."},
        "a": {WOOD_HI: "x.......x.......", WOOD_LO: "....x.......x...", KICK2: "x.........x.....", HAT: "..o...o...o...o."},
        "f": {WOOD_HI: "x.......x.......", WOOD_LO: "....x.......x.xx", KICK2: "x.........x.....", HAT: "..o...o...o....."},
    }, rep("t", 8, "a a a f", 7, "t", 4, "a a a f", 3), vel=88)
    return p


def dead_letter():
    """E, 66 a minute. The slow heavy one: a guitar riff on the tritone, timpani, a choir, a bell."""
    p = Piece("Dead Letter Office", 66)
    riff = "D1 D2 D1 D3"
    p.voice("guitar", DISTORTION, 40, {
        "D1": "1^! - - - - - . . b5 - - - 4^ - - -",
        "D2": "1^! - - - - - . . b3^ - - - b2^ - - -",
        "D3": "1^! - - - - - . . b6^ - - - b7^ - - -",
    }, rep(riff, 7, "_", 4, riff, 2), vel=88, gate=0.95, volume=96, pan=50)
    p.voice("bass", PICKBASS, 28, {
        "D1": "1 - - - - - 1 . b5 - - - 4 - - -",
        "D2": "1 - - - - - 1 . b3 - - - b2 - - -",
        "D3": "1 - - - - - 1 . b6 - - - b7 - - -",
    }, rep("_", 4, riff, 9), vel=104, gate=0.9, volume=115)
    p.voice("timpani", TIMPANI, 40, {
        "a": "1 . . . . . 1 1 . . . . . . . .",
    }, rep("_", 4, "a", 36), vel=84, gate=0.9, volume=96, pan=74, reverb=70)
    p.voice("choir", CHOIR, 64, {
        "C1": "1 - - - - - - - - - - - - - - -",
        "C2": "1 - - - - - - - b3 - - - - - - -",
        "C3": "1 - - - - - - - b3 - - - 4 - - -",
    }, rep("_", 12, "C1 C2 C1 C3", 7), vel=64, gate=1.0, volume=84, pan=76, reverb=90)
    p.voice("bell", BELLS, 64, {
        "B": "1' - - - - - - - - - - - - - - -",
    }, rep("B _ _ _", 10), vel=80, gate=1.0, volume=90, pan=36, reverb=80)
    p.voice("lead", OVERDRIVE, 64, {
        "X1": "5 - - - - - - - b5 - - - 4 - - -",
        "X2": "b3 - - - - - 1 - b3 - - - b2 - - -",
        "X3": "5 - - - - - b7 - b5 - - - 4 - - -",
        "X4": "1' - - - - - - - b6 - - - b7 - - -",
    }, rep("_", 20, "X1 X2 X3 X4", 2, "_", 4, "X1 X2 X3 X4", 2), vel=92, gate=0.97, volume=96, reverb=70)
    p.drums({
        "a": {KICK: "x.....xx........", ESNARE: "........x.......", RIDE: "x...x...x...x..."},
        "c": {CRASH: "x...............", KICK: "x.....xx........", ESNARE: "........x.......", RIDE: "x...x...x...x..."},
        "f": {KICK: "x.....xx........", ESNARE: "........x.......", RIDE: "x...x...x.......", TOM1: "............x...",
              TOM2: ".............x..", TOM3: "..............x.", TOM4: "...............x"},
    }, rep("_", 4, "c a a f", 6, "_", 4, "c a a f", 2), vel=98)
    return p


# The quiet ones after After Hours (see the top). In each the chords are named in its first comment; a tune's bar
# is written against the chord of that bar, so a tune is not moved with the chords unless its form says so.

def do_not_disturb():
    """A, 56 a minute. The lullaby: a music box over strings that sink a third and come back, a voice a semitone apart."""
    p = Piece("Do Not Disturb", 56)
    hold = " ".join("-" * 16)
    # two bars each: A minor, F minor, A minor, E major
    p.voice("strings", SLOWSTR, 57, {
        "m": "1m - - - - - - - - - - - - - - -", "M": "1M - - - - - - - - - - - - - - -", "T": hold,
    }, rep("m T m-4 T m T M-5 T", 4), vel=68, gate=1.0, volume=90, pan=54, reverb=80)
    p.voice("drone", CONTRABASS, 33, {
        "D": "1 - - - - - - - - - - - - - - -", "T": hold,
    }, rep("D T D-4 T D T D-5 T", 4), vel=82, gate=1.0, volume=102)
    p.voice("music box", MUSICBOX, 69, {
        "Ba": ". . . . 5 - b3' - 2' - 1' - - - - -",
        "Bb": ". . . . b3' - 7 - b6 - - - - - - -",
        "Bc": ". . . . 5 - 1' - b3' - 5' - - - - -",
        "Bd": ". . . . 5' - 4' - 2' - 7 - - - - -",
        "Be": ". . . . 1' - 2' - b3' - - - 5 - - -",
        "Bf": ". . . . b3' - b6 - 7 - - - - - - -",
        "Bg": ". . . . b3' - 1' - 5 - - - - - - -",
        "Bh": ". . . . 2' - 7 - 5 - - - - - - -",
    }, rep("_", 8, "Ba _ Bb _ Bc _ Bd _", 1, "Be _ Bf _ Bg _ Bh _", 1, "Ba _ Bb _ Bc _ Bd _", 1), vel=80, gate=1.0,
            volume=96, pan=44, reverb=80)
    p.voice("voice", VOICE, 69, {                       # A, A flat, A, G sharp: the one note the chords do not share
        "a": "1 - - - - - - - - - - - - - - -", "b": "7, - - - - - - - - - - - - - - -", "T": hold,
    }, rep("_", 16, "a T b T a T b T", 2), vel=60, gate=1.0, volume=80, pan=74, reverb=90)
    p.voice("harp", HARP, 57, {
        "H": "1 . . . 5 . . . b3' . . . 5 . . .",
        "HM": "1 . . . 5 . . . 3' . . . 5 . . .",
    }, rep("_", 24, "H H H-4 H-4 H H HM-5 HM-5", 1), vel=64, gate=1.0, volume=84, pan=36, reverb=80)
    p.drums({
        "a": {KICK2: "x..o............"},                 # a heart, slow
    }, rep("_", 8, "a", 24), vel=78, volume=86)
    return p


def left_luggage():
    """D, 66 a minute. The empty hall: a fretless bass riff with room in it, electric piano, a tune on the vibraphone."""
    p = Piece("Left Luggage", 66)
    # eight bars: D minor x4, G major x2, D minor x2; the middle: B flat, C, D minor x2, twice
    intro = rep("L1 L1 L1 L2", 1)
    unit = "L1 L1 L1 L2 L1+5 L1+5 L1 L2".split()
    middle = "L1-4 L1-2 L1 L2".split() * 2
    p.voice("bass", FRETLESS, 38, {
        "L1": "1 - - . . . 1 . 5, - - . . . b7, .",
        "L2": "1 - - . . . 1 . 4 - - . b3 . 2 .",
    }, intro + unit * 2 + middle + unit + intro, vel=98, gate=0.9, volume=112)
    chords, mid = "c c c c C-7 C-7 c c".split(), "C-4 C-2 c c".split() * 2
    p.voice("piano", EPIANO, 62, {
        "c": "1m - - - - - - - - - - - . . . .",
        "C": "1M - - - - - - - - - - - . . . .",
    }, rep("_", 4) + chords * 2 + mid + chords + rep("_", 4), vel=62, gate=1.0, volume=82, pan=44, reverb=60)
    p.voice("strings", SLOWSTR, 50, {
        "m": "1m - - - - - - - - - - - - - - -", "M": "1M - - - - - - - - - - - - - - -",
    }, rep("_", 20, "M-4 M-2 m m", 2, "_", 12), vel=60, gate=1.0, volume=76, pan=78, reverb=80)
    tune = "A1 A2 A3 A4 A5 A6 A7 A8".split()
    p.voice("vibes", VIBES, 74, {
        "A1": "5 - - - - - - - 4 - - - b3 - - -",
        "A2": "1 - - - - - - - - - - - . . . .",
        "A3": "5 - - - - - - - b7 - - - 5 - - -",
        "A4": "4 - - - - - - - - - - - . . . .",
        "A5": "6 - - - - - - - 5 - - - 4 - - -",
        "A6": "2 - - - - - - - - - - - . . . .",
        "A7": "b3 - - - - - - - 1 - - - b7, - - -",
        "A8": "1 - - - - - - - - - - - . . . .",
        "B1": "b3 - - - - - - - 1 - - - b3 - - -",
        "B2": "4 - - - - - - - 2 - - - 4 - - -",
        "B3": "5 - - - - - - - - - - - 4 - b3 -",
        "B4": "1 - - - - - - - - - - - . . . .",
        "B5": "1' - - - - - - - b6 - - - 4 - - -",
        "B6": "b7 - - - - - - - 4 - - - 2 - - -",
        "B7": "b3 - - - - - - - 4 - - - 5 - - -",
        "B8": "1' - - - - - - - - - - - - - - -",
    }, rep("_", 12) + tune + "B1 B2 B3 B4 B5 B6 B7 B8".split() + tune + rep("_", 4), vel=82, gate=1.0, volume=94,
            reverb=70)
    p.drums({
        "t": {RIDE: "o...o...o...o..."},
        "a": {RIDE: "o...o...o...o...", KICK2: "x.......o.......", STICK: "....o.......o..."},
        "f": {RIDE: "o...o...o...o...", KICK2: "x.......o.......", STICK: "....o.......o.o."},
    }, rep("t", 4, "a a a f", 8, "t", 4), vel=84, volume=90)
    return p


def light_under_the_door():
    """E, 58 a minute. The watch kept: a harp going round, strings trembling on one note, a horn far off, then a flute."""
    p = Piece("Light Under the Door", 58)
    hold = " ".join("-" * 16)
    # two bars each: E minor, F major, E minor, D minor (the white keys from E)
    p.voice("harp", HARP, 52, {
        "m": "1 . 5 . 1' . b3' . 5' . b3' . 1' . 5 .",
        "M": "1 . 5 . 1' . 3' . 5' . 3' . 1' . 5 .",
    }, rep("m m M+1 M+1 m m m-2 m-2", 4), vel=70, gate=1.0, volume=92, pan=44, reverb=70)
    p.voice("drone", CONTRABASS, 40, {
        "D": "1 - - - - - - - - - - - - - - -", "T": hold,
    }, rep("D T D+1 T D T D-2 T", 4), vel=82, gate=1.0, volume=100)
    p.voice("tremolo", TREMOLO, 64, {                   # B, C, B, A
        "a": "5 - - - - - - - - - - - - - - -", "b": "b6 - - - - - - - - - - - - - - -",
        "c": "4 - - - - - - - - - - - - - - -", "T": hold,
    }, rep("_", 8, "a T b T a T c T", 3), vel=58, gate=1.0, volume=76, pan=76, reverb=80)
    tune = {
        "H1": "5 - - - - - - - - - - - 1' - - -",
        "H2": "b3' - - - - - - - 1' - - - 5 - - -",
        "H3": "4 - - - - - - - - - - - b6 - - -",
        "H4": "b2' - - - - - - - b6 - - - 4 - - -",
        "H5": "5 - - - - - - - 1' - - - b3' - - -",
        "H6": "5' - - - - - - - - - - - . . . .",
        "H7": "4' - - - - - - - b2' - - - b7 - - -",
        "H8": "4 - - - - - - - - - - - . . . .",
    }
    whole = "H1 H2 H3 H4 H5 H6 H7 H8"
    p.voice("horn", HORN, 52, tune, rep("_", 8, whole, 1, "_", 8, whole, 1), vel=80, gate=0.97, volume=92, pan=58,
            reverb=90)
    p.voice("flute", FLUTE, 64, tune, rep("_", 16, whole, 2), vel=70, gate=0.97, volume=82, pan=40, reverb=80)
    p.voice("timpani", TIMPANI, 40, {
        "a": "1 . . . . . . . . . . . . . 1 1",
    }, rep("_", 16, "a _ _ _ a _ _ _", 2), vel=78, gate=0.9, volume=92, pan=72, reverb=70)
    return p


def between_floors():
    """F sharp, in five, 72 a minute. The lift that stopped: five piano notes round and round, a cello, a held chord."""
    p = Piece("Between Floors", 72, steps=20, sig=(5, 4))
    hold = " ".join("-" * 20)
    # two bars each: F sharp minor, B minor, D major, G major; the piano's lowest note stays until the last
    round_ = "Oi Oi Oiv Oiv OVI OVI OII OII"
    p.voice("piano", PIANO, 66, {
        "Oi": "1 - - . 5 - - . b3 - - . 5 - - . b3 - - .",
        "Oiv": "1 - - . b6 - - . 4 - - . b6 - - . 4 - - .",
        "OVI": "1 - - . b6 - - . b3 - - . b6 - - . b3 - - .",
        "OII": "b2 - - . b6 - - . 4 - - . b6 - - . 4 - - .",
    }, rep(round_, 4), vel=72, gate=1.0, volume=94, pan=46, reverb=80)
    p.voice("bass", ACBASS, 42, {
        "B": "1 - - - - - - - - - - . 5, - - - - - - .",
    }, rep("_", 4, "B-4 B-4 B+1 B+1", 1, "B B B+5 B+5 B-4 B-4 B+1 B+1", 3), vel=92, gate=0.9, volume=108)
    p.voice("pad", WARMPAD, 54, {
        "m": "1m - - - - - - - - - - - - - - - - - - -", "M": "1M - - - - - - - - - - - - - - - - - - -", "T": hold,
    }, rep("_", 8, "m T m+5 T M-4 T M+1 T", 3), vel=58, gate=1.0, volume=74, pan=76, reverb=80)
    p.voice("cello", CELLO, 54, {
        "T1": "5 - - - - - - - - - - - b3 - - - 1 - - -",
        "T2": "b3 - - - - - - - - - - - - - - - . . . .",
        "T3": "b6 - - - - - - - - - - - 4 - - - 1 - - -",
        "T4": "4 - - - - - - - - - - - - - - - . . . .",
        "T5": "1' - - - - - - - - - - - b6 - - - b3 - - -",
        "T6": "b6 - - - - - - - - - - - - - - - . . . .",
        "T7": "b2' - - - - - - - - - - - b6 - - - 4 - - -",
        "T8": "b2 - - - - - - - - - - - - - - - . . . .",
    }, rep("_", 8, "T1 T2 T3 T4 T5 T6 T7 T8", 2, "_", 8), vel=86, gate=1.0, volume=98, reverb=70)
    p.voice("choir", CHOIR, 66, {                       # C sharp, then D for the three chords that have it
        "a": "5 - - - - - - - - - - - - - - - - - - -", "b": "b6 - - - - - - - - - - - - - - - - - - -", "T": hold,
    }, rep("_", 16, "a T b T T T T T", 2), vel=58, gate=1.0, volume=76, pan=30, reverb=90)
    p.drums({
        "a": {KICK2: "x...................", RBELL: "............o......."},     # three and two
    }, rep("_", 4, "a", 28), vel=80, volume=88)
    return p


def night_bell():
    """C sharp, 60 a minute. The desk at night: a slow minor blues on an organ, a bell tolling, a small bell nobody
    answers, a cello."""
    p = Piece("Night Bell", 60)
    hold = " ".join("-" * 16)
    # twelve bars: C sharp minor x4, F sharp minor x2, C sharp minor x2, A major, G sharp major, C sharp minor x2
    p.voice("organ", CHURCH, 49, {
        "m": "1m - - - - - - - - - - - - - - -", "M": "1M - - - - - - - - - - - - - - -", "T": hold,
    }, rep("m T T T m+5 T m T M-4 M-5 m T", 3), vel=56, gate=1.0, volume=72, pan=58, reverb=80)
    p.voice("bass", ACBASS, 37, {
        "P": "1 - - - - - - . 5, - - - - - - .",
        "Q": "1 - - - - - - . 5 - - - - - - .",
    }, rep("P P P P P+5 P+5 P P Q-4 Q-5 P P", 3), vel=92, gate=0.9, volume=108)
    p.voice("bell", BELLS, 61, {
        "B": "1 - - - - - - - - - - - - - - -",
    }, rep("B _ _ _", 9), vel=78, gate=1.0, volume=88, pan=36, reverb=90)
    p.voice("desk bell", GLOCK, 85, {
        "d": ". . . . . . . . . . . . 5 - - -",
    }, rep("_ _ _ d", 9), vel=70, gate=1.0, volume=80, pan=84, reverb=70)
    tune = {
        "N1": "5 - - - - - - - b7 - - - 5 - - -",
        "N2": "4 - - - b3 - - - 1 - - - - - - -",
        "N3": "5 - - - - - - - b7 - - - 1' - - -",
        "N4": "b7 - - - 5 - - - - - - - . . . .",
        "N5": "b6 - - - - - - - 1' - - - b6 - - -",
        "N6": "4 - - - b6 - - - 4 - - - - - - -",
        "N7": "5 - - - - - - - 4 - - - b3 - - -",
        "N8": "1 - - - - - - - - - - - . . . .",
        "N9": "b3' - - - - - - - 1' - - - b6 - - -",
        "N10": "2' - - - - - - - 7 - - - 5 - - -",
        "N11": "b3 - - - 4 - - - 5 - - - - - - -",
        "N12": "1 - - - - - - - - - - - . . . .",
    }
    whole = "N1 N2 N3 N4 N5 N6 N7 N8 N9 N10 N11 N12"
    p.voice("cello", CELLO, 49, tune, rep("_", 12, whole, 2), vel=86, gate=1.0, volume=98, pan=50, reverb=70)
    p.voice("strings", STRINGS, 61, tune, rep("_", 24, whole, 1), vel=62, gate=1.0, volume=76, pan=74, reverb=80)
    p.voice("timpani", TIMPANI, 37, {
        "a": "1 . . . . . . . . . . . . . 1 1",
    }, rep("_", 24, "a _ _ _ a+5 _ a _ _ _ a _", 1), vel=76, gate=0.9, volume=90, pan=72, reverb=70)
    p.drums({
        "a": {KICK2: "x...............", RIDE: "....o.......o..."},
    }, rep("_", 12, "a", 24), vel=82, volume=88)
    return p


def standing_water():
    """B flat, 52 a minute. The flooded floor: every chord a step lower than the last, drips on a marimba, a clarinet."""
    p = Piece("Standing Water", 52)
    hold = " ".join("-" * 16)
    # two bars each: B flat minor, A flat minor, G flat minor, F major; all the voices sink with the chords
    p.voice("strings", SLOWSTR, 58, {
        "m": "1m - - - - - - - - - - - - - - -", "M": "1M - - - - - - - - - - - - - - -", "T": hold,
    }, rep("m T m-2 T m-4 T M-5 T", 4), vel=66, gate=1.0, volume=88, pan=56, reverb=80)
    p.voice("drone", CONTRABASS, 34, {
        "D": "1 - - - - - - - - - - - - - - -", "T": hold,
    }, rep("D T D-2 T D-4 T D-5 T", 4), vel=82, gate=1.0, volume=102)
    p.voice("drips", MARIMBA, 70, {
        "da": ". . . 1' . . . . . . 5 . . . . .",
        "db": ". . . . . . b3' . . . . . . 1' . 5",
        "dB": ". . . . . . 3' . . . . . . 1' . 5",
    }, rep("da db da-2 db-2 da-4 db-4 da-5 dB-5", 4), vel=70, gate=1.0, volume=88, pan=34, reverb=90)
    p.voice("clarinet", CLARINET, 58, {
        "S1": "5 - - - - - - - - - - - b3 - - -",
        "S2": "1 - - - - - - - - - - - . . . .",
        "S7": "2 - - - - - - - - - - - 7, - - -",
        "S8": "5, - - - - - - - - - - - . . . .",
        "T1": "1 - - - b3 - - - 5 - - - - - - -",
        "T2": "b7 - - - - - - - 5 - - - . . . .",
        "T7": "5, - - - 7, - - - 2 - - - - - - -",
        "T8": "4 - - - - - - - 2 - - - . . . .",
    }, rep("_", 8, "S1 S2 S1-2 S2-2 S1-4 S2-4 S7 S8", 1, "T1 T2 T1-2 T2-2 T1-4 T2-4 T7 T8", 1,
           "S1 S2 S1-2 S2-2 S1-4 S2-4 S7 S8", 1), vel=80, gate=0.97, volume=94, pan=60, reverb=80)
    p.voice("voice", VOICE, 70, {                       # the fifth of each chord
        "a": "5 - - - - - - - - - - - - - - -", "T": hold,
    }, rep("_", 16, "a T a-2 T a-4 T a-5 T", 2), vel=56, gate=1.0, volume=74, pan=78, reverb=90)
    p.voice("harp", HARP, 46, {
        "H": "1 . . . 5 . . . 1' . . . 5 . . .",
    }, rep("_", 24, "H H H-2 H-2 H-4 H-4 H-5 H-5", 1), vel=62, gate=1.0, volume=82, pan=44, reverb=80)
    return p


TRACKS = [
    ("AJM_HING", "the plain Doom rocker: bass and guitar in one riff, organ stabs", hinges),
    ("AJM_FARS", "the creeping one: synth bass in octaves, held organ, bells, a slow tune", far_side),
    ("AJM_SEVN", "the baroque one, a bar of seven: harpsichord, plucked strings, a cello", seven),
    ("AJM_CLOK", "the time maps: a slow shuffle, a clock ticks; the third round is the blues backwards", clock),
    ("AJM_AFTR", "the quiet one: strings, a low drone, timpani, a few piano notes", after_hours),
    ("AJM_ENGN", "the heavy one, Sigil's way: a chugging guitar, a brass tune over held fifths", engine),
    ("AJM_PORT", "the groove: a fingered bass riff, muted guitar, electric piano, vibes", porter),
    ("AJM_FIRE", "the fast rocker: a galloping riff, a guitar tune over held fifths", fire_door),
    ("AJM_LIFT", "the heavy shuffle: twelve bars round and round, organ, a guitar tune", service_lift),
    ("AJM_FILE", "the machine: synth bass in sixteenths, a saw riff, a square-wave tune", filing),
    ("AJM_COPY", "the canon: plucked strings, a woodblock; the tune's copy four bars behind", carbon_copy),
    ("AJM_DEAD", "the slow heavy one: a riff on the tritone, timpani, a choir, a bell", dead_letter),
    ("AJM_DSTB", "quiet, the lullaby: a music box over strings that sink a third, a voice a semitone apart", do_not_disturb),
    ("AJM_LUGG", "quiet, the empty hall: a fretless bass riff, electric piano, a vibraphone tune", left_luggage),
    ("AJM_LGHT", "quiet, the watch kept: a harp going round, trembling strings, a horn, then a flute", light_under_the_door),
    ("AJM_FLRS", "quiet, in five: five piano notes round and round, a cello, a held chord", between_floors),
    ("AJM_BELL", "quiet, a slow minor blues: an organ, a bell tolling, a desk bell nobody answers, a cello", night_bell),
    ("AJM_WATR", "quiet, the flooded floor: every chord a step lower, drips on a marimba, a clarinet", standing_water),
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
