"""Ajar's music, written as notes and turned into MIDI files by this script.

Nothing is recorded: a piece is a tune written out bar by bar, a line of
chords and an accompaniment pattern, the way the maps are rooms written out
as rectangles. GZDoom plays the files as it plays Doom's own music.

One figure runs through every piece: the doorbell, two notes a third apart,
the higher first ("ding, dong"). Because the pieces are notes, the music can
do what the maps do: mirrored() turns a piece upside down (the lobby's major
becomes minor), rewound() plays it from its last note to its first.

    python3 tools/music.py DIR    writes the .mid files to DIR and prints
                                  what each piece is and a check of its notes
    music.make_all()              what tools/build.py puts into the package:
                                  music/<LUMP>.mid and the list ajmusic.txt
                                  (LUMP|Title|what it is for), read by the
                                  sound lab (src/zscript/soundlab.zs)

The trial set (2026-11-23), to judge this way of making music by ear in the
sound lab (MAP=SOUND ./run.sh). No map plays any of it yet.
"""
import random
import re
import struct

PPQ = 480                       # MIDI ticks to a beat
STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
KINDS = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10), "maj7": (0, 4, 7, 11),
         "6": (0, 4, 7, 9), "m6": (0, 3, 7, 9), "dim": (0, 3, 6), "sus4": (0, 5, 7)}

# General MIDI instruments (program numbers) and percussion keys used here
PIANO, CELESTA, GLOCK, MUSICBOX, VIBES, BELLS = 0, 8, 9, 10, 11, 14
BASS, PIZZ, STRINGS, BASSOON, CLARINET = 32, 45, 48, 70, 71
STICK, WOOD_HI, WOOD_LO, TRIANGLE = 37, 76, 77, 81
DRUMS = 9                       # the percussion channel


def pitch(name):
    """'C#5' -> 73 (C4 is 60, middle C)."""
    m = re.fullmatch(r"([A-G])([#b]?)(-?\d)", name)
    if not m:
        raise ValueError(f"not a note: {name}")
    return STEP[m[1]] + {"#": 1, "b": -1, "": 0}[m[2]] + 12 * (int(m[3]) + 1)


def chord(name):
    """'Bbm7' -> (bass pitch class, intervals above it)."""
    m = re.fullmatch(r"([A-G])([#b]?)(.*)", name)
    if not m or m[3] not in KINDS:
        raise ValueError(f"not a chord: {name}")
    return (STEP[m[1]] + {"#": 1, "b": -1, "": 0}[m[2]]) % 12, KINDS[m[3]]


def tones(ch):
    return {(ch[0] + i) % 12 for i in ch[1]}


class Piece:
    """A piece: beats to the bar, speed, and voices. A voice is a channel
    with an instrument and its notes (start, length in beats, pitch, loudness)."""

    def __init__(self, title, meter, bpm, seed=1):
        self.title, self.meter, self.bpm = title, meter, bpm
        self.bars = 0
        self.voices = []
        self.rng = random.Random(seed)
        self.report = []            # melody notes that fall on a beat and are not of the bar's chord
        self.checked = 0

    def voice(self, program, volume=100, pan=64, reverb=40, drums=False):
        used = {v["channel"] for v in self.voices}
        channel = DRUMS if drums else next(c for c in range(16) if c != DRUMS and c not in used)
        v = dict(channel=channel, program=program, volume=volume, pan=pan, reverb=reverb, notes=[])
        self.voices.append(v)
        return v

    def note(self, v, start, length, p, vel, hold=0.92):
        vel = max(1, min(127, vel + self.rng.randint(-4, 4)))
        v["notes"].append((start, length, p, vel, hold))
        self.bars = max(self.bars, int(-(-(start + length) // self.meter)))

    def tune(self, v, bar, text, vel=84, shift=0, chords=None, hold=0.92, late=0):
        """A tune from `bar` on: 'E5/2 C5/1 | r/3 | ...', a note and its length
        in beats, bars parted by '|'. `late` delays it by beats (a canon's
        second voice); `chords`, the same bars' chords, has its notes checked."""
        for i, one in enumerate(text.split("|")):
            at = 0.0
            for tok in one.split():
                name, _, n = tok.partition("/")
                n = float(n)
                if name != "r":
                    p = pitch(name) + shift
                    self.note(v, (bar + i) * self.meter + at + late, n, p, vel + (6 if at == 0 else 0), hold)
                    if chords and at == int(at):
                        here = chords[i][min(int(at * len(chords[i]) / self.meter), len(chords[i]) - 1)]
                        self.checked += 1
                        if p % 12 not in tones(here):
                            self.report.append(f"bar {bar + i + 1} beat {int(at) + 1}: {name}")
                at += n
            if abs(at - self.meter) > 1e-9:
                raise ValueError(f"{self.title}: bar {i + 1} of '{text[:24]}...' has {at} beats, not {self.meter}")

    # -- accompaniments: each takes the first bar and a list of bars, a bar being a list of chords --

    def low(self, pc, floor=33):
        return floor + (pc - floor) % 12            # the bass note: the lowest one from `floor` (A1) up

    def close(self, ch, floor=55):
        return sorted(floor + (pc - floor) % 12 for pc in tones(ch))    # the chord within an octave from `floor` (G3)

    def waltz(self, bass, keys, bar, chords, vel=50):
        """Oom-pah-pah: the bass on one, the chord on two and three."""
        last = None
        for i, cs in enumerate(chords):
            ch = cs[0]
            t = (bar + i) * self.meter
            fifth = ch == last and 7 in ch[1]
            self.note(bass, t, 1, self.low((ch[0] + 7) % 12 if fifth else ch[0]), vel + 18, 0.9)
            for b in (1, 2):
                for p in self.close(ch):
                    self.note(keys, t + b, 1, p, vel - (4 if b == 2 else 0), 0.55)
            last = None if fifth else ch

    def march(self, bass, keys, bar, chords, vel=52):
        """In four: the bass on one and three, the chord plucked on two and four."""
        for i, cs in enumerate(chords):
            t = (bar + i) * self.meter
            for half in (0, 1):
                ch = cs[min(half, len(cs) - 1)]
                second = half == 1 and len(cs) == 1 and 7 in ch[1]
                self.note(bass, t + 2 * half, 1, self.low((ch[0] + 7) % 12 if second else ch[0]), vel + 16, 0.6)
                for p in self.close(ch, 50):
                    self.note(keys, t + 2 * half + 1, 1, p, vel - 6, 0.35)

    def pendulum(self, bass, pad, bar, chords, vel=44):
        """The bass swings between the chord's root and its fifth; the strings hold the chord."""
        for i, cs in enumerate(chords):
            ch = cs[0]
            t = (bar + i) * self.meter
            self.note(bass, t, 2, self.low(ch[0]), vel + 14, 0.9)
            self.note(bass, t + 2, 2, self.low((ch[0] + 7) % 12) if 7 in ch[1] else self.low(ch[0]), vel + 6, 0.9)
            for p in self.close(ch):
                self.note(pad, t, self.meter, p, vel - 8, 1.0)

    def hits(self, v, bar, count, pattern, vel=46):
        """Percussion: pattern is (beat, key, louder-by) for one bar, repeated."""
        for i in range(count):
            for beat, key, more in pattern:
                self.note(v, (bar + i) * self.meter + beat, 0.25, key, vel + more, 1.0)

    # -- the file --

    def midi(self):
        end = self.bars * self.meter * PPQ
        tempo = round(60000000 / self.bpm)
        first = [(0, 0, b"\xff\x03" + _vlq(len(self.title)) + self.title.encode("ascii")),
                 (0, 0, b"\xff\x51\x03" + struct.pack(">I", tempo)[1:]),
                 (0, 0, bytes([0xFF, 0x58, 4, self.meter, 2, 24, 8]))]
        tracks = [_track(first, end)]
        for v in self.voices:
            c = v["channel"]
            ev = [(0, 0, bytes([0xB0 | c, 7, v["volume"]])), (0, 0, bytes([0xB0 | c, 10, v["pan"]])),
                  (0, 0, bytes([0xB0 | c, 91, v["reverb"]])), (0, 0, bytes([0xB0 | c, 93, 0]))]
            if c != DRUMS:
                ev.append((0, 0, bytes([0xC0 | c, v["program"]])))
            for start, length, p, vel, hold in v["notes"]:
                on = round(start * PPQ)
                off = min(end, max(on + 1, round((start + length * hold) * PPQ)))
                ev.append((on, 2, bytes([0x90 | c, p, vel])))
                ev.append((off, 1, bytes([0x80 | c, p, 64])))       # a note ends before another begins on the same tick
            tracks.append(_track(ev, end))
        return b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), PPQ) + b"".join(tracks)

    def seconds(self):
        return self.bars * self.meter * 60 / self.bpm

    def faults(self):
        """What would be wrong in the file: notes out of range or outside the
        piece, the same key struck again on a channel while it still sounds."""
        out = []
        end = self.bars * self.meter
        for v in self.voices:
            ringing = {}
            for start, length, p, vel, hold in sorted(v["notes"]):
                if not 0 <= p <= 127 or start < 0 or start >= end:
                    out.append(f"channel {v['channel']}: note {p} at beat {start}")
                if v["channel"] != DRUMS and ringing.get(p, 0) > start + 1e-6:
                    out.append(f"channel {v['channel']}: note {p} struck again at beat {start} while sounding")
                ringing[p] = start + length * hold
        return out


def _vlq(n):
    out = [n & 0x7F]
    while n > 0x7F:
        n >>= 7
        out.append(0x80 | (n & 0x7F))
    return bytes(reversed(out))


def _track(events, end):
    data, now = b"", 0
    for tick, _, msg in sorted(events, key=lambda e: e[:2]):
        data += _vlq(tick - now) + msg
        now = tick
    data += _vlq(end - now) + b"\xff\x2f\x00"       # every track ends on the piece's last bar line: the loop is exact
    return b"MTrk" + struct.pack(">I", len(data)) + data


def bars(text):
    """'C | Am | Gm6 A7' -> a list of bars, each a list of chords."""
    return [[chord(c) for c in one.split()] for one in text.split("|")]


def rewound(piece, title):
    """The piece from its last note to its first: a note begins as long before
    the end as it ended after the beginning, and keeps its length. A stroke of
    percussion has no length: it falls as long before the end as it fell after
    the beginning (one on a bar line stays on a bar line)."""
    back = Piece(title, piece.meter, piece.bpm)
    back.bars = piece.bars
    end = piece.bars * piece.meter
    for v in piece.voices:
        w = dict(v, notes=[((end - start) % end if v["channel"] == DRUMS else end - (start + length), length, p, vel, hold)
                           for start, length, p, vel, hold in v["notes"]])
        back.voices.append(w)
    return back


def upside_down(p, axis):
    """A note mirrored about a D (`axis`): the white keys fall on white keys,
    E on C, G on A, so a major chord comes out minor."""
    return 2 * axis - p


def mirror_chord(ch):
    pcs = sorted((4 - pc) % 12 for pc in tones(ch))
    fifth = (ch[0] + (7 if 7 in ch[1] else ch[1][2])) % 12
    bass = (4 - fifth) % 12                         # the old fifth becomes the new root
    return bass, tuple(sorted((pc - bass) % 12 for pc in pcs))


# ---------------------------------------------------------------------------------------------------------------
# The pieces
# ---------------------------------------------------------------------------------------------------------------

def lobby(mirror=False):
    """The hotel (MAP01-MAP10): a slow waltz in C. The doorbell (E, C) opens
    every phrase; the middle part goes to A minor. Twice through: vibraphone,
    then clarinet with the bell answering. Mirrored, the same piece upside
    down: C major becomes A minor and the bell rings dong, ding."""
    p = Piece("The Lobby, mirrored" if mirror else "The Lobby", 3, 104, seed=11)
    bell = p.voice(CELESTA, 96, 84, 60)
    vib = p.voice(VIBES, 100, 54, 50)
    reed = p.voice(CLARINET, 92, 70, 45)
    keys = p.voice(PIANO, 80, 44, 40)
    bass = p.voice(BASS, 96, 64, 20)

    a1 = "E5/2 C5/1 | G4/2 r/1 | E5/2 C5/1 | A4/2 r/1 | F5/1 E5/1 D5/1 | B4/2 D5/1 | C5/3 | r/3"
    a1c = "C | C | Am | Am | Dm | G7 | C | G7"
    a2 = "E5/2 C5/1 | G5/2 E5/1 | A5/2 F5/1 | E5/2 D5/1 | C5/1 D5/1 E5/1 | F5/2 A4/1 | B4/1 C5/1 D5/1 | C5/3"
    a2c = "C | C | F | G | Am | Dm | G7 | C"
    b = "A4/1 C5/1 E5/1 | G#4/2 B4/1 | A4/1 C5/1 E5/1 | D5/2 B4/1 | A4/2 C5/1 | G4/2 E5/1 | F#4/1 A4/1 C5/1 | B4/2 D5/1"
    bc = "Am | E7 | Am | E7 | F | C | D7 | G7"
    ring = "E6/2 C6/1 | r/3"
    answer = "r/3 | r/3 | r/3 | r/3 | r/3 | r/3 | r/3 | D6/2 B5/1"       # the bell on the dominant, in the tune's last bar

    def turn(text, axis):
        if not mirror:
            return text
        names = "C C# D D# E F F# G G# A A# B".split()
        out = []
        for tok in text.split():
            name, sep, n = tok.partition("/")
            if sep and name != "r":
                q = upside_down(pitch(name), axis)
                tok = f"{names[q % 12]}{q // 12 - 1}/{n}"
            out.append(tok)
        return " ".join(out)

    def harmony(text):
        return [[mirror_chord(c) for c in one] for one in bars(text)] if mirror else bars(text)

    D5, D6 = pitch("D5"), pitch("D6")
    p.tune(bell, 0, turn(ring, D6), 80)                 # the bell alone, then again over the first oom-pah-pah
    p.tune(bell, 2, turn(ring, D6), 72)
    p.waltz(bass, keys, 2, harmony("C | C"))
    at = 4
    for time in (0, 1):
        for text, ch in ((a1, a1c), (a2, a2c), (b, bc), (a2, a2c)):
            h = harmony(ch)
            lead = vib if time == 0 or text is b else reed
            p.tune(lead, at, turn(text, D5), 82 if lead is vib else 76, chords=h, hold=0.96 if lead is reed else 0.92)
            if time == 1 and text is a1:
                p.tune(bell, at, turn(answer, D6), 64)
            if time == 1 and text is a2:
                p.tune(vib, at, turn(text, D5), 44, shift=12)       # the vibraphone, far above, shadows the clarinet
            p.waltz(bass, keys, at, h)
            at += 8
    return p


def institute():
    """The Institute (MAP11-MAP16): office hours in D minor. The doorbell has
    shrunk to a minor third (F, D) on a bassoon over plucked strings; a rim
    click types and a triangle rings at the end of each line, as a typewriter
    does. The middle part, on a clarinet, looks out of the window in F."""
    p = Piece("The Institute", 4, 92, seed=12)
    low = p.voice(BASSOON, 100, 58, 35)
    reed = p.voice(CLARINET, 90, 72, 45)
    glock = p.voice(GLOCK, 70, 84, 55)
    keys = p.voice(PIZZ, 92, 50, 30)
    bass = p.voice(PIZZ, 104, 64, 20)
    drum = p.voice(0, 84, drums=True, reverb=25)

    a = ("F4/1.5 D4/.5 r/1 A3/1 | D4/.5 E4/.5 F4/1 D4/1 r/1 | G4/1.5 D4/.5 r/1 Bb3/1 | A3/.5 C#4/.5 E4/1 A3/1 r/1 | "
         "F4/1.5 D4/.5 r/1 A4/1 | Bb4/1 A4/.5 G4/.5 F4/1 D4/1 | E4/1 G4/1 C#4/1 E4/1 | D4/2 r/2")
    ac = "Dm | Dm | Gm | A7 | Dm | Bb | Gm6 A7 | Dm"
    b = ("A4/1 C5/1 F4/2 | G4/1 Bb4/1 E4/2 | A4/1 C5/1 F5/1 C5/1 | C#5/2 A4/2 | "
         "D5/1.5 A4/.5 F4/1 D4/1 | G4/1 Bb4/1 D5/2 | C#5/1 E5/1 A4/2 | r/1 A3/1 C#4/1 E4/1")
    bc = "F | C7 | F | A7 | Dm | Gm | A7 | A7"
    figure = "F6/1.5 D6/.5 r/2 | r/4 | G6/1.5 D6/.5 r/2 | r/4 | F6/1.5 D6/.5 r/2 | r/4 | r/4 | r/4"   # the bell, far above

    typing = [(1.5, STICK, 0), (3, STICK, 6), (3.5, STICK, -8)]
    p.march(bass, keys, 0, bars("Dm | Dm"))
    p.hits(drum, 1, 1, typing)
    at = 2
    for n, (text, ch) in enumerate(((a, ac), (a, ac), (b, bc), (a, ac), (a, ac), (b, bc), (a, ac))):
        h = bars(ch)
        p.tune(reed if text is b else low, at, text, 78 if text is b else 84, chords=h, hold=0.86)
        if text is a and n >= 3:
            p.tune(glock, at, figure, 58)
        p.march(bass, keys, at, h)
        p.hits(drum, at, 8, typing)
        p.note(drum, (at + 7) * 4 + 2, 0.25, TRIANGLE, 62, 1.0)         # the end of the line
        at += 8
    return p


def clock():
    """The Clock Department (MAP18 and the time maps): a clock ticks twice a
    second under a music box in E minor whose tune is the doorbell stepping
    down through the chords. The second time a vibraphone plays the same tune
    two bars behind: an earlier self, doing what you did. A bell strikes the
    doorbell (B, G) where each round ends."""
    p = Piece("The Clock Department", 4, 120, seed=13)
    box = p.voice(MUSICBOX, 100, 76, 60)
    self2 = p.voice(VIBES, 84, 48, 55)
    hour = p.voice(BELLS, 78, 64, 70)
    pad = p.voice(STRINGS, 60, 64, 60)
    bass = p.voice(BASS, 90, 64, 20)
    tick = p.voice(0, 70, drums=True, reverb=15)

    m = ("B5/2 G5/2 | E5/3 r/1 | B5/2 G5/2 | E5/2 C5/2 | A5/2 E5/2 | C5/3 r/1 | A5/2 F#5/2 | D5/2 A4/2 | "
         "B5/1 A5/1 G5/2 | D5/3 r/1 | F#5/2 D5/2 | B4/3 r/1 | E5/1 D5/1 C5/2 | A4/2 C5/2 | B4/2 G4/2 | E4/3 r/1")
    mc = "Em | Em | Cmaj7 | Cmaj7 | Am | Am | D | D | G | G | Bm | Bm | Am | Am | Em | Em"
    half = " | ".join(m.split(" | ")[8:])
    strike = "B3/2 G3/2"
    h = bars(mc)

    p.hits(tick, 0, 52, [(0, WOOD_HI, 6), (1, WOOD_LO, -4), (2, WOOD_HI, 0), (3, WOOD_LO, -6)])
    p.pendulum(bass, pad, 2, bars("Em | Em"))
    p.tune(hour, 2, strike, 70, hold=1.0)
    for n in range(3):
        at = 4 + 16 * n
        p.pendulum(bass, pad, at, h)
        p.tune(hour, at + 15, strike, 62, hold=1.0)
    p.tune(box, 4, m, 80, chords=h)
    p.tune(box, 20, m, 80)
    p.tune(self2, 20, m, 60, shift=-12, late=8)                 # the same tune, two bars late; it ends in the third round
    p.tune(box, 44, half, 80)                                   # the third round: the box waits, then ends the tune
    return p


TRACKS = [
    # lump, what it is for, how it is made
    ("AJM_LOBB", "the hotel, MAP01 to MAP10: a slow waltz on the doorbell", lambda: lobby()),
    ("AJM_LOBM", "a mirror map: the same waltz upside down, major turned minor", lambda: lobby(mirror=True)),
    ("AJM_INST", "the Institute, MAP11 to MAP16: office hours, a bassoon over plucked strings", institute),
    ("AJM_CLOK", "the time maps: a clock ticks; the tune's earlier self joins two bars late", clock),
    ("AJM_CLKR", "a replay: the clock piece from its last note to its first", lambda: rewound(clock(), "The Clock Department, rewound")),
]


def make_all():
    out, listing = {}, []
    for lump, what, make in TRACKS:
        piece = make()
        wrong = piece.faults()
        if wrong:
            raise SystemExit(f"music: {piece.title}: {wrong[0]} ({len(wrong)} faults)")
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
        data = files[f"music/{lump}.mid"]
        notes = sum(len(v["notes"]) for v in piece.voices)
        print(f"{lump}  {piece.title}: {piece.bars} bars of {piece.meter}, {piece.seconds():.0f} s at {piece.bpm} a minute, "
              f"{len(piece.voices)} voices, {notes} notes, {len(data)} bytes")
        print(f"    {what}")
        if piece.checked:
            print(f"    tune notes on a beat that are not of the bar's chord: {len(piece.report)} of {piece.checked}"
                  + (": " + "; ".join(piece.report) if piece.report else ""))
    if len(sys.argv) > 1:
        os.makedirs(sys.argv[1], exist_ok=True)
        for name, data in files.items():
            with open(os.path.join(sys.argv[1], os.path.basename(name)), "wb" if isinstance(data, bytes) else "w") as f:
                f.write(data)
        print("written to", sys.argv[1])
