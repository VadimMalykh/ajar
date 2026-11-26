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
    ^ * q m M a                    with its fifth; fifth and octave; fourth; minor triad; major triad; augmented
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
drums, then round again from the bare beginning. Vadim heard them in the
lab on 2026-11-24 and gave three their maps: Do Not Disturb MAP11, Light
Under the Door MAP19, Standing Water MAP33; the other three play nowhere yet.

The children's games, 2026-11-25: Vadim asked for something in the mood of
the theme of the series Squid Game, "but still our Doom style (as previous
melodies)", then for several of the sort, from still to active, to choose
from. They are the last five of TRACKS. No note of the series' music is in
them. None plays on a map until Vadim has chosen.

The first five put the playground INSIDE a Doom piece (a recorder somewhere
over minor riffs and guitars) and Vadim could not hear the mood in them. What
that theme is, by its composer's account: instruments of a primary school
(recorders, castanets), a tune made on the cheering clap everybody knows
(three, three, seven), played by children not quite in tune and not quite
together, and nothing under it. It is bright and bare, and uneasy because it
is innocent. So three were written anew the same day, the other way round
(Ready or Not, Knock Down Ginger, Salt Mustard Vinegar Pepper): the school
band first and alone, then the class (`bend` puts a voice out of tune,
`loose` lets its notes come late; a second row of drums claps not quite
together), and the Doom band comes in under them as the thing that is wrong.

He also found that all the pieces move through much the same chords. True:
nearly all are in minor and go between home, the 4th, the flat 6th and the
flat 7th, which is the rule read out of Doom's own music (see the top), and
the quiet ones hold two-bar chords with one foreign chord among them. The
three new ones try other ways: three minor chords a major third apart, round
and round (Ready or Not); two chords only, minor home and the MAJOR fourth,
with a chorus walking by fourths to home in major (Knock Down Ginger); a
tune in major over a bass going down by semitones, then the same in minor
(Salt, Mustard, Vinegar, Pepper). Ready or Not he did not take ("16 - no") and
it is removed.

Two ambient ones, the same day: he asked for "2 more slow, ambient-like
ones with experimental chord progressions". They came after the children's
games in TRACKS and are not games: no beat, held sounds, a few notes. In both the
chords are not written as blocks moved about but as three lines, each
holding its note until it has to move (a bar of dashes ties over), so what
is heard at a change is the one or two notes that move. Everything Else
Moves: one note, E, stays through six chords and exactly one other note
moves at each change (A minor, C, E minor, E, C sharp minor, A, and round).
Revolving Door was four major chords a minor third apart; Vadim: "19 is very
good actually, 20 - no", so Everything Else Moves stays and Revolving Door is
removed. What he took is the way of the first: one line at a time, by a
step. The pieces after it are made that way.

Four from Vadim's own chords, the same day: he put two sketches in his
Downloads, distant_galaxy_theme.mid (29 notes) and garmonic.mid (31), and
asked for two slow ambient versions "on harmonic ideas" from each. Of each
pair the first sets his chords as he voiced them and the second takes the
idea further.
- distant_galaxy_theme: eight chords of two bars, A minor, G sharp minor
  (the same chord slipped a semitone down), A with no third, D minor, C over
  E, E minor, F, then E with a C still in it (augmented) becoming E major.
  Distant Galaxy I was that, in held chords as he voiced them; Vadim: "20 -
  no", and it is removed. Distant Galaxy II is in D and does the slip
  twice, on the first chord and on the fourth, each time coming back to a
  chord with no third, and keeps his ending; slow harp notes, not held chords.
  He then asked for "couple more variations on Distant Galaxy": III is his
  eight chords as a rocking figure in twelve with a tune that only climbs
  (it has I's place in TRACKS, so the numbers of the others in the lab
  stay; removed too, "delete 20"); IV, now in III's place, is his eight
  chords with no two lines moving at once, made as Garmonic I is, of which he said "22 - yes yes
  yes!!!!!".
- garmonic: a B flat held on top while the two notes under it slip down a
  semitone one after the other (E flat minor becomes B flat); E flat minor
  to D major with the F sharp kept; D augmented; G minor; and G minor back
  to E flat minor with the B flat kept. Garmonic I is that, bar for bar.
  Garmonic II makes a chain of his first move: a minor chord's two lower
  notes slip and it is the major chord a fifth up; that chord's third
  drops, and it goes again: E flat minor, B flat, B flat minor, F, F minor,
  C, C minor, G, G minor, and his last move closes the ring. Every note
  only ever falls by a semitone, the chords climb by fifths, and after
  three times round all three lines are an octave lower.

Two on the harmony of Morten Lauridsen's O Magnum Mysterium, the same day
("check O Magnum Mysterium theme and create couple slow versions on that
harmonic ideas"): Mysterium I and II. What is taken and what is not stands
above the function. Vadim: "24 - no": Mysterium I (sixteen chords in D, a
line that stayed on D, a clarinet) is removed; II stays.

Two fast ones on his two sketches, the same day ("23 is also pretty good.
Could you as an experiment try 2 faster versions based on Distant Galaxy and
Garmony, in Doom style?"): Distant Galaxy, Fast and Garmonic, Fast, one of
each. The Doom rules above (a one-bar riff in fours, the guitar an octave
over the bass, blocks of four and eight, the drums on the grid), and the
sketch's harmony as what the riff does:
- Distant Galaxy, Fast: each of his first four chords is a group of four
  bars of one riff: on A, the same riff a semitone lower (in metal a riff
  moved whole is the usual thing, so here his slip is at home), on A with
  no third, on D. Over it one held note to a group, E, D sharp, E, F: his
  top line. His other four chords are the chorus: held fifths, C over an E
  bass, E minor, F, and E with the tune's C over it falling to B.
- Garmonic, Fast: his held B flat is a muted guitar on one note, all
  through. Under it the riff has three notes, and from bar to bar one of
  them slips: E flat, G flat, B flat; E flat, F, B flat; D, F, B flat. The
  second half is his other chords the same way, the kept note now F sharp:
  E flat minor over F sharp, D, D augmented, G minor, E flat minor.

Removed on Vadim's word the same day: The Small Hours Twice (AJM_CLOK),
Service Lift (AJM_LIFT), Filing Under Fire (AJM_FILE), Carbon Copy
(AJM_COPY). They are in git before 2026-11-25. So "the first six" and "the
other six" above are four and four now.

And The Far Side (AJM_FARS, the creeping one, the second of TRACKS), later
the same day: "delete 2". Garmonic, Fast was moved from the end to its
place, so that every other piece keeps the number Vadim knows it by in the
sound lab; that is the only reason it stands among the first ones.

And Distant Galaxy III (AJM_GAL3, the twentieth), the same evening:
"delete 20". Distant Galaxy IV was moved from the end to its place, as
above, so it is 20 in the lab now and the others keep their numbers.

On Paradox Engine, 2026-11-26. Vadim: "Could you make 2 new variations of
theme 5? One fast, but different arragement, and another one slow? Using
same melodic idea?" (5 in the lab is Paradox Engine). Two were written with
its riff and both its tunes note for note: a Toccata (a harpsichord had the
riff, a church organ and a guitar the tunes) and a Slow one (the riff
ticking on a muted guitar at a quarter of its speed, a clarinet and a horn).
"Both - no", and they are removed. Then: "Could you maybe generate 5 fast
and 5 slow? So I have something to choose from? Main melodic idea should be
the same, with some variations, also different instruments, rhytms, etc".

What Paradox Engine is made of, which is what "the main melodic idea" is
taken to be: the riff (a low key note hammered in sixteenths, out of which
the flat 2nd, flat 3rd, flat 2nd, 4th, flat 3rd stand: E flat, F, E flat, G,
F in D; a flat 5th in every fourth bar); the tune that goes over the riff
(the square wave's); the tune of the chorus over the flat 6th, the flat 7th
and home (the brass's). The two tunes stand below as patterns
(ENGINE_OVER_RIFF, ENGINE_CHORUS), with a second way of playing each (the
long notes walked through) and both cut for a bar of twelve.

Ten were written, five fast and five slow, each with the riff's notes and
both tunes in their order and the rhythm, the metre, the key and the
instruments changed. Vadim: "Delete 26, 28, 31, 32": the Gallop, in Seven,
Heavy (the three nearest to Paradox Engine's own distorted guitar) and
Still (ambient, three lines moving one at a time) are removed. Six stay,
and none plays on a map until he says so. So that the three he did not
name keep their numbers (27, 29, 30), the last three were moved into the
empty places, as before:
- 26 Piano (D, 63): the riff in the left hand at a quarter speed, the tunes
  in the right; a cello later. (It was 35.)
- 27 Shuffle (D, 12/8): the riff in triplets; a rock organ has the verse
  tune.
- 28 Night Shift (E, 12/8 at 60): the riff a fretless bass line four bars
  long; vibraphone, a muted trumpet. (It was 34.)
- 29 Machine (C, 140): the riff shared between a synth bass (the hammered
  note) and a square wave (the hidden notes), four on the floor; a guitar
  joins in the second chorus.
- 30 Upside Down (A, 138): the hammered note on top, a muted guitar on one
  note all through; the hidden notes a heavy riff under it.
- 31 Music Box (G, 3/4): a slow waltz with the riff as its accompaniment.
  (It was 33.)

With that he asked: "Also can you create by 5 versions combining melodic
ideas from Paradox Engine with harmonic ideas from Distang Galaxy, Garmony
and Mysterium?" Fifteen, five on each harmony, after the six in TRACKS (32
to 46). How the Engine's riff and tunes are laid on each harmony stands
above each set, further down. The fifteen, each made in the manner of a
piece he kept or put on a map:
- 32 to 36, Galaxy Engine: Band (A, 132), Machine (G, 140), Shuffle (D, 12/8
  at 132), Piano (A, 63), Night Shift (E, 12/8 at 60).
- 37 to 41, Garmonic Engine: Upside Down (E flat, 132), Groove (E, 100),
  Music Box (F, 3/4 at 92), Pizzicato (E flat, 92; strings alone), Slow
  (E flat, 54; ambient, the tunes over it from the first bar).
- 42 to 46, Mysterium Engine: Choir (B flat, 52), Piano (B flat, 66), Music
  Box (C, 3/4 at 96), Stream (G, 12/8 at 76; a harp in triplets), Band
  (B flat, 132; the one fast one, the Doom band in major).
"""
import random
import re
import struct

PPQ = 480
DEG = {"1": 0, "b2": 1, "2": 2, "b3": 3, "3": 4, "4": 5, "b5": 6, "5": 7, "b6": 8, "6": 9, "b7": 10, "7": 11}
SHAPE = {"": (0,), "^": (0, 7), "*": (0, 7, 12), "q": (0, 5), "m": (0, 3, 7), "M": (0, 4, 7), "a": (0, 4, 8)}
TOKEN = re.compile(r"(b?[1-7])([',]*)([\^*qmMa]?)(!?)")
BAR = re.compile(r"([A-Za-z]\w*?)(<?)([+-]\d+)?")
DRUMS = 9

# General MIDI programs
PIANO, EPIANO, HARPSI, CELESTA, VIBES, BELLS, ORGAN, MUTED, OVERDRIVE, DISTORTION = 0, 4, 6, 8, 11, 14, 18, 28, 29, 30
ACBASS, FINGER, PICKBASS, FRETLESS, SYNBASS1, SYNBASS, CELLO, CONTRABASS, PIZZ, HARP, TIMPANI = 32, 33, 34, 35, 38, 39, 42, 43, 45, 46, 47
STRINGS, SLOWSTR, CHOIR, SYNBRASS, SQUARE, SAW, POLYSYNTH = 48, 49, 52, 62, 80, 81, 90
GLOCK, MUSICBOX, MARIMBA, CHURCH, REED, TREMOLO, SPACEVOICE, GLASS, VOICE, HORN, CLARINET, FLUTE, RECORDER, WARMPAD = 9, 10, 12, 19, 20, 44, 91, 92, 53, 60, 71, 73, 74, 89
# percussion keys
KICK, KICK2, SNARE, ESNARE, HAT, OHAT, CRASH, RIDE, RBELL = 36, 35, 38, 40, 42, 46, 49, 51, 53
TOM1, TOM2, TOM3, TOM4, WOOD_HI, WOOD_LO, STICK, CLAP, TAMB, CASTANET = 48, 47, 45, 41, 76, 77, 37, 39, 54, 85


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

    def voice(self, name, program, root, patterns, form, vel=90, gate=0.85, volume=100, pan=64, reverb=40, bend=0,
              loose=0):
        """A pitched voice. `root` is the MIDI note of the key note in this voice's register; `bend` puts the
        whole voice that many hundredths of a semitone out of tune (below zero: flat); `loose` lets every note
        come up to that many ticks late or half as many early (a child playing; a step is PPQ / per_beat ticks)."""
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
        self._loosen(notes, loose)
        used = {v["channel"] for v in self.voices}
        channel = next(c for c in range(16) if c != DRUMS and c not in used)
        self.voices.append(dict(name=name, channel=channel, program=program, volume=volume, pan=pan, reverb=reverb,
                                gate=gate, notes=notes, bend=bend))

    def _loosen(self, notes, loose):
        late = {}                               # the notes of one chord together
        for n in notes if loose else ():
            n.append(late.setdefault(n[0], self.rng.randint(-loose // 2, loose)))

    def drums(self, patterns, form, vel=96, volume=105, loose=0):
        """patterns: name -> {key: 'x..X..o.'}: x a hit, X a loud one, o a soft one. Can be called again for a
        second row of hits (hands clapping not quite together: `loose`, as for a voice)."""
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
        self._loosen(notes, loose)
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
            if v.get("bend"):                   # the wheel's whole way is two semitones each side
                w = max(0, min(16383, 8192 + round(v["bend"] * 8192 / 200)))
                ev.append((0, 0, bytes([0xE0 | c, w & 127, w >> 7])))
            spans, sounding = [], {}            # a loose voice: pitch -> its last note, which is cut short when
            for s, n, p, vel, *late in v["notes"]:          # the same note comes again before it is over
                on = s * self.tick
                off = min(end, on + max(self.tick // 4, int((n - 1 + v["gate"]) * self.tick)))
                if late:
                    on, off = max(0, on + late[0]), min(end, max(off + late[0], on + late[0] + 1))
                    if p in sounding and sounding[p][1] > on:
                        sounding[p][1] = on
                    sounding[p] = span = [on, off, p, vel]
                    spans.append(span)
                else:
                    spans.append((on, off, p, vel))
            for on, off, p, vel in spans:
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



# The children's games, 2026-11-25 (see the top): five of one sort, from the still one to the fast one. Each is built
# as an older piece is (named in its first line), so what is new is the riffs, the tunes and the playground in them.

def grandmothers_footsteps():
    """D, 56 a minute. The still one, built as After Hours: whoever is seen moving is out. Plucked steps come on and
    stop dead, a music box, a recorder far off with the taunt, three knocks before every round."""
    p = Piece("Grandmother's Footsteps", 56)
    hold = " ".join("-" * 16)
    # two bars each: D minor, E flat major, D minor, A major
    p.voice("strings", SLOWSTR, 50, {
        "m": "1m - - - - - - - - - - - - - - -", "M": "1M - - - - - - - - - - - - - - -", "T": hold,
    }, rep("m T M+1 T m T M-5 T", 4), vel=66, gate=1.0, volume=88, pan=54, reverb=80)
    p.voice("drone", CONTRABASS, 38, {
        "D": "1 - - - - - - - - - - - - - - -", "T": hold,
    }, rep("D T D+1 T D T D-5 T", 4), vel=82, gate=1.0, volume=102)
    p.voice("steps", PIZZ, 50, {                        # three steps and stock still; one more when nobody looks
        "a": "1 . . . 5, . . . 1 . . . . . . .",
        "b": ". . . . . . . . . . . . 5, . . .",
    }, rep("_", 8, "a b a+1 b+1 a b a-5 _", 3), vel=72, gate=0.5, volume=90, pan=34, reverb=60)
    p.voice("music box", MUSICBOX, 74, {                # each chord falls and comes half-way back
        "B1": ". . . . 1' - - - 5 - - - b3 - - -",
        "B2": "5 - - - - - - - - - - - . . . .",
        "B3": ". . . . b2' - - - b6 - - - 4 - - -",
        "B4": "b6 - - - - - - - - - - - . . . .",
        "B5": ". . . . b3' - - - 1' - - - 5 - - -",
        "B6": "4 - - - b3 - - - - - - - . . . .",
        "B7": ". . . . 2' - - - 7 - - - 5 - - -",
        "B8": "7 - - - - - - - - - - - . . . .",
    }, rep("_", 8, "B1 B2 B3 B4 B5 B6 B7 B8", 1, "_", 8, "B1 B2 B3 B4 B5 B6 B7 B8", 1), vel=80, gate=1.0, volume=96,
            pan=44, reverb=80)
    p.voice("recorder", RECORDER, 74, {                 # the taunt, slow; over E flat it comes out as children sing it
        "Ra": "5 - - - - - - - b3 - - - 5 - - -",
        "Rb": "b6 - - - 5 - - - b3 - - - . . . .",
        "Rc": "b6 - - - - - - - 4 - - - b6 - - -",
        "Rd": "b7 - - - b6 - - - 4 - - - . . . .",
        "Re": "2 - - - - - - - 7, - - - 2 - - -",
        "Rf": "b3 - - - 2 - - - 7, - - - . . . .",
    }, rep("_", 16, "Ra Rb Rc Rd Ra Rb Re Rf", 1, "_", 8), vel=70, gate=0.97, volume=84, pan=80, reverb=110)
    p.voice("voice", VOICE, 62, {                       # A, B flat, A, A
        "a": "5 - - - - - - - - - - - - - - -", "b": "b6 - - - - - - - - - - - - - - -", "T": hold,
    }, rep("_", 16, "a T b T a T a T", 2), vel=58, gate=1.0, volume=76, pan=74, reverb=90)
    p.voice("harp", HARP, 50, {
        "H": "1 . . . 5 . . . 1' . . . 5 . . .",
    }, rep("_", 24, "H H H+1 H+1 H H H-5 H-5", 1), vel=62, gate=1.0, volume=82, pan=40, reverb=80)
    p.drums({
        "k": {WOOD_LO: "..........x.x.x."},
    }, rep("_ _ _ _ _ _ _ k", 4), vel=72, volume=88)
    return p


def knock_down_ginger():
    """A, 100 a minute. The middle one. The school band first: one recorder has the tune, which is the cheer itself
    (three, three, seven), over castanets and nothing else; then the class, ragged and a little flat, with a toy drum;
    only then the riff comes in under them. Two chords in the verse, A minor and D major (the bright fourth, no sad
    sixth anywhere); the chorus walks C, G, D to A MAJOR."""
    p = Piece("Knock Down Ginger", 100)
    hold = " ".join("-" * 16)
    # 60 bars: castanets 4, the recorder alone 8, the class 8, the riff under them 8, chorus 8, the stop 8, all 8, chorus 8
    cheer = {                                           # five notes and no third: it is neither glad nor sad
        "a1": "5 - 5 - 6 - - . 5 - 5 - 4 - - .",
        "a2": "5 - 6 - 5 - 4 - 2 - 4 - 5 - - .",
        "b1": "1' - 1' - 2' - - . 1' - 1' - 6 - - .",
        "b2": "1' - 6 - 5 - 4 - 5 - 6 - 5 - - .",
        "c1": "4 - 4 - 5 - - . 4 - 4 - 2 - - .",
        "c2": "1 - 2 - 4 - 5 - 4 - 2 - 1 - - .",
    }
    tune = "a1 a2 b1 b2 a1 a2 c1 c2".split()
    p.voice("recorder", RECORDER, 69, cheer, rep("_", 4) + tune * 3 + rep("_", 16) + tune + rep("_", 8),
            vel=102, gate=0.8, volume=118, pan=56, reverb=50, loose=8)
    p.voice("the class", RECORDER, 69, cheer, rep("_", 12) + tune * 2 + rep("_", 16) + tune + rep("_", 8),
            vel=86, gate=0.8, volume=100, pan=86, reverb=50, bend=-15, loose=24)
    p.voice("one more", RECORDER, 69, cheer, rep("_", 44) + tune + rep("_", 8),
            vel=84, gate=0.8, volume=96, pan=30, reverb=50, bend=10, loose=20)
    p.voice("glockenspiel", GLOCK, 81, cheer, rep("_", 20) + tune + rep("_", 16) + tune + rep("_", 8),
            vel=72, gate=1.0, volume=84, pan=40)
    p.voice("melodica", REED, 57, {
        "n": "1^ - - - - - - - - - - - - - - .", "d": "4,M - - - - - - - - - - - - - - .",
    }, rep("_", 12, "n n d d n n d n", 1, "_", 24, "n n d d n n d n", 1, "_", 8), vel=64, gate=1.0, volume=80, pan=70)
    verse, walk = "A1 A2 D1+5 D2+5 A1 A2 D1+5 A2", "C+3 C-2 C+5 S C+3 C-2 C+5 S"
    p.voice("bass", PICKBASS, 33, {
        "A1": "1 . 1 . 1 . . . b3 . b3 . b7, . . .",
        "A2": "1 . 1 . 5, . b7, . 5, . b7, . 1 . . .",
        "D1": "1 . 1 . 3 . . . 1 . 1 . 6, . . .",
        "D2": "1 . 1 . 5, . 1 . 5, . 6, . 5, . . .",
        "C": "1 . 1 . 1 . . . 1 . 1 . 1 . . .",
        "S": "1 . 1 . 1 . 1 . 1 . 1 . 1 . . .",
    }, rep("_", 20, verse, 1, walk, 1, "_", 8, verse, 1, walk, 1), vel=104, gate=0.8, volume=115)
    p.voice("guitar", OVERDRIVE, 45, {
        "A1": "1^! . 1 . 1 . . . b3^! . b3 . b7, . . .",
        "A2": "1^! . 1 . 5, . b7, . 5,^ . b7, . 1 . . .",
        "D1": "1^! . 1 . 3 . . . 1^! . 1 . 6, . . .",
        "D2": "1^! . 1 . 5, . 1 . 5,^ . 6, . 5, . . .",
        "C": "1*! - - - - - . . 1* - - - - - . .",
        "S": "1*! . 1* . 1* . 1* . 1* . 1* . 1* . . .",
    }, rep("_", 20, verse, 1, walk, 1, "_", 8, verse, 1, walk, 1), vel=84, gate=0.75, volume=92, pan=50)
    p.voice("organ", ORGAN, 57, {
        "M": "1M - - - - - - - - - - - - - - -",
    }, rep("_", 28, "M+3 M-2 M+5 M", 2, "_", 16, "M+3 M-2 M+5 M", 2), vel=60, gate=1.0, volume=76, pan=80)
    p.voice("lead", DISTORTION, 57, {                   # over C, G, D and A major
        "K1": "5 - - - - - - - b7 - - - 5 - - -",
        "K2": "4 - - - - - - - 2 - - - b7, - - -",
        "K3": "4 - - - - - - - 6 - - - 1' - - -",
        "K4": "3' - - - - - - - - - - - . . . .",
        "K5": "b7 - - - - - - - b3' - - - 5' - - -",
        "K6": "4' - - - - - - - 2' - - - b7 - - -",
        "K7": "6 - - - - - - - 1' - - - 4' - - -",
        "K8": "3' - - - - - - - 1' - - - - - - -",
    }, rep("_", 28, "K1 K2 K3 K4 K5 K6 K7 K8", 1, "_", 16, "K1 K2 K3 K4 K5 K6 K7 K8", 1), vel=92, gate=0.97,
            volume=96, pan=44, reverb=60)
    p.voice("voices", CHOIR, 57, {                      # ha, ha, ha
        "H": "1^ . 1^ . 1^ . . . 1^ . 1^ . 1^ . . .",
        "s": "1^ . 1^ . 1^ . 1^ . 1^ . 1^ . 1^ . . .",
    }, rep("_", 28, "H+3 H-2 H+5 s", 2, "_", 16, "H+3 H-2 H+5 s", 2), vel=86, gate=0.9, volume=90, pan=76, reverb=70)
    # the stop: nobody moves; a music box has the cheer at half the speed
    p.voice("music box", MUSICBOX, 69, {
        "x1": "5 - - . 5 - - . 6 - - - - - . .",
        "x2": "5 - - . 5 - - . 4 - - - - - . .",
        "x3": "5 - - . 6 - - . 5 - - . 4 - - .",
        "x4": "2 - - . 4 - - . 5 - - - - - . .",
        "y1": "4 - - . 4 - - . 5 - - - - - . .",
        "y2": "4 - - . 4 - - . 2 - - - - - . .",
        "y3": "1 - - . 2 - - . 4 - - . 5 - - .",
        "y4": "4 - - . 2 - - . 1 - - - - - . .",
    }, rep("_", 36, "x1 x2 x3 x4 y1 y2 y3 y4", 1, "_", 16), vel=82, gate=1.0, volume=98, pan=44, reverb=80)
    p.voice("tremolo", TREMOLO, 45, {
        "a": "1^ - - - - - - - - - - - - - - -", "T": hold,
    }, rep("_", 36, "a T T T T T T T", 1, "_", 16), vel=58, gate=1.0, volume=76, pan=74, reverb=80)
    three, seven = "X.x.x...X.x.x...", "X.x.x.x.x.x.X..."
    hat, snare, ride = "X.x.X.x.X.x.X.x.", "....x.......x...", "x.x.x.x.x.x.x.x."
    fill = {TOM1: ".............x..", TOM2: "..............x.", TOM4: "...............x"}
    p.drums({
        "k1": {CASTANET: three},
        "k2": {CASTANET: seven},
        "t1": {CASTANET: three, TOM3: "x.......o.......", TAMB: "......o.......o."},     # a toy drum, a tambourine
        "t2": {CASTANET: seven, TOM3: "x.......o.......", TAMB: "..............o."},
        "a": {CASTANET: three, KICK: "x.x.....x.x.....", ESNARE: snare, HAT: hat},        # the kick twice, the snare once
        "b": {CASTANET: seven, KICK: "x.x...x.x.x.....", ESNARE: snare, HAT: hat},
        "f": {CASTANET: seven, KICK: "x.x...x.x.x.....", ESNARE: snare, HAT: "X.x.X.x.X.x.....", **fill},
        "c": {CRASH: "x...............", RIDE: ride, KICK: "x.x.....x.x.....", ESNARE: snare},
        "r": {RIDE: ride, KICK: "x.x.....x.x.....", ESNARE: snare},
        "g": {RIDE: "x.x.x.x.x.x.....", KICK: "x.x...x.x.x.....", ESNARE: snare, **fill},
        "n": {WOOD_LO: "x..............."},
        "kf": {CASTANET: seven, **fill},
    }, rep("k1 k2", 6, "t1 t2", 4, "a b a b a b a f", 1, "c r r g", 2, "n _ n _ n _ k1 kf", 1, "a b a b a b a f", 1,
           "c r r g", 2))
    p.drums({                                           # the class clapping, not quite together
        "c1": {CLAP: three.lower()}, "c2": {CLAP: seven.lower()},
    }, rep("_", 12, "c1 c2", 8, "_", 16, "c1 c2", 4, "c1 c1 c1 c2", 2), vel=88, loose=26)
    return p


def salt_mustard():
    """G, a 12/8 shuffle, 92 a minute. The skipping one. A rope on the ground and a recorder skipping in G MAJOR,
    while the bass goes down by semitones under it (G, F sharp, F, E, E flat, D): a nursery tune with one sour bar.
    Then the band has the same tune and the same way down in G minor. Then the major again, with everybody."""
    p = Piece("Salt, Mustard, Vinegar, Pepper", 92, steps=12, per_beat=3, sig=(12, 8))
    # 48 bars: the rope 4, the recorder alone 8, the class 8, the band in minor 8 + 8, the stop 4, all in major 8
    skip = {
        "M1": "5 - 3 5 - 3 1 - 3 5 - -",                 # G
        "M2": "5 - 2 5 - 2 7, - 2 5 - -",                # D over F sharp
        "M4": "6 - 4 6 - 4 1 - 4 6 - -",                 # C over E
        "M5": "b6 - 4 b6 - 4 1 - 4 b6 - -",              # C minor over E flat: the sour bar
        "M7": "4 - 2 4 - 2 7, - 2 4 - -",                # D seventh
        "M8": "3 - - 1 - - - - - . . .",
        "N1": "5 - b3 5 - b3 1 - b3 5 - -",              # G minor
        "N4": "b3' - 1' b3' - 1' 5 - 1' b3' - -",        # G minor over E
        "N5": "1' - b6 1' - b6 b3 - b6 1' - -",          # E flat
        "N8": "b3 - - 1 - - - - - . . .",
    }
    major, minor = "M1 M2 M1 M4 M5 M1 M7 M8".split(), "N1 M2 N1 N4 N5 N1 M7 N8".split()
    p.voice("recorder", RECORDER, 67, skip, rep("_", 4) + major * 2 + rep("_", 8) + minor + rep("_", 4) + major,
            vel=102, gate=0.85, volume=118, pan=56, reverb=50, loose=8)
    p.voice("the class", RECORDER, 67, skip, rep("_", 12) + major + rep("_", 8) + minor + rep("_", 4) + major,
            vel=86, gate=0.85, volume=100, pan=86, reverb=50, bend=-15, loose=24)
    p.voice("glockenspiel", GLOCK, 79, skip, rep("_", 28) + minor + rep("_", 4) + major, vel=72, gate=1.0, volume=84,
            pan=40)
    p.voice("lead", DISTORTION, 55, skip, rep("_", 20) + minor * 2 + rep("_", 12), vel=92, gate=0.9, volume=96, pan=44,
            reverb=60)
    down = "{0} {0}-1 {0}-2 {0}-3 {0}-4 {0}-5 {0}-5 {1}"                         # the way down, a bar a step
    p.voice("toy bass", ACBASS, 43, {
        "T": "1 - - . . . 1 - - . . .",
    }, rep("_", 12, down.format("T", "T"), 1, "_", 28), vel=92, gate=0.9, volume=104)
    chords = {
        "G": ". . . 1M . . . . . 1M . .", "D": ". . . 5,M . . . . . 5,M . .",
        "C": ". . . 4,M . . . . . 4,M . .", "c": ". . . 4,m . . . . . 4,m . .",
        "g": ". . . 1m . . . . . 1m . .", "E": ". . . b6,M . . . . . b6,M . .",
    }
    glad, grim = "G D G C c G D G".split(), "g D g g E g D g".split()
    p.voice("melodica", REED, 55, chords, rep("_", 12) + glad + rep("_", 28), vel=66, gate=0.9, volume=82, pan=70)
    line = down.format("C", "S")
    p.voice("bass", PICKBASS, 31, {                     # the rope rhyme's rhythm: salt, mustard, vinegar, pepper
        "C": "1 . . 1 . 1 1' 1 1 1' . 1",
        "S": "1 . . 1 . 1 1' . . 5, . 7,",
    }, rep("_", 20, line, 2, "_", 4, line, 1), vel=104, gate=0.8, volume=115)
    p.voice("guitar", OVERDRIVE, 43, {
        "C": "1! . . 1 . 1 1' 1 1! 1' . 1",
        "S": "1! . . 1 . 1 1' . . 5,! . 7,",
    }, rep("_", 20, line, 2, "_", 4, line, 1), vel=86, gate=0.75, volume=92, pan=50)
    p.voice("organ", ORGAN, 55, chords, rep("_", 20) + grim * 2 + rep("_", 4) + glad, vel=64, gate=0.7, volume=78,
            pan=80)
    p.voice("voices", CHOIR, 55, chords, rep("_", 28) + grim + rep("_", 12), vel=86, gate=0.9, volume=88, pan=74,
            reverb=70)
    p.voice("music box", MUSICBOX, 79, {                # the stop: the first two bars at half the speed
        "h1": "5 - - - 3 - 5 - - - 3 -",
        "h2": "1 - - - 3 - 5 - - - - -",
        "h3": "5 - - - 2 - 5 - - - 2 -",
        "h4": "7, - - - 2 - 5 - - - - -",
    }, rep("_", 36, "h1 h2 h3 h4", 1, "_", 8), vel=82, gate=1.0, volume=98, pan=44, reverb=80)
    rope, snare = "x..x..x..x..", "...x.....x.."
    p.drums({
        "h": {WOOD_LO: rope},                                                    # the rope on the ground
        "t": {WOOD_LO: rope, TAMB: "..o..o..o..o"},
        "a": {KICK: "x.....xx...x", ESNARE: snare, HAT: "X.xX.xX.xX.x"},
        "f": {KICK: "x.....xx....", ESNARE: "...x.....xxx", HAT: "X.xX.xX.x..."},
        "pa": {KICK: "x.....xx...x", ESNARE: snare, HAT: "XxxXxxXxxXxx"},        # pepper: the hats run
        "pf": {KICK: "x.....xx....", ESNARE: "...x.....xxx", HAT: "XxxXxxXxx..."},
        "n": {WOOD_LO: "x..........."},
        "nf": {WOOD_LO: rope, ESNARE: ".........xxx"},
    }, rep("h", 12, "t", 8, "a a a f", 2, "pa pa pa pf", 2, "n n n nf", 1, "pa pa pa pf", 2))
    p.drums({                                           # hands, on two and four, not quite together
        "c": {CLAP: "...x.....x.."},
    }, rep("_", 2, "c", 18, "_", 8, "c", 8, "_", 4, "c", 8), vel=88, loose=20)
    return p


def mr_wolf():
    """G, 136 a minute. The fast one, built as Fire Door and Paradox Engine: the guitar chugs three, three, seven in
    every bar; a recorder asks the time, the hour is struck (three, three, seven); a chase over held fifths; the stop."""
    p = Piece("What's the Time, Mr Wolf?", 136)
    hold = " ".join("-" * 16)
    riff = "W1 W1 W1 W2"
    verse = rep(riff, 2, "W1+5 W1+5 W1+5 W2+5", 1, riff, 1)                      # 16 bars: home, the 4th, home
    # 68 bars: the riff 4, verse 16, chase 8, verse 16, the stop 4, chase 16, the riff 4
    p.voice("guitar", DISTORTION, 43, {
        "W1": "1^! 1 1 . b3^! b3 b3 . 1^! 1 b3 1 4^ 1 b7, .",
        "W2": "1^! 1 1 . b3^! b3 b3 . 4^! 4 b5 4 b3^ 1 b7, .",
        "H": "1*! . 1* . 1* - - - 1*! . 1* . 1* - - -",
    }, rep(riff, 1) + verse + rep("H+8 H+10 H H", 2) + verse + rep("_", 4, "H+8 H+10 H H", 4, riff, 1),
            vel=86, gate=0.8, volume=94, pan=50)
    low = rep("p p p q", 2, "p+5 p+5 p+5 q+5", 1, "p p p q", 1)
    p.voice("bass", PICKBASS, 31, {
        "p": "1 . 1 . b3 . b3 . 1 . b3 . 4 . b7, .",
        "q": "1 . 1 . b3 . b3 . 4 . b5 . b3 . b7, .",
        "c": "1 . 1 . 1 - - . 1 . 1 . 1 - - .",
    }, rep("_", 4) + low + rep("c+8 c+10 c c", 2) + low + rep("_", 4, "c+8 c+10 c c", 4, "p p p q", 1),
            vel=106, gate=0.8, volume=115)
    ask = "Q1 Q2 _ _ Q1 Q3 _ _ Q1+5 Q2+5 _ _ Q1 Q3 _ _"
    call = {
        "Q1": "5 - 5 - b7 - 5 - 4 - b3 - 4 - - -",
        "Q2": "5 - - - - - - - . . . . . . . .",
        "Q3": "5 - - - b7 - - - 1' - - - . . . .",
    }
    p.voice("recorder", RECORDER, 67, call, rep("_", 4, ask, 1, "_", 8, ask, 1, "_", 24),
            vel=104, gate=0.85, volume=118, pan=58, reverb=50)
    p.voice("glockenspiel", GLOCK, 79, call, rep("_", 28, ask, 1, "_", 24), vel=74, gate=1.0, volume=84, pan=36,
            reverb=60)
    told = "_ _ o3 _ _ _ o3 o7 _ _ o3+5 _ _ _ o3 o7"
    p.voice("voices", CHOIR, 55, {                      # the hour: three, then three and seven
        "o3": "1^ - - . 1^ - - . 1^ - - . . . . .",
        "o7": "1^ . 1^ . 1^ . 1^ . 1^ . 1^ . 1^ - - .",
    }, rep("_", 4, told, 1, "_", 8, told, 1, "_", 24), vel=88, gate=0.9, volume=92, pan=74, reverb=70)
    p.voice("timpani", TIMPANI, 43, {
        "o3": "1 . . . 1 . . . 1 . . . . . . .",
        "o7": "1 . 1 . 1 . 1 . 1 . 1 . 1 . . .",
    }, rep("_", 4, told, 1, "_", 8, told, 1, "_", 24), vel=92, gate=0.9, volume=98, pan=72, reverb=60)
    chase = "D1 D2 D3 D4 D5 D6 D7 D8"
    p.voice("lead", OVERDRIVE, 55, {                    # dinner time: over E flat, F, G minor, G minor
        "D1": "b3' - - - 1' - b6 - 1' - - - b3' - - -",
        "D2": "4' - - - 2' - b7 - 2' - - - 4' - - -",
        "D3": "5' - - - 4' - b3' - 4' - 5' - b7' - 5' -",
        "D4": "5' - - - - - - - - - - - . . . .",
        "D5": "b6' - - - b3' - 1' - b3' - - - b6' - - -",
        "D6": "b7' - - - 4' - 2' - 4' - - - b7' - - -",
        "D7": "1'' - - - b7' - 5' - b7' - 1'' - b3'' - 1'' -",
        "D8": "1'' - - - - - - - - - - - - - - -",
    }, rep("_", 20, chase, 1, "_", 20, chase, 2, "_", 4), vel=92, gate=0.97, volume=96, pan=44, reverb=60)
    p.voice("strings", STRINGS, 55, {
        "m": "1m - - - - - - - - - - - - - - -", "M": "1M - - - - - - - - - - - - - - -",
    }, rep("_", 20, "M-4 M-2 m m", 2, "_", 20, "M-4 M-2 m m", 4, "_", 4), vel=64, gate=1.0, volume=78, pan=80,
            reverb=60)
    # the stop: the wolf has turned round; a music box asks at half the speed
    p.voice("music box", MUSICBOX, 79, {
        "Y1": "5 - - - 5 - - - b7 - - - 5 - - -",
        "Y2": "4 - - - b3 - - - 4 - - - - - - -",
        "Y3": "5 - - - - - - - - - - - - - - -",
    }, rep("_", 44, "Y1 Y2 Y3 _", 1, "_", 20), vel=84, gate=1.0, volume=100, pan=44, reverb=80)
    p.voice("tremolo", TREMOLO, 43, {
        "a": "1^ - - - - - - - - - - - - - - -", "T": hold,
    }, rep("_", 44, "a T T T", 1, "_", 20), vel=62, gate=1.0, volume=80, pan=74, reverb=80)
    snare, hat = "....x.......x...", "X.x.X.x.X.x.X.x."
    p.drums({
        "h": {HAT: "x.x.x.x.x.x.x.x."},
        "a": {KICK: "x.x...x.x.x.x...", SNARE: snare, HAT: hat},
        "f": {KICK: "x.x...x.x.......", SNARE: "....x.....x.xx..", TOM2: "..............x.", TOM4: "...............x",
              HAT: "X.x.X.x.X......."},
        "c": {CRASH: "x...............", KICK: "x.x.....x.x.....", SNARE: snare, RIDE: "x.x.x.x.x.x.x.x."},
        "r": {KICK: "x.x.....x.x.....", SNARE: snare, RIDE: "x.x.x.x.x.x.x.x."},
        "n": {WOOD_LO: "x..............."},
        "nf": {WOOD_LO: "x...............", SNARE: "..........x.xx..", TOM2: "..............x.", TOM4: "...............x"},
    }, rep("h", 4, "a a a f", 4, "c r r f", 2, "a a a f", 4, "n n n nf", 1, "c r r f", 4, "a a a f", 1), vel=98)
    return p


# Ambient, 2026-11-25 (see the top): no beat, and the chords are three lines that move one at a time.

def everything_else_moves():
    """E, 50 a minute. Ambient. One note stays, the E, through six chords two bars long, and at every change exactly
    one other note moves, by a step or half a step: A minor, C, E minor, E major, C sharp minor, A major, and the
    seventh change (C sharp to C) is the way back in. A vibraphone, then a clarinet that plays only the note that
    has just moved."""
    p = Piece("Everything Else Moves", 50)
    hold = " ".join("-" * 16)

    def line(**notes):
        return {k: f"{v} - - - - - - - - - - - - - - -" for k, v in notes.items()} | {"T": hold}

    # 36 bars, three times round: the chords over a held E; the vibraphone and the roots in the bass; clarinet and harp
    p.voice("line one", SLOWSTR, 52, line(a="4", g="b3", s="3"), rep("a T g T T T s T T T a T", 3),       # A G G G# G# A
            vel=64, gate=1.0, volume=88, pan=44, reverb=80)
    p.voice("line two", WARMPAD, 52, line(c="b6", b="5", x="6"), rep("c T T T b T T T x T T T", 3),      # C C B B C# C#
            vel=66, gate=1.0, volume=88, pan=84, reverb=80)
    p.voice("the one that stays", VOICE, 52, line(e="1'"), rep("e T", 18), vel=62, gate=1.0, volume=84, pan=64,
            reverb=90)
    p.voice("bass", CONTRABASS, 40, line(e="1", a="4,", c="b6,", x="6,"),
            rep("e T T T", 3, "a T c T e T e T x T a T", 2), vel=80, gate=1.0, volume=100)
    p.voice("vibraphone", VIBES, 64, {                  # two notes up to a long one; the long ones are line one's
        "V1": ". . . . . . . . 4 - - - b6 - - -",
        "V2": "1' - - - - - - - - - - - . . . .",
        "V3": ". . . . . . . . b6 - - - 1' - - -",
        "V4": "b3' - - - - - - - - - - - . . . .",
        "V5": ". . . . . . . . 5 - - - 1' - - -",
        "V6": "b3' - - - - - - - 5 - - - . . . .",
        "V8": "3' - - - - - - - - - - - . . . .",         # the same two notes up, and the top one half a step higher
        "V9": ". . . . . . . . 6 - - - 1' - - -",
        "V12": "4' - - - - - - - - - - - . . . .",
    }, rep("_", 12, "V1 V2 V3 V4 V5 V6 V5 V8 V9 V8 V9 V12", 1, "_", 12), vel=76, gate=1.0, volume=94, pan=36,
            reverb=80)
    p.voice("clarinet", CLARINET, 64, line(c="b6", g="b3", b="5", s="3", x="6", a="4"),    # C, G, B, G#, C#, A
            rep("_", 24, "c T g T b T s T x T a T", 1), vel=72, gate=0.97, volume=88, pan=58, reverb=80)
    p.voice("harp", HARP, 64, {
        "Ha": "4, - - - 1 - - - 4 - - - b6 - - -",
        "Hc": "b6, - - - 1 - - - b3 - - - b6 - - -",
        "He": "1, - - - 5, - - - 1 - - - b3 - - -",
        "HE": "1, - - - 5, - - - 1 - - - 3 - - -",
        "Hx": "6, - - - 1 - - - 3 - - - 6 - - -",
        "HA": "4, - - - 1 - - - 4 - - - 6 - - -",
    }, rep("_", 24, "Ha _ Hc _ He _ HE _ Hx _ HA _", 1), vel=62, gate=1.0, volume=82, pan=76, reverb=80)
    return p



# From Vadim's two sketches, 2026-11-25 (see the top). Of each pair the first is his chords as he voiced them.

DEGREES = ["1", "b2", "2", "b3", "3", "4", "b5", "5", "b6", "6", "b7", "7"]


NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def token(pitch, of):
    """A MIDI pitch as a pattern's token, counted from the key note `of`."""
    octave, degree = divmod(pitch - of, 12)
    return DEGREES[degree] + ("'" * octave if octave > 0 else "," * -octave)


def spell(text, again=0):
    """A line written as a note a bar ('F#4 E4 E4/F#4 ...': with a stroke, the second note comes in the middle of
    the bar) -> bar -> {step: pitch}, for write(). A note that is the same as the one before is held, not struck
    again, unless `again` bars have gone by since it was struck."""
    def pitch(name):
        return NOTE[name[0]] + name.count("#") - name.count("b") + 12 * (int(name[-1]) + 1)
    bars, last, since = [], None, 0
    for b, bar in enumerate(text.split()):
        notes = {}
        for step, name in zip((0, 8), bar.split("/")):
            p = pitch(name)
            if p != last or (again and step == 0 and since >= again):
                notes[step], last, since = p, p, 0
        bars.append(notes)
        since += 1
    return bars


def write(per_bar, of, steps=16, start=0, rest="-"):
    """Patterns and form for a line given as bar -> {step: pitch}: held between its notes, silent before `start`."""
    patterns, form = {}, []
    for b, notes in enumerate(per_bar):
        if b < start:
            form.append("_")
            continue
        patterns[f"n{b}"] = " ".join(token(notes[i], of) if i in notes else rest for i in range(steps))
        form.append(f"n{b}")
    return patterns, form


def echo(per_bar, of, steps=16, start=0, up=12, after=4, length=4):
    """Patterns and form for a voice that says each note of a line again, `after` steps later and `up` higher."""
    patterns, form = {}, []
    for b, notes in enumerate(per_bar):
        if b < start or not notes:
            form.append("_")
            continue
        row = ["."] * steps
        for s, pitch in notes.items():
            row[s + after:s + after + length] = [token(pitch + up, of)] + ["-"] * (length - 1)
        patterns[f"n{b}"] = " ".join(row[:steps])
        form.append(f"n{b}")
    return patterns, form


def held(steps=16, **notes):
    """Patterns for a line of held notes: each name a whole bar on that note, T a bar tied over."""
    return {k: " ".join([v] + ["-"] * (steps - 1)) for k, v in notes.items()} | {"T": " ".join("-" * steps)}


def distant_galaxy_four():
    """A, 54 a minute. Ambient. Vadim's eight chords, but no two lines move at once: where his three notes slip
    together to G sharp minor, here C goes to B, then A to G sharp, then E to D sharp, half a bar apart, and back
    the same way; and so through all eight, by a semitone or a tone at a time. Made as Garmonic I is (voice, slow
    strings, warm pad, a vibraphone the second time, a glass voice the third)."""
    p = Piece("Distant Galaxy IV", 54)
    #        Am        to G#m      and back    Dm         C over E    Em          F           E
    top = "E4 E4       E4/D#4 D#4/E4   E4 E4/F4    F4 F4/E4   E4 E4      E4 E4       E4/F4 F4/E4   E4 E4"
    middle = "C4 C4/B3 B3 B3       B3/A3 A3    A3 A3      A3/C4 C4   B3 B3/C4    C4 C4         C4/B3 B3/C4"
    low = "A3 A3       G#3 G#3     A3 A3       A3 A3      G3 G3      G3 G3       A3 A3         G#3 G#3"
    bass = "A2 A2      G#2 G#2     A2 A2       D2 D2      E2 E2      E2 E2       F2 F2         E2 E2"
    # 48 bars, three times round: the four lines; a vibraphone; a glass voice
    three = lambda text, **how: spell(" ".join(text.split() * 3), **how)
    p.voice("top line", VOICE, 57, *write(three(top, again=2), 57), vel=66, gate=1.0, volume=88, pan=52, reverb=90)
    p.voice("middle line", SLOWSTR, 57, *write(three(middle), 57), vel=64, gate=1.0, volume=88, pan=36, reverb=80)
    p.voice("low line", WARMPAD, 57, *write(three(low), 57), vel=66, gate=1.0, volume=88, pan=88, reverb=80)
    p.voice("bass", CONTRABASS, 45, *write(three(bass, again=2), 45), vel=80, gate=1.0, volume=100)
    tune = {                                    # two notes up to a long one, each once its chord has arrived
        "v1": ". . . . . . . . 1 - - - b3 - - -", "v2": "5 - - - - - - - - - - - . . . .",
        "v3": ". . . . . . . . 7, - - - 2 - - -", "v4": "b5 - - - - - - - . . . . . . . .",
        "v5": ". . . . . . . . 1 - - - 5 - - -", "v6": "1' - - - - - - - - - - - . . . .",
        "v7": ". . . . . . . . 4 - - - b6 - - -",
        "v9": ". . . . . . . . b7, - - - b3 - - -",
        "v11": ". . . . . . . . 2 - - - 5 - - -", "v12": "b7 - - - - - - - - - - - . . . .",
        "v14": "b6 - - - - - - - . . . . . . . .",
        "v16": "7 - - - - - - - - - - - . . . .",
    }
    notes = "v1 v2 v3 v4 v5 v6 v7 v6 v9 v2 v11 v12 v1 v14 v11 v16"
    p.voice("vibraphone", VIBES, 69, tune, rep("_", 16, notes, 1, "_", 16), vel=76, gate=1.0, volume=94, pan=30,
            reverb=80)
    p.voice("glass", GLASS, 69, tune, rep("_", 32, notes, 1), vel=66, gate=1.0, volume=84, pan=70, reverb=90)
    return p


def distant_galaxy_two():
    """D, 60 a minute. Ambient. The sketch's ideas, turned: its slip (a minor chord, the same chord a semitone lower,
    then home with no third) is done twice, on D and on G, and then his ending, B flat, A with the F still in it, A.
    No held chords at first: a harp gives each chord a note a second, up and down."""
    p = Piece("Distant Galaxy II", 60)
    # 48 bars, three times round: harp and bass; a pad and a glass tune; a celesta an octave over the harp
    harp = {
        "pa": "1 - - - 5 - - - 1' - - - b3' - - -", "pb": "5' - - - b3' - - - 1' - - - 5 - - -",      # minor
        "sa": "1 - - - 5 - - - 1' - - - 2' - - -", "sb": "5' - - - 2' - - - 1' - - - 5 - - -",        # no third
        "Ma": "1 - - - 5 - - - 1' - - - 3' - - -", "Mb": "5' - - - 3' - - - 1' - - - 5 - - -",        # major
        "Aa": "1 - - - 3 - - - b6 - - - 1' - - -", "Ab": "3' - - - 1' - - - 5 - - - 3 - - -",         # augmented, major
    }
    round_ = "pa pb pa-1 pb-1 sa sb pa-7 pb-7 pa-8 pb-8 sa-7 sb-7 Ma-4 Mb-4 Aa-5 Ab-5"
    p.voice("harp", HARP, 62, harp, rep(round_, 3), vel=70, gate=1.0, volume=92, pan=40, reverb=80)
    p.voice("celesta", CELESTA, 74, harp, rep("_", 32, round_, 1), vel=58, gate=1.0, volume=74, pan=80, reverb=80)
    p.voice("bass", CONTRABASS, 38, held(d="1", c="7,", g="4,", f="3,", b="b6,", a="5,"),
            rep("d T c T d T g T f T g T b T a T", 3), vel=80, gate=1.0, volume=100)
    p.voice("pad", WARMPAD, 62, held(m="1m", o="1*", M="1M", A="1a"),
            rep("_", 16, "m T m-1 T o T m-7 T m-8 T o-7 T M-4 T A-5 M-5", 2), vel=58, gate=1.0, volume=78, pan=64,
            reverb=80)
    p.voice("glass", GLASS, 62, held(a="5", s="b5", b="b6", d="1'", f="b3'", e="2'"),     # A G# A Bb A A D F/E
            rep("_", 16, "a T s T a T b T a T T T d T f e", 2), vel=70, gate=1.0, volume=88, pan=56, reverb=90)
    return p


def garmonic_one():
    """E flat, 54 a minute. Ambient. Vadim's sketch bar for bar: a B flat held on top; under it F sharp slips to F,
    then E flat to D (E flat minor has become B flat); again with a bass; E flat minor to D major with the F sharp
    kept, the B flat coming back over it; G minor; and back with the B flat kept. A vibraphone the second time,
    a glass voice the third."""
    p = Piece("Garmonic I", 54)
    late, last = "- - - - - - - - {} - - - - - - -", "- - - - - - - - - - - - {} - - -"   # in the middle, on the last beat
    # 48 bars, three times round: his lines (the bass from the fifth bar); the bass from the start and a tune; glass
    p.voice("top line", VOICE, 63, held(h="5", a="b5") | {"r": "- - - - 5 - - - - - - - - - - -"},
            rep("h T T T h T T T h a T r T T T T", 3), vel=66, gate=1.0, volume=88, pan=52, reverb=90)
    p.voice("middle line", SLOWSTR, 63, held(f="b3", n="2", g="3"), rep("f n T T f n T T f T T T g f T T", 3),
            vel=64, gate=1.0, volume=88, pan=36, reverb=80)
    p.voice("low line", WARMPAD, 63, held(e="1") | {"s": late.format("7,"), "u": last.format("1")},
            rep("e s T T e s T T e s T T T u T T", 3), vel=66, gate=1.0, volume=88, pan=88, reverb=80)
    walk = "e s T T e s T T m s T T g u T T"                                     # E flat, D; F sharp, D; G, E flat
    p.voice("bass", CONTRABASS, 39, held(e="1", m="b3", g="3") | {"s": late.format("7,"), "u": last.format("1")},
            rep("_", 4) + walk.split()[4:] + rep(walk, 2), vel=80, gate=1.0, volume=100)
    p.voice("cello", CELLO, 51, held(e="1", m="b3", g="3") | {"s": late.format("7,"), "u": last.format("b3")},
            rep("_", 4) + walk.split()[4:] + rep(walk, 2), vel=62, gate=1.0, volume=80, pan=70, reverb=70)
    tune = {
        "b1": ". . . . . . . . 1 - - - b3 - - -",
        "b2": "5 - - - - - - - - - - - . . . .",
        "b3": ". . . . . . . . 2 - - - 5 - - -",
        "b4": "7 - - - - - - - - - - - . . . .",
        "b8": "2' - - - - - - - - - - - . . . .",
        "b9": ". . . . . . . . b3 - - - 5 - - -",
        "b10": ". . . . . . . . b3 - - - b5 - - -",
        "b13": "7 - - - - - - - 5 - - - 3 - - -",
    }
    notes = "b1 b2 b3 b4 b1 b2 b3 b8 b9 b10 b4 b9 b13 _ b1 b2"
    p.voice("vibraphone", VIBES, 75, tune, rep("_", 16, notes, 1, "_", 16), vel=76, gate=1.0, volume=94, pan=30,
            reverb=80)
    p.voice("glass", GLASS, 75, tune, rep("_", 32, notes, 1), vel=66, gate=1.0, volume=84, pan=70, reverb=90)
    return p


def garmonic_two():
    """E flat, 54 a minute. Ambient. The first move of Vadim's sketch made into a chain. A minor chord's two lower
    notes slip a semitone, one and then the other, and it is the major chord a fifth higher; that chord's third
    drops and it is minor; again. E flat minor, B flat, B flat minor, F, F minor, C, C minor, G, G minor, and his last
    move (G minor to E flat minor, the B flat kept) closes the ring. No note ever goes any way but down a semitone,
    save one a time round; the chords climb by fifths; three times round and every line is an octave lower."""
    p = Piece("Garmonic II", 54)
    rounds = 3
    bars = rounds * 14
    lines = [63, 66, 70]                                # E flat, G flat, B flat
    root, third, fifth = 0, 1, 2                        # which line has which note of the chord
    moves = [[{} for _ in range(bars)] for _ in lines]  # line -> bar -> {step: pitch}
    roots = [{} for _ in range(bars)]                   # bar -> {step: pitch} for the bass
    for i, pitch in enumerate(lines):
        moves[i][0][0] = pitch

    def go(line, by, bar, step):
        lines[line] += by
        moves[line][bar][step] = lines[line]

    def low(pitch):                                     # the bass's octave: B flat 1 to A 2
        return 34 + (pitch - 34) % 12

    bar = 0
    for r in range(rounds):
        for chord in range(5):                          # E flat, B flat, F, C, G minor
            if chord:
                go(third, -1, bar, 0)                   # major to minor
            elif r:
                roots[bar][0] = low(lines[root])        # the bass comes in the second time round
            if chord < 4:
                go(third, -1, bar + 1, 0)               # his move: F sharp to F,
                go(root, -1, bar + 1, 8)                # then E flat to D
                root, third, fifth = fifth, root, third
                bar += 3
            else:
                go(root, -1, bar + 1, 0)                # his last: G to F sharp,
                go(fifth, +1, bar + 1, 8)               # then D to E flat
                root, third, fifth = fifth, root, third
                bar += 2
            if r:
                roots[bar - 2 if chord < 4 else bar - 1][8] = low(lines[root])

    for i, (program, pan, name) in enumerate(((SLOWSTR, 36, "line one"), (WARMPAD, 88, "line two"), (VOICE, 60, "line three"))):
        p.voice(name, program, 63, *write(moves[i], 63), vel=64, gate=1.0, volume=88, pan=pan, reverb=80)
    p.voice("bass", CONTRABASS, 39, *write(roots, 39, start=14), vel=80, gate=1.0, volume=100)
    p.voice("voices", CHOIR, 51, *write([{s: n + 12 for s, n in b.items()} for b in roots], 51, start=28),
            vel=54, gate=1.0, volume=72, pan=74, reverb=90)
    # the second and third time a vibraphone says again, a beat later and higher, each note that has just moved
    said = [{} for _ in range(bars)]
    for line in moves:
        for b, notes in enumerate(line):
            for s, pitch in notes.items():
                if b >= 14:
                    said[b][s + 4] = 75 + (pitch - 75) % 12
    patterns, form = {}, []
    for b, notes in enumerate(said):
        if not notes:
            form.append("_")
            continue
        row = ["."] * p.steps
        for s, pitch in notes.items():
            row[s:s + 4] = [token(pitch, 75), "-", "-", "-"]
        patterns[f"n{b}"] = " ".join(row)
        form.append(f"n{b}")
    p.voice("vibraphone", VIBES, 75, patterns, form, vel=72, gate=1.0, volume=90, pan=30, reverb=80)
    return p


# On the harmony of Morten Lauridsen's O Magnum Mysterium (1994), 2026-11-25: Vadim asked for "couple slow versions
# on that harmonic ideas". None of its notes, tune or chord order are here; what is taken is how its harmony is made,
# as far as it is on record and as Claude remembers it: everything in one major key, plain chords and no chord that
# pushes (no dominant seventh), many chords with their third in the bass and the bass going by step, a second or a
# sixth added and left there, a note held over a change and let down a step afterwards, endings from the fourth
# chord to home, and ONE note in the whole piece from outside the key: the raised fourth, leaning on the fifth.

def mysterium_two():
    """G, 50 a minute. Ambient. Chords with the third in the bass walking down the scale, and the top line always
    late: it holds while the others step down, then follows (a chain of sevenths let down to sixths; where that
    would put an F sharp under its C, which is the chord that pushes, the middle line waits with it); each time it
    ends from the fourth chord to home. All in G major; at the very end of the third time a clarinet comes in
    for four bars and has the one note from outside, a C sharp."""
    p = Piece("Mysterium II", 50)
    #        down, the top late       settling                  down again, higher         home
    top = "C5 C5/B4 B4/A4 A4/G4       G4 G4 G4 G4               E5 E5/D5 D5/C5 C5/B4       G4 G4 G4 G4"
    middle = "G4 G4/F#4 E4 D4         E4 D4 E4 D4               B4 A4 G4 G4/F#4            E4 D4 E4 D4"
    low = "E4 D4 C4 B3                C4 B3 C4 A3               G4 F#4 E4 D4               C4 B3 C4 B3"
    bass = "E2 D2 C2 B1               C2 B1 A1 D2               G2 F#2 E2 D2               C2 D2 G2 G2"
    # 48 bars, three times round: the four lines; a vibraphone after the top line; the clarinet's four bars
    three = lambda text, **how: spell(" ".join(text.split() * 3), **how)
    p.voice("top line", VOICE, 67, *write(three(top, again=2), 67), vel=66, gate=1.0, volume=88, pan=56, reverb=90)
    p.voice("middle line", SLOWSTR, 67, *write(three(middle), 67), vel=62, gate=1.0, volume=86, pan=36, reverb=80)
    p.voice("low line", WARMPAD, 67, *write(three(low), 67), vel=64, gate=1.0, volume=86, pan=88, reverb=80)
    p.voice("bass", CONTRABASS, 43, *write(three(bass, again=1), 43), vel=80, gate=1.0, volume=100)
    p.voice("vibraphone", VIBES, 67, *echo(three(top), 67, start=16), vel=66, gate=1.0, volume=84, pan=28, reverb=80)
    p.voice("clarinet", CLARINET, 67, {
        "e": "6 - - - - - - - - - - - - - - -",           # E over the fourth chord
        "x": "b5 - - - - - - - 5 - - - - - - -",         # C sharp, and it gives way to D
        "d": "5 - - - - - - - - - - - - - - -",
    }, rep("_", 44, "e x e d", 1), vel=74, gate=0.97, volume=90, pan=70, reverb=80)
    return p


# Fast, the Doom way, on Vadim's two sketches, 2026-11-25 (see the top): an experiment he asked for.

FAST_DRUMS = {
    "h": {HAT: "x.x.x.x.x.x.x.x."},
    "a": {KICK: "x.x...x.x.x...x.", SNARE: "....x.......x...", HAT: "X.x.X.x.X.x.X.x."},
    "f": {KICK: "x.x...x.x.......", SNARE: "....x.....x.xx..", TOM2: "..............x.", TOM4: "...............x",
          HAT: "X.x.X.x.X......."},
    "c": {CRASH: "x...............", KICK: "x..x..x...x.....", SNARE: "....x.......x...", RIDE: "x.x.x.x.x.x.x.x."},
    "r": {KICK: "x..x..x...x.....", SNARE: "....x.......x...", RIDE: "x.x.x.x.x.x.x.x."},
}


def distant_galaxy_fast():
    """A, 132 a minute. The Doom way. Vadim's first four chords are the verse, four bars of one riff each: on A,
    a semitone lower, on A with no third, on D; from the second verse a square wave holds his top line over it, E,
    D sharp, E, F. His other four are the chorus, two bars each, twice: held fifths on C over an E bass, E minor,
    F, E, and a guitar tune whose C stays over the last E before it falls to B."""
    p = Piece("Distant Galaxy, Fast", 132)
    riffs = {
        "R": "1! . 1 1 b3 . 1 1 5 . 1 1 b7 . 5 .", "Rb": "1! . 1 1 b3 . 1 1 5 . 1 1 b7 . 1' b7",
        "S": "1! . 1 1 5 . 1 1 1' . 1 1 5 . 4 .", "Sb": "1! . 1 1 5 . 1 1 1' . 1 1 5 . 4 5",       # no third
    }
    intro = rep("R R R Rb", 1)
    verse = rep("R R R Rb", 1, "R-1 R-1 R-1 Rb-1", 1, "S S S Sb", 1, "R+5 R+5 R+5 Rb+5", 1)
    quiet = lambda bars: rep("_", bars)
    # 104 bars: 4 in; verse 16, chorus 16; verse, chorus; 4 of the bass alone; verse, chorus
    p.voice("guitar", DISTORTION, 45, riffs | {
        "C": "1^! - - 1^ - - 1^ - - - 1^ - 1^ - - -", "U": "1! - - 1 - - 1 - - - 1 - 1 - - -",
    }, intro + (verse + rep("C+3 C+3 C-5 C-5 C-4 C-4 U-5 C-5", 2)) * 2 + quiet(4) + verse
            + rep("C+3 C+3 C-5 C-5 C-4 C-4 U-5 C-5", 2), vel=86, gate=0.8, volume=94, pan=50)
    low = rep("c-5 c-5 c-5 c-5 c-4 c-4 c-5 c-5", 2)                       # E under C and E minor, F, E
    p.voice("bass", PICKBASS, 33, riffs | {"c": "1 . . 1 . . 1 . . . 1 . 1 . . ."},
            quiet(4) + (verse + low) * 2 + intro + verse + low, vel=106, gate=0.8, volume=115)
    pads = rep("M+3 M+3 m-5 m-5 M-4 M-4 a-5 M-5", 2)
    p.voice("strings", STRINGS, 57, {k: f"1{k} - - - - - - - - - - - - - - -" for k in "mMa"},
            quiet(20) + pads + quiet(16) + pads + quiet(20) + pads, vel=64, gate=1.0, volume=78, pan=40, reverb=60)
    tune = rep("K1 K2 K3 K4 K5 K6 K7 K8", 2)
    p.voice("lead", OVERDRIVE, 69, {
        "K1": "5 - - - - - - - b7 - - - b3' - - -",
        "K2": "b7 - - - - - - - - - - - 5 - - -",
        "K3": "2' - - - - - - - b7 - - - 5 - - -",
        "K4": "b7 - - - - - - - - - - - 2 - b7 -",
        "K5": "1' - - - - - - - b6 - - - 1' - - -",
        "K6": "b3' - - - - - - - - - - - 1' - - -",
        "K7": "b3' - - - - - - - 7 - - - 5 - - -",
        "K8": "2' - - - - - - - - - - - - - - -",
    }, quiet(20) + tune + quiet(16) + tune + quiet(20) + tune, vel=92, gate=0.97, volume=96, reverb=60)
    slip = rep("e T T T s T T T e T T T f T T T", 1)
    p.voice("square", SQUARE, 69, held(e="5", s="b5", f="b6"),
            quiet(36) + slip + quiet(20) + slip + quiet(16), vel=74, gate=1.0, volume=80, pan=74, reverb=50)
    stabs = rep("s", 4, "s-1", 4, "o", 4, "s+5", 4)
    p.voice("organ", ORGAN, 57, {
        "s": ". . 1m . . . 1m . . . 1m . . . 1m .", "o": ". . 1^ . . . 1^ . . . 1^ . . . 1^ .",
    }, quiet(72) + stabs + quiet(16), vel=62, gate=0.7, volume=76, pan=80)
    p.drums(FAST_DRUMS, rep("h", 4, "a a a f", 4, "c r r f", 4, "a a a f", 4, "c r r f", 4, "h", 4, "a a a f", 4,
                            "c r r f", 4), vel=98)
    return p


def garmonic_fast():
    """E flat, 128 a minute. The Doom way. Vadim's held B flat is a muted guitar on that one note, alone for four
    bars and then all through. Under it a riff of three notes, of which one slips from bar to bar as in his sketch:
    E flat, G flat, B flat; E flat, F, B flat; D, F, B flat. The second half is his other chords, the muted guitar
    now on the F sharp they keep: E flat minor over F sharp, D, D with the B flat back, G minor, home. A brass tune
    the second time round, strings the third."""
    p = Piece("Garmonic, Fast", 128)
    riffs = {
        "X": "1! . 1 1 b3 . 1 1 5 . 1 1 b3 . 5 .", "Xb": "1! . 1 1 b3 . 1 1 5 . 1 1 b3 . 5 b3",    # minor
        "W": "1! . 1 1 2 . 1 1 5 . 1 1 2 . 5 .",                                                  # its third slipped
        "Y": "1! . 1 1 b3 . 1 1 b6 . 1 1 b3 . b6 .", "Yb": "1! . 1 1 b3 . 1 1 b6 . 1 1 b3 . b6 b3",  # and its root
        "P": "1! . 1 1 3 . 1 1 6 . 1 1 3 . 6 .",                                                  # the third lowest
        "Q": "1! . 1 1 3 . 1 1 5 . 1 1 3 . 5 .", "Qa": "1! . 1 1 3 . 1 1 b6 . 1 1 3 . b6 .",      # major, augmented
    }
    first = rep("X W Y-1 Yb-1", 4)                                       # 16 bars
    second = rep("P+3 P+3 Q-1 Qa-1 X+4 X+4 X Xb", 2)                     # 16 bars
    quiet = lambda bars: rep("_", bars)
    # 104 bars: 4 of the one note; both halves three times, the bass alone for 4 before the third
    p.voice("guitar", DISTORTION, 39, riffs, quiet(4) + (first + second) * 2 + quiet(4) + first + second,
            vel=86, gate=0.8, volume=94, pan=50)
    p.voice("bass", PICKBASS, 27, riffs, quiet(4) + (first + second) * 2 + rep("X W Y-1 Yb-1", 1) + first + second,
            vel=106, gate=0.8, volume=115)
    kept = rep("b", 16, "g", 4, "b", 4, "g", 4, "b", 4)                  # B flat; F sharp, B flat, twice
    p.voice("the one note", MUTED, 51, {
        "b": "5! - - 5 - - 5 - 5 - - 5 - - 5 -", "g": "b3! - - b3 - - b3 - b3 - - b3 - - b3 -",
    }, rep("b", 4) + kept * 2 + rep("b", 4) + kept, vel=84, gate=0.7, volume=92, pan=84)
    tune = {
        "b1": ". . . . . . . . 1 - - - b3 - - -", "b2": "5 - - - - - - - - - - - . . . .",
        "b3": ". . . . . . . . 2 - - - 5 - - -", "b4": "7 - - - - - - - - - - - . . . .",
        "b8": "2' - - - - - - - - - - - . . . .",
        "p1": ". . . . . . . . b3 - - - 5 - - -", "p2": "1' - - - - - - - - - - - . . . .",
        "q1": ". . . . . . . . b3 - - - b5 - - -", "q2": "7 - - - - - - - - - - - . . . .",
        "g1": "7 - - - - - - - 5 - - - 3 - - -", "g2": "5 - - - - - - - 7 - - - - - - -",
        "x2": "5 - - - - - - - - - - - - - - -",
    }
    sung = rep("b1 b2 b3 b4 b1 b2 b3 b8", 2, "p1 p2 q1 q2 g1 g2 b1 x2", 2)
    p.voice("brass", SYNBRASS, 63, tune, quiet(36) + sung + quiet(4) + sung, vel=90, gate=0.97, volume=96, pan=40,
            reverb=50)
    p.voice("strings", STRINGS, 51, {k: f"1{k} - - - - - - - - - - - - - - -" for k in "mMa"},
            quiet(88) + rep("m m M-1 a-1 m+4 m+4 m m", 2), vel=64, gate=1.0, volume=78, pan=64, reverb=60)
    p.drums(FAST_DRUMS, rep("h", 4, "a a a f", 4, "c r r f", 4, "a a a f", 4, "c r r f", 4, "h", 4, "a a a f", 4,
                            "c r r f", 4), vel=98)
    return p


# On Paradox Engine, 2026-11-26 (see the top): Vadim asked for five fast and five slow variations to choose from,
# "main melodic idea should be the same, with some variations, also different instruments, rhytms, etc". Its two
# tunes as patterns, for the pieces below. engine() has its own copy and is not touched.

ENGINE_OVER_RIFF = {                            # the tune over the riff (the square wave's in Paradox Engine)
    "Q1": "1 - - - - - b2 - 1 - - - b7, - - -",
    "Q2": "1 - - - - - - - . . . . 5, - b7, -",
    "Q3": "1 - - - - - b2 - b3 - - - b2 - - -",
    "Q4": "1 - - - - - - - - - - - . . . .",
    "Q5": "5 - - - - - b6 - 5 - - - 4 - - -",
    "Q6": "b3 - - - - - 4 - b3 - - - b2 - - -",
    "Q7": "1 - - - b2 - - - b3 - - - 4 - - -",
    "Q8": "1' - - - - - - - - - - - - - - -",
}
ENGINE_CHORUS = {                               # the tune of the chorus, over the flat 6th, flat 7th, home, home
    "S1": "1' - - - - - - - b6 - - - 1' - - -",
    "S2": "2' - - - - - - - b7 - - - 2' - - -",
    "S3": "4' - - - b3' - - - 1' - - - - - b7 -",
    "S4": "1' - - - - - - - - - - - . . . .",
    "S5": "4' - - - - - - - 1' - - - 4' - - -",
    "S6": "5' - - - - - - - 2' - - - 5' - - -",
    "S7": "5' - - - 4' - - - b3' - - - 4' - 5' -",
    "S8": "1'' - - - - - - - - - - - - - - -",
}
# The second way of playing each: the same bars, the same first note in each, the long notes walked through.
ENGINE_OVER_RIFF_2 = {
    "Q1": "1 - - - - - b2 - 1 - b7, - 5, - b7, -",
    "Q2": "1 - - - - - - - b3 - - - b2 - 1 -",
    "Q3": "1 - b2 - b3 - - - 4 - - - b3 - b2 -",
    "Q4": "1 - - - - - - - - - - - 5 - b6 -",
    "Q5": "5 - - - - - b6 - 5 - 4 - b3 - 4 -",
    "Q6": "b3 - - - - - 4 - b3 - b2 - 1 - b2 -",
    "Q7": "1 - b2 - b3 - 4 - 5 - - - b7 - - -",
    "Q8": "1' - - - - - - - - - - - - - - -",
}
ENGINE_CHORUS_2 = {
    "S1": "1' - - - - - b7 - b6 - - - 1' - - -",
    "S2": "2' - - - - - 1' - b7 - - - 2' - - -",
    "S3": "4' - - - b3' - 2' - 1' - - - - - b7 -",
    "S4": "1' - - - - - - - 5 - - - 1' - - -",
    "S5": "4' - - - - - b3' - 1' - - - 4' - - -",
    "S6": "5' - - - - - 4' - 2' - - - 5' - - -",
    "S7": "5' - 4' - b3' - 4' - 5' - - - b7' - - -",
    "S8": "1'' - - - - - - - - - - - - - - -",
}
# Both tunes cut for a bar of twelve (12/8: four beats of three), the same notes in the same order.
ENGINE_OVER_RIFF_12 = {
    "Q1": "1 - - - - b2 1 - - b7, - -",
    "Q2": "1 - - - - - . . . 5, - b7,",
    "Q3": "1 - - - - b2 b3 - - b2 - -",
    "Q4": "1 - - - - - - - - . . .",
    "Q5": "5 - - - - b6 5 - - 4 - -",
    "Q6": "b3 - - - - 4 b3 - - b2 - -",
    "Q7": "1 - - b2 - - b3 - - 4 - -",
    "Q8": "1' - - - - - - - - - - -",
}
ENGINE_CHORUS_12 = {
    "S1": "1' - - - - - b6 - - 1' - -",
    "S2": "2' - - - - - b7 - - 2' - -",
    "S3": "4' - - b3' - - 1' - - - - b7",
    "S4": "1' - - - - - - - - . . .",
    "S5": "4' - - - - - 1' - - 4' - -",
    "S6": "5' - - - - - 2' - - 5' - -",
    "S7": "5' - - 4' - - b3' - - 4' - 5'",
    "S8": "1'' - - - - - - - - - - -",
}


# --- the fast ones on Paradox Engine (three kept of five) ---

def engine_shuffle():
    """D, a 12/8 shuffle, 132 a minute. Paradox Engine in triplets: its riff falls into four beats of three by
    itself (the hidden notes on the last of a beat, the last two together), on an overdriven guitar; the bass plays
    the shuffle on D, long and short, and joins the guitar's turn in the fourth bar. A rock organ is the main voice
    and has the tune over the riff, later an octave up; in the chorus it stabs the chords on two and four under
    synth brass with the chorus tune (the second time a lead guitar has it, the third time both)."""
    p = Piece("Paradox Engine, Shuffle", 132, steps=12, per_beat=3, sig=(12, 8))
    riff = "X1 X1 X1 X2"
    chorus = rep("C+8 C+10 C C", 2)
    quiet = lambda bars: rep("_", bars)
    # 64 bars: 4 in; verse 8, the 4th and home 8; chorus; verse; chorus; 4 of the bass alone; verse; chorus
    p.voice("guitar", OVERDRIVE, 38, {
        "X1": "1! 1 b2' 1 1 b3' 1 1 b2' 1 4' b3'",
        "X2": "1! 1 b2' 1 1 b3' 1 1 b5' 4' b3' b2'",
        "C": "1*! - 1* 1* - 1* 1* - 1* 1* - 1*",
    }, rep(riff, 3, "X1+5 X1+5 X1+5 X2+5", 1, riff, 1) + chorus + rep(riff, 2) + chorus + quiet(4) + rep(riff, 2)
            + chorus, vel=86, gate=0.8, volume=94, pan=50)
    shuffle = "p p p q"
    p.voice("bass", PICKBASS, 26, {
        "p": "1 - 1 1 - 1 1 - 1 1 - 1",
        "q": "1 - 1 1 - 1 1 - b5 4 - b3",
    }, rep("_", 4, shuffle, 2, "p+5 p+5 p+5 q+5", 1, shuffle, 1, "p+8 p+10 p p", 2, shuffle, 2, "p+8 p+10 p p", 2,
           shuffle, 3, "p+8 p+10 p p", 2), vel=106, gate=0.8, volume=115)
    chords = {
        "hM": "1M - - - - - - - - - - -", "hm": "1m - - - - - - - - - - -",          # held
        "sM": ". . . 1M - . . . . 1M - .", "sm": ". . . 1m - . . . . 1m - .",          # on two and four
    }
    over = rep("Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8", 1)
    p.voice("organ", ORGAN, 62, chords | ENGINE_OVER_RIFF_12,
            quiet(20) + rep("hM-4 hM-2 hm hm", 2) + [f"{q}+12" for q in over] + rep("sM-4 sM-2 sm sm", 2) + quiet(4)
            + [f"{q}+24" for q in over] + rep("sM-4 sM-2 sm sm", 2), vel=80, gate=0.9, volume=96, pan=74, reverb=50)
    sung = rep("S1 S2 S3 S4 S5 S6 S7 S8", 1)
    p.voice("brass", SYNBRASS, 62, ENGINE_CHORUS_12, quiet(20) + sung + quiet(28) + sung, vel=90, gate=0.97,
            volume=98, pan=56, reverb=50)
    p.voice("lead", OVERDRIVE, 62, ENGINE_CHORUS_12, quiet(36) + sung + quiet(12) + sung, vel=88, gate=0.97,
            volume=94, pan=40, reverb=60)
    p.drums({
        "h": {RIDE: "x.xx.xx.xx.x"},
        "a": {KICK: "x....xx.....", SNARE: "...x.....x..", HAT: "X.xX.xX.xX.x"},
        "f": {KICK: "x....x......", SNARE: "...x........", TOM2: "......x.x...", TOM4: ".........x.x",
              HAT: "X.xX.x......"},
        "c": {CRASH: "x...........", KICK: "x.....x.....", SNARE: "...x.....x..", RIDE: "x.xx.xx.xx.x"},
        "r": {KICK: "x.....x.....", SNARE: "...x.....x..", RIDE: "x.xx.xx.xx.x"},
    }, rep("h", 4, "a a a f", 4, "c r r f", 2, "a a a f", 2, "c r r f", 2, "a a a f", 3, "c r r f", 2), vel=96)
    return p


def engine_machine():
    """C, 140 a minute. Paradox Engine as a machine: its riff shared out between two synths, so that only together
    are they the riff note for note. A synth bass hammers the key note and leaves the gaps; a square wave two
    octaves up plays only the hidden notes into them, as a line of its own. Four on the floor, a clap on two and
    four, an open hat on the off-beats. A saw lead has both tunes; in the chorus a space voice holds the triads
    under it, and from the second chorus a distorted guitar holds the fifths: the band coming into the machine."""
    p = Piece("Paradox Engine, Machine", 140)
    quiet = lambda bars: rep("_", bars)
    hammer = "b b b bb"
    # 64 bars: 4 of the hammer alone; verse 8, the 4th and home 8; chorus; verse; chorus; 4 of the hidden notes
    # alone; verse; chorus
    p.voice("synth bass", SYNBASS1, 36, {
        "b": "1 1 . 1 1 . 1 1 . 1 1 . 1 . 1 1",
        "bb": "1 1 . 1 1 . 1 1 . 1 1 . 1 . . 1",
    }, rep(hammer, 3, "b+5 b+5 b+5 bb+5", 1, hammer, 1, "b+8 b+10 b b", 2, hammer, 2, "b+8 b+10 b b", 2, "_", 4,
           hammer, 2, "b+8 b+10 b b", 2), vel=100, gate=0.7, volume=112)
    hidden = "h1 h1 h1 h2"
    p.voice("square", SQUARE, 48, {
        "h1": ". . b2' . . b3' . . b2' . . 4' . b3' . .",
        "h2": ". . b2' . . b3' . . b5' . . 4' . b3' b2' .",
    }, rep("_", 4, hidden, 2, "h1+5 h1+5 h1+5 h2+5", 1, hidden, 1, "_", 8, hidden, 2, "_", 8, hidden, 3, "_", 8),
            vel=86, gate=0.9, volume=88, pan=70, reverb=40)
    tunes = ENGINE_OVER_RIFF | ENGINE_CHORUS | {"R" + k[1:]: v for k, v in ENGINE_OVER_RIFF_2.items()} | {
        "T" + k[1:]: v for k, v in ENGINE_CHORUS_2.items()}
    p.voice("saw lead", SAW, 72, tunes,                                  # the chorus tune an octave down from its root
            rep("_", 20, "S1-12 S2-12 S3-12 S4-12 S5-12 S6-12 S7-12 S8-12", 1, "Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8", 1,
                "T1-12 T2-12 T3-12 T4-12 T5-12 T6-12 T7-12 T8-12", 1, "_", 4, "R1 R2 R3 R4 R5 R6 R7 R8", 1,
                "S1-12 S2-12 S3-12 S4-12 S5-12 S6-12 S7-12 S8-12", 1), vel=92, gate=0.95, volume=100, pan=56,
            reverb=50)
    pads = rep("M+8 M+10 m m", 2)
    p.voice("space voice", SPACEVOICE, 48, {k: f"1{k} - - - - - - - - - - - - - - -" for k in "mM"},
            quiet(20) + pads + quiet(8) + pads + quiet(12) + pads, vel=70, gate=1.0, volume=82, pan=40, reverb=70)
    p.voice("guitar", DISTORTION, 36, {"H": "1*! - - - - - - - 1* - - - 1* - 1* -"},
            quiet(36) + rep("H+8 H+10 H H", 2) + quiet(12) + rep("H+8 H+10 H H", 2), vel=86, gate=0.8, volume=90,
            pan=30)
    floor, clap, off = "x...x...x...x...", "....x.......x...", "..x...x...x...x."
    p.drums({
        "h": {HAT: "x.x.x.x.x.x.x.x."},
        "a": {KICK: floor, CLAP: clap, OHAT: off},
        "f": {KICK: floor, CLAP: clap, OHAT: "..x...x...x.....", SNARE: "..........x.xxxx"},
        "c": {CRASH: "x...............", KICK: floor, CLAP: clap, SNARE: clap, OHAT: off},
        "r": {KICK: floor, CLAP: clap, SNARE: clap, OHAT: off},
        "k": {KICK: floor},
    }, rep("h", 4, "a a a f", 4, "c r r f", 2, "a a a f", 2, "c r r f", 2, "k", 4, "a a a f", 2, "c r r f", 2),
            vel=96)
    return p


def engine_upside_down():
    """A, 138 a minute. Paradox Engine turned over: the hammered key note is on top, a muted guitar on that one A
    all through, verses and choruses alike, with gaps where the hidden notes were; the hidden notes are below it as
    a heavy riff, picked bass and a distorted guitar an octave over it in fifths, each note held until the next, the
    kick drum on them. In the chorus bass and guitar keep that rhythm on the chord's root. Synth brass has the tune
    over the riff; an overdriven lead with strings has the chorus tune, the brass with it the third time."""
    p = Piece("Paradox Engine, Upside Down", 138)
    quiet = lambda bars: rep("_", bars)
    riff = "U1 U1 U1 U2"
    chorus = "C-4 C-2 C C"                                     # flat 6th, flat 7th, home, home: all below the A
    low = {
        "U1": "1! - b2 - - b3 - - b2 - - 4 - b3 - -",
        "U2": "1! - b2 - - b3 - - b5 - - 4 - b3 b2 -",
        "C": "1! - 1 - - 1 - - 1 - - 1 - 1 - -",
    }
    # 64 bars: 4 of the one note; verse 8, the 4th (a fifth down, so the A stays on top) and home 8; chorus; verse;
    # chorus; 4 without the guitar; verse; chorus
    form = rep(riff, 2, "U1-7 U1-7 U1-7 U2-7", 1, riff, 1, chorus, 2, riff, 2, chorus, 2)
    p.voice("bass", PICKBASS, 33, low, quiet(4) + form + rep(riff, 1) + rep(riff, 2, chorus, 2), vel=106, gate=0.95,
            volume=115)
    p.voice("guitar", DISTORTION, 45, {k: re.sub(r"(b?[1-7])", r"\1^", v) for k, v in low.items()},
            quiet(4) + form + quiet(4) + rep(riff, 2, chorus, 2), vel=86, gate=0.95, volume=94, pan=44)
    p.voice("the one note", MUTED, 57, {"m": "1 1 . 1 1 . 1 1 . 1 1 . 1 . 1 1"}, rep("m", 64), vel=84, gate=0.6,
            volume=92, pan=84)
    tunes = ENGINE_OVER_RIFF | ENGINE_CHORUS | {"R" + k[1:]: v for k, v in ENGINE_OVER_RIFF_2.items()} | {
        "T" + k[1:]: v for k, v in ENGINE_CHORUS_2.items()}
    sung = rep("S1 S2 S3 S4 S5 S6 S7 S8", 1)
    p.voice("brass", SYNBRASS, 69, tunes,                                # the third chorus with the lead, in unison
            rep("_", 28, "Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8", 1, "_", 12, "R1 R2 R3 R4 R5 R6 R7 R8", 1,
                "S1-12 S2-12 S3-12 S4-12 S5-12 S6-12 S7-12 S8-12", 1), vel=88, gate=0.97, volume=94, pan=70, reverb=50)
    p.voice("lead", OVERDRIVE, 57, tunes, quiet(20) + sung + rep("_", 8, "T1 T2 T3 T4 T5 T6 T7 T8", 1, "_", 12) + sung,
            vel=94, gate=0.97, volume=102, pan=56, reverb=60)
    pads = rep("M-4 M-2 m m", 2)
    p.voice("strings", STRINGS, 57, {k: f"1{k} - - - - - - - - - - - - - - -" for k in "mM"},
            quiet(20) + pads + quiet(8) + pads + quiet(12) + pads, vel=62, gate=1.0, volume=76, pan=36, reverb=60)
    accents = "x.x..x..x..x.x.."
    p.drums({
        "h": {HAT: "x.x.x.x.x.x.x.x."},
        "a": {KICK: accents, SNARE: "....x.......x...", HAT: "X.x.X.x.X.x.X.x."},
        "f": {KICK: "x.x..x..x.......", SNARE: "....x.....x.xx..", TOM2: "..............x.", TOM4: "...............x",
              HAT: "X.x.X.x.X......."},
        "c": {CRASH: "x...............", KICK: accents, SNARE: "....x.......x...", RIDE: "x.x.x.x.x.x.x.x."},
        "r": {KICK: accents, SNARE: "....x.......x...", RIDE: "x.x.x.x.x.x.x.x."},
    }, rep("h", 4, "a a a f", 4, "c r r f", 2, "a a a f", 2, "c r r f", 2, "a a a f", 3, "c r r f", 2), vel=98)
    return p


# --- the slow ones on Paradox Engine (three kept of five) ---

def engine_music_box():
    """G, 92 a minute, in three. Paradox Engine as a toy: a slow waltz whose accompaniment is the riff, the key note
    plucked low on the first beat and the hidden notes on a celesta on the second and third. Both tunes cut for
    three beats on a music box; in the chorus (E flat, F, G minor) the root on the first beat and the chord on the
    other two; slow strings from the second verse; in the last chorus a voice sings the chorus tune an octave
    under the music box."""
    p = Piece("Paradox Engine, Music Box", 92, steps=12, per_beat=4, sig=(3, 4))
    waltz = {
        "w1": "1 - - - b2' - - - b3' - - -", "w2": "1 - - - b2' - - - 4' - - -",
        "w3": "1 - - - b3' - - - 1' - - -", "w4": "1 - - - 5 - - - 1' - - -",
        "w5": "1 - - - b5' - - - 4' - - -", "w6": "1 - - - b3' - - - b2' - - -",
    }
    group, chorus = rep("w1 w2 w3 w4 w1 w2 w5 w6", 1), rep("C-4 C-2 c c", 2)        # chorus: flat 6th, flat 7th, home
    # 72 bars: the waltz 8, verse 8, chorus 8, verse 8, chorus 8, the waltz 8, verse 8, chorus 8, the waltz 8
    tunes = {
        "Q1": "1 - - - b2 - 1 - b7, - - -", "Q2": "1 - - - - - - - 5, - b7, -",
        "Q3": "1 - - - b2 - b3 - b2 - - -", "Q4": "1 - - - - - - - - - - -",
        "Q5": "5 - - - b6 - 5 - 4 - - -", "Q6": "b3 - - - 4 - b3 - b2 - - -",
        "Q7": "1 - - - b2 - - - b3 - 4 -", "Q8": "1' - - - - - - - - - - -",
        "S1": "1' - - - b6 - - - 1' - - -", "S2": "2' - - - b7 - - - 2' - - -",
        "S3": "4' - - - b3' - - - 1' - b7 -", "S4": "1' - - - - - - - - - - -",
        "S5": "4' - - - 1' - - - 4' - - -", "S6": "5' - - - 2' - - - 5' - - -",
        "S7": "5' - 4' - b3' - - - 4' - 5' -", "S8": "1'' - - - - - - - - - - -",
    }
    over, sung = "Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8", "S1 S2 S3 S4 S5 S6 S7 S8"
    p.voice("plucked bass", ACBASS, 43, {k: " ".join(v.split()[:4] + ["."] * 8) for k, v in waltz.items()} | {
        "c": "1 - - - . . . . . . . .", "C": "1 - - - . . . . . . . .",
    }, group * 2 + chorus + group + chorus + group * 2 + chorus + group, vel=82, gate=0.9, volume=98)
    # the hidden notes over the music box; the second verse under it (an octave down), while the tune goes up
    p.voice("celesta", CELESTA, 67, {k: " ".join(["."] * 4 + v.split()[4:]) for k, v in waltz.items()} | {
        "c": ". . . . 1,m - - - 1,m - - -", "C": ". . . . 1,M - - - 1,M - - -",
    }, group * 2 + chorus + [w + "-12" for w in group] + chorus + group * 2 + chorus + group, vel=64, gate=1.0,
            volume=84, pan=76, reverb=70)
    p.voice("music box", MUSICBOX, 67, tunes,
            rep("_", 8, over, 1, sung, 1) + [q + "+12" for q in over.split()] + [s + "-12" for s in sung.split()]
            + rep("_", 8, over, 1, sung, 1, "_", 8), vel=88, gate=1.0, volume=104, pan=50, reverb=70)
    p.voice("strings", SLOWSTR, 55, held(12, m="1m", M="1M"),
            rep("_", 24, "m T T T m T T T", 1, "M-4 M-2 m T", 2, "m T T T", 4, "M-4 M-2 m T", 2, "_", 8),
            vel=56, gate=1.0, volume=72, pan=40, reverb=80)
    p.voice("voice", VOICE, 55, tunes, rep("_", 56, sung, 1, "_", 8), vel=68, gate=1.0, volume=86, pan=62,
            reverb=90)
    return p


def engine_night_shift():
    """E, 60 a minute, a 12/8 swing. Paradox Engine after dark, in the manner of Left Luggage and Night Bell. The
    riff is a fretless bass line four bars long with room in it, the hidden notes one or two to a bar in their
    order; an electric piano puts the minor chord softly on two and four; the tune over the riff on a vibraphone.
    In the chorus (C, D, E minor) the bass walks and a muted trumpet has the chorus tune; the second time round
    they change tunes. A closed hat and a side stick, soft."""
    muted_trumpet = 59
    p = Piece("Paradox Engine, Night Shift", 60, steps=12, per_beat=3, sig=(12, 8))
    group, walk = rep("n1 n2 n3 n4", 1), rep("Wa+8 Wa+10 Wm+12 Wd+12", 2)          # walk: flat 6th, flat 7th, home
    # 44 bars: the bass alone 4, verse 8, chorus 8, the riff 4, verse 8, chorus 8, the bass alone 4
    p.voice("fretless", FRETLESS, 28, {
        "n1": "1 - . 1 . 1 b2' - . 1 . 1", "n2": "b3' - . 1 . 1 b2' - . 1 . 1",
        "n3": "4' - . 1 . 1 b3' - . 1 . 1", "n4": "1 - . 1 . 1 b5' - 4' b3' - b2'",
        "Wa": "1 - - 3 - - 5 - - 3 - -", "Wm": "1 - - b3 - - 5 - - b3 - -",
        "Wd": "5 - - b3 - - 1 - - 5, - -",                                      # down, to step up to the flat 6th
    }, group * 3 + walk + group * 3 + walk + group, vel=98, gate=0.9, volume=112)
    chords = rep("E-4 E-2 e e", 2)
    p.voice("electric piano", EPIANO, 52, {
        "e": ". . . 1m - . . . . 1m - .", "E": ". . . 1M - . . . . 1M - .",
    }, rep("_", 4, "e", 8) + chords + rep("e", 12) + chords + rep("_", 4), vel=58, gate=1.0, volume=78, pan=44,
            reverb=60)
    tunes = ENGINE_OVER_RIFF_12 | ENGINE_CHORUS_12
    over, sung = "Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8", "S1 S2 S3 S4 S5 S6 S7 S8"
    p.voice("vibraphone", VIBES, 64, tunes, rep("_", 4, over, 1, "_", 20, sung, 1, "_", 4), vel=84, gate=1.0,
            volume=96, pan=70, reverb=70)
    p.voice("muted trumpet", muted_trumpet, 52, tunes,
            rep("_", 12, sung, 1, "_", 4) + [q + "+12" for q in over.split()] + rep("_", 12), vel=86, gate=0.95,
            volume=98, pan=56, reverb=70)
    p.drums({
        "h": {HAT: "o.oo.oo.oo.o"},
        "a": {HAT: "o.oo.oo.oo.o", STICK: "...x.....x.."},
    }, rep("h", 4, "a", 36, "h", 4), vel=74, volume=86)
    return p


def engine_piano():
    """D, 63 a minute. Paradox Engine on a piano alone, a cello later. The left hand has the riff at a quarter of
    its speed, the hammered note opened into key note and fifth, the hidden notes on the riff's own places; the
    right hand the tune over the riff. In the chorus (B flat, C, D minor) the left hand breaks the chords in eighths
    and the right hand has the chorus tune; the second time the tunes are walked through, the verse an octave
    higher with the cello on the hidden notes as one long line, the chorus in octaves with the cello on the roots."""
    p = Piece("Paradox Engine, Piano", 63)
    group, broken = rep("a b a b a b a d", 1), rep("M-4 M-2 m m", 2)               # broken: flat 6th, flat 7th, home
    # 36 bars: the left hand alone 4, verse 8, chorus 8, verse 8 (the cello in), chorus 8 (in octaves)
    p.voice("left hand", PIANO, 38, {
        "a": "1 - 5 - b2' - 1 - 5 - b3' - 1 - 5 -",
        "b": "b2' - 1 - 5 - 4' - 1 - b3' - 1 - 5 -",
        "d": "b5' - 1 - 5 - 4' - 1 - b3' - b2' - 1 -",
        "M": "1 - 5 - 1' - 3' - 5' - 3' - 1' - 5 -",
        "m": "1 - 5 - 1' - b3' - 5' - b3' - 1' - 5 -",
    }, rep("a b a d", 1) + group + broken + group + broken, vel=70, gate=1.0, volume=90, pan=50, reverb=60)
    tunes = (ENGINE_OVER_RIFF | {k.replace("Q", "W"): v for k, v in ENGINE_OVER_RIFF_2.items()}
             | ENGINE_CHORUS | {k.replace("S", "T"): v for k, v in ENGINE_CHORUS_2.items()})
    walked = "T1 T2 T3 T4 T5 T6 T7 T8"
    p.voice("right hand", PIANO, 62, tunes,
            rep("_", 4, "Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8", 1, "S1 S2 S3 S4 S5 S6 S7 S8", 1, "W1+12 W2+12 W3+12 W4+12 "
                "W5+12 W6+12 W7+12 W8+12", 1, walked, 1), vel=82, gate=0.97, volume=100, pan=70, reverb=60)
    p.voice("right hand, octave", PIANO, 74, tunes, rep("_", 28, walked, 1), vel=70, gate=0.97, volume=88, pan=78,
            reverb=60)
    p.voice("cello", CELLO, 62, held(d="1", e="b2", f="b3", g="4"),            # D, E flat, F, E flat, G, F, E flat, D
            rep("_", 20, "d e f e g f e d", 1, "d-4 d-2 d T", 2), vel=72, gate=1.0, volume=88, pan=40, reverb=80)
    return p


# ---------------------------------------------------------------------------------------------------------------------
# Paradox Engine's riff and tunes on the harmony of three other pieces, 2026-11-26 (see the top): five of each.
#
# 1. On Vadim's sketch distant_galaxy_theme (its chords: home minor; the same chord a semitone lower; home with no
#    third; the 4th minor; then the flat 3rd over a bass on the 5th, the 5th minor, the flat 6th, and the 5th
#    augmented becoming major). VERSE, 16 bars, his first four chords four bars each: the Engine's riff on the key
#    note, the whole riff a semitone lower, the riff with no third in it (its flat 3rd and 4th a step higher) on the
#    key note, the riff on the 4th. The tune over it is the first half of the Engine's (Q1 to Q4) four times, at
#    those levels: at home, a semitone lower, a fifth higher (where it has no third in it either), on the 4th.
#    CHORUS, 8 bars, his other four chords a bar each, twice, the bass on the 5th, 5th, flat 6th, 5th: the Engine's
#    chorus tune with its rhythm and shape kept and its notes moved onto these chords (GALAXY_CHORUS); in the last
#    bar of four the flat 3rd stays over the augmented chord and falls to the 2nd as it becomes major, as in his
#    sketch.

GALAXY_VERSE_LEVELS = (0, -1, 7, 5)             # Q1 to Q4 at each, four bars each
GALAXY_CHORUS = {
    "D1": "5' - - - - - - - b3' - - - 5' - - -",             # over the flat 3rd chord, the 5th in the bass
    "D2": "b7' - - - - - - - 5' - - - b7' - - -",            # over the 5th minor
    "D3": "4' - - - b3' - - - 1' - - - - - b7 -",            # over the flat 6th (the Engine's own third bar)
    "D4": "b3' - - - - - - - 2' - - - - - - -",              # over the 5th augmented, then major
    "D5": "b3'' - - - - - - - b7' - - - b3'' - - -",
    "D6": "2'' - - - - - - - b7' - - - 2'' - - -",
    "D7": "b3'' - - - b2'' - - - 1'' - - - b2'' - b3'' -",
    "D8": "b3'' - - - - - - - 2'' - - - - - - -",
}

# 2. On Vadim's sketch garmonic (a note held on top, the 5th, while the two notes under it slip down a semitone one
#    after the other, so home minor becomes the major chord on the 5th; then home minor over its flat 3rd, the major
#    chord on the major 7th with that flat 3rd kept, the same augmented as the 5th comes back, the minor chord on
#    the major 3rd, and home with the 5th kept). VERSE, 8 bars, his first move twice: two bars of the Engine's riff
#    at home, in the second of them its last flat 3rd slipped to the 2nd; then two bars of the whole riff a semitone
#    lower. The Engine's tune slips with it (GARMONIC_VERSE). CHORUS, 8 bars, his other chords: bass on the flat
#    3rd, flat 3rd, 7th, 7th, 3rd, 3rd, home, home; the Engine's chorus tune, rhythm and shape kept, on these
#    chords (GARMONIC_CHORUS). The Engine's hammered note is his held note: the 5th, on TOP, through the verse; the
#    flat 3rd for the chorus's first four bars (the note those chords keep), the 5th again for its last four.

GARMONIC_VERSE = "Q1 Q2 Q3-1 Q4-1 Q5 Q6g Q7-1 Q8-1"         # with ENGINE_OVER_RIFF | GARMONIC_OVER_RIFF
GARMONIC_OVER_RIFF = {"Q6g": "b3 - - - - - 4 - 2 - - - 1 - - -"}       # Q6, its second half slipped
GARMONIC_CHORUS = {
    "T1": "b3' - - - - - - - 1' - - - b3' - - -",            # home minor over the flat 3rd
    "T2": "5' - - - - - - - b3' - - - 5' - - -",
    "T3": "b5' - - - - - - - b3' - - - b5' - - -",           # the major chord on the 7th
    "T4": "5' - - - - - - - - - - - . . . .",                # the same augmented: the 5th comes back
    "T5": "7' - - - - - - - 5' - - - 7' - - -",              # the minor chord on the major 3rd
    "T6": "3'' - - - - - - - 7' - - - 3'' - - -",
    "T7": "b3'' - - - 2'' - - - 1'' - - - 2'' - b3'' -",     # home
    "T8": "1'' - - - - - - - - - - - - - - -",
}

# 3. On the harmony of O Magnum Mysterium as Mysterium II has it (one major key, plain chords, the third in the bass
#    and the bass walking down by step, seconds and sixths added and left, endings from the fourth chord to home).
#    The Engine's tunes are not changed by a note. Its key note is heard as the THIRD of a major key a major third
#    lower (D as the third of B flat), where its Phrygian scale is that key's major scale: the flat 2nd that grinds
#    against the key note in the Engine is here the fourth leaning on the third. Under both tunes the same bass, a
#    bar a note, walking down the major scale from its third to its third (degrees 3 2 1 7 6 5 4 3). Chords, verse:
#    I, V, I, V, IV, I, IV, I. Chorus: I, II major (the one chord from outside the key, for the tune's raised fourth),
#    I, V, vi, V, IV, I. A voice with a tune has its root a major third above the key's.

MYSTERIUM_BASS = "3 2 1 7, 6, 5, 4, 3,"                     # a bar each, degrees of the major key
MYSTERIUM_VERSE = "I V I V IV I IV I"
MYSTERIUM_CHORUS = "I II I V vi V IV I"


# --- on Distant Galaxy's harmony: the five functions go between this line and the next marker ---

GALAXY_RIFF = {                                 # the Engine's riff, and the same with no third (flat 3rd, 4th a step up)
    "X1": "1! 1 b2' 1 1 b3' 1 1 b2' 1 1 4' 1 b3' 1 1",
    "X2": "1! 1 b2' 1 1 b3' 1 1 b5' 1 1 4' 1 b3' b2' 1",
    "N1": "1! 1 b2' 1 1 4' 1 1 b2' 1 1 5' 1 4' 1 1",
    "N2": "1! 1 b2' 1 1 4' 1 1 b5' 1 1 5' 1 4' b2' 1",
}
GALAXY_RIFF_12 = {
    "X1": "1! 1 b2' 1 1 b3' 1 1 b2' 1 4' b3'",
    "X2": "1! 1 b2' 1 1 b3' 1 1 b5' 4' b3' b2'",
    "N1": "1! 1 b2' 1 1 4' 1 1 b2' 1 5' 4'",
    "N2": "1! 1 b2' 1 1 4' 1 1 b5' 5' 4' b2'",
}
GALAXY_VERSE_RIFF = "X1 X1 X1 X2 X1-1 X1-1 X1-1 X2-1 N1 N1 N1 N2 X1+5 X1+5 X1+5 X2+5"
GALAXY_CHORUS_12 = {                            # GALAXY_CHORUS cut for twelve as ENGINE_CHORUS_12 is cut
    "D1": "5' - - - - - b3' - - 5' - -",
    "D2": "b7' - - - - - 5' - - b7' - -",
    "D3": "4' - - b3' - - 1' - - - - b7",
    "D4": "b3' - - - - - 2' - - - - -",
    "D5": "b3'' - - - - - b7' - - b3'' - -",
    "D6": "2'' - - - - - b7' - - 2'' - -",
    "D7": "b3'' - - b2'' - - 1'' - - b2'' - b3''",
    "D8": "b3'' - - - - - 2'' - - - - -",
}
GALAXY_SUNG = "D1 D2 D3 D4 D5 D6 D7 D8"


def galaxy_tune(names="Q1 Q2 Q3 Q4", shift=0):
    """The verse tune's 16 bars: the four bars `names` at each of GALAXY_VERSE_LEVELS in turn, all moved by `shift`."""
    return [n + (f"{level + shift:+d}" if level + shift else "") for level in GALAXY_VERSE_LEVELS for n in names.split()]


def galaxy_engine_band():
    """A, 132 a minute. The Doom band, made as Distant Galaxy, Fast is: an overdriven guitar and a picked bass play
    the Engine's riff on Vadim's first four chords, four bars each (home, a semitone lower, home with no third, the
    4th). From the second verse a square wave holds his top line (E, D sharp, E, F) and synth brass has the first
    half of the Engine's tune at the four levels; the third time the tune is walked through and a rock organ stabs
    the chords on two and four. Chorus, his other four chords: guitar and bass on the bass notes (E, E, F, E), held
    fifths where the chord allows one, strings on the chords, an overdriven lead with the chorus tune."""
    p = Piece("Galaxy Engine, Band", 132)
    quiet = lambda bars: rep("_", bars)
    verse = GALAXY_VERSE_RIFF.split()
    # 80 bars: 4 in; verse 16, chorus 8; verse 16 (top line, tune), chorus; 4 of the bass alone; verse 16 (top line,
    # the tune walked through, organ), chorus
    p.voice("guitar", OVERDRIVE, 45, GALAXY_RIFF | {
        "C": "1^! - - 1^ - - 1^ - - - 1^ - 1^ - - -",
        "U": "1! - - 1 - - 1 - - - 1 - 1 - - -",           # the bass note alone: its fifth would rub on the chord
        "V": "1! - - 1 - - 1 - - - 1^ - 1^ - - -",         # alone under the augmented half, the fifth once major
    }, rep("X1 X1 X1 X2", 1) + (verse + rep("U+7 C+7 C+8 V+7", 2)) * 2 + quiet(4) + verse
            + rep("U+7 C+7 C+8 V+7", 2), vel=86, gate=0.8, volume=94, pan=50)
    low = rep("c+7 c+7 c+8 c+7", 2)
    p.voice("bass", PICKBASS, 33, GALAXY_RIFF | {"c": "1 . . 1 . . 1 . . . 1 . 1 . . ."},
            quiet(4) + (verse + low) * 2 + rep("X1 X1 X1 X2", 1) + verse + low, vel=106, gate=0.8, volume=115)
    pads = rep("M+3 m+7 M+8 A+7", 2)
    p.voice("strings", STRINGS, 45, {k: f"1{k} - - - - - - - - - - - - - - -" for k in "mM"} | {
        "A": "1a - - - - - - - 1M - - - - - - -",
    }, quiet(20) + pads + quiet(16) + pads + quiet(20) + pads, vel=64, gate=1.0, volume=78, pan=40, reverb=60)
    sung = rep(GALAXY_SUNG, 1)
    p.voice("lead", OVERDRIVE, 57, GALAXY_CHORUS, quiet(20) + sung + quiet(16) + sung + quiet(20) + sung, vel=94,
            gate=0.97, volume=98, reverb=60)
    tunes = ENGINE_OVER_RIFF | {"W" + k[1:]: v for k, v in ENGINE_OVER_RIFF_2.items()}
    p.voice("brass", SYNBRASS, 69, tunes, quiet(28) + galaxy_tune() + quiet(12) + galaxy_tune("W1 W2 W3 W4")
            + quiet(8), vel=96, gate=0.97, volume=100, pan=72, reverb=50)
    slip = rep("e T T T s T T T e T T T f T T T", 1)
    p.voice("square", SQUARE, 69, held(e="5", s="b5", f="b6"), quiet(28) + slip + quiet(12) + slip + quiet(8),
            vel=66, gate=1.0, volume=74, pan=56, reverb=50)
    stabs = rep("s", 4, "s-1", 4, "o", 4, "s+5", 4)                    # on two and four, between the hidden notes
    p.voice("organ", ORGAN, 57, {
        "s": ". . . . 1m . . . . . . . 1m . . .", "o": ". . . . 1^ . . . . . . . 1^ . . .",
    }, quiet(56) + stabs + quiet(8), vel=64, gate=0.7, volume=76, pan=84)
    p.drums(FAST_DRUMS, rep("h", 4, "a a a f", 4, "c r r f", 2, "a a a f", 4, "c r r f", 2, "h", 4, "a a a f", 4,
                            "c r r f", 2), vel=98)
    return p


def galaxy_engine_machine():
    """G, 140 a minute. Made as Paradox Engine, Machine is: the riff shared out between a synth bass, which hammers
    the key note and leaves the gaps, and a square wave two octaves up with only the hidden notes, on Vadim's first
    four chords (home, a semitone lower, home with no third, the 4th). Four on the floor, a clap, an open hat off the
    beat. A saw lead has both tunes; a space voice holds the chord in the verse (minor, minor a semitone lower, a bare
    fifth, minor on the 4th) and his other four chords in the chorus, where the synth bass hammers the bass notes
    (D, D, E flat, D); from the second chorus a distorted guitar holds them too."""
    p = Piece("Galaxy Engine, Machine", 140)
    quiet = lambda bars: rep("_", bars)
    # 80 bars: 4 of the hammer alone; verse 16, chorus 8; verse 16 (the tune), chorus; 4 of the hidden notes alone;
    # verse 16 (the tune walked through), chorus
    verse = rep("b b b bb b-1 b-1 b-1 bb-1 b b b bb b+5 b+5 b+5 bb+5", 1)
    chorus = rep("b+7 b+7 b+8 b+7", 2)
    p.voice("synth bass", SYNBASS1, 31, {
        "b": "1 1 . 1 1 . 1 1 . 1 1 . 1 . 1 1",
        "bb": "1 1 . 1 1 . 1 1 . 1 1 . 1 . . 1",
    }, rep("b b b bb", 1) + (verse + chorus) * 2 + quiet(4) + verse + chorus, vel=96, gate=0.7, volume=104)
    hidden = rep("h1 h1 h1 h2 h1-1 h1-1 h1-1 h2-1 n1 n1 n1 n2 h1+5 h1+5 h1+5 h2+5", 1)
    p.voice("square", SQUARE, 43, {
        "h1": ". . b2' . . b3' . . b2' . . 4' . b3' . .",
        "h2": ". . b2' . . b3' . . b5' . . 4' . b3' b2' .",
        "n1": ". . b2' . . 4' . . b2' . . 5' . 4' . .",
        "n2": ". . b2' . . 4' . . b5' . . 5' . 4' b2' .",
    }, quiet(4) + hidden + quiet(8) + hidden + quiet(8) + rep("h1 h1 h1 h2", 1) + hidden + quiet(8), vel=86,
            gate=0.9, volume=88, pan=70, reverb=40)
    tunes = ENGINE_OVER_RIFF | {"R" + k[1:]: v for k, v in ENGINE_OVER_RIFF_2.items()} | GALAXY_CHORUS
    sung = [d + "-12" for d in GALAXY_SUNG.split()]                     # the chorus tune an octave down from its root
    p.voice("saw lead", SAW, 67, tunes, quiet(20) + sung + galaxy_tune() + sung + quiet(4) + galaxy_tune("R1 R2 R3 R4")
            + sung, vel=100, gate=0.95, volume=108, pan=56, reverb=50)
    pads = held(m="1m", o="1^", M="1M") | {"A": "1a - - - - - - - 1M - - - - - - -"}
    verse_pad, chorus_pad = rep("m T T T m-1 T T T o T T T m+5 T T T", 1), rep("M+3 m+7 M+8 A+7", 2)
    p.voice("space voice", SPACEVOICE, 43, pads, quiet(20) + chorus_pad + verse_pad + chorus_pad + quiet(4) + verse_pad
            + chorus_pad, vel=68, gate=1.0, volume=80, pan=40, reverb=70)
    p.voice("guitar", DISTORTION, 43, {
        "H": "1*! - - - - - - - 1* - - - 1* - 1* -",
        "U": "1! - - - - - - - 1 - - - 1 - 1 -",           # the bass note alone: its fifth would rub on the chord
        "V": "1! - - - - - - - 1* - - - 1* - 1* -",        # alone under the augmented half
    }, quiet(44) + rep("U+7 H+7 H+8 V+7", 2) + quiet(20) + rep("U+7 H+7 H+8 V+7", 2), vel=86, gate=0.8, volume=90,
            pan=30)
    floor, clap, off = "x...x...x...x...", "....x.......x...", "..x...x...x...x."
    p.drums({
        "h": {HAT: "x.x.x.x.x.x.x.x."},
        "a": {KICK: floor, CLAP: clap, OHAT: off},
        "f": {KICK: floor, CLAP: clap, OHAT: "..x...x...x.....", SNARE: "..........x.xxxx"},
        "c": {CRASH: "x...............", KICK: floor, CLAP: clap, SNARE: clap, OHAT: off},
        "r": {KICK: floor, CLAP: clap, SNARE: clap, OHAT: off},
        "k": {KICK: floor},
    }, rep("h", 4, "a a a f", 4, "c r r f", 2, "a a a f", 4, "c r r f", 2, "k", 4, "a a a f", 4, "c r r f", 2),
            vel=96)
    return p


def galaxy_engine_shuffle():
    """D, a 12/8 shuffle, 132 a minute. Made as Paradox Engine, Shuffle is: the riff in triplets on an overdriven
    guitar, on Vadim's first four chords (home, a semitone lower, home with no third, the 4th); the bass plays the
    shuffle on each chord's root and joins the guitar's turn in every fourth bar. A rock organ is the main voice
    and has the verse tune at the four levels, the third time with synth brass. Chorus, his other four chords: the
    guitar and bass on the bass notes (A, A, B flat, A), the organ on the chords, held the first time and on two and
    four after; synth brass has the chorus tune, the second time a lead guitar, the third time both."""
    p = Piece("Galaxy Engine, Shuffle", 132, steps=12, per_beat=3, sig=(12, 8))
    quiet = lambda bars: rep("_", bars)
    verse = GALAXY_VERSE_RIFF.split()
    chorus = rep("U+7 C+7 C+8 V+7", 2)
    # 80 bars: 4 in; verse 16, chorus 8; verse 16 (the tune), chorus; 4 of the bass alone; verse 16 (the tune, with
    # the brass), chorus
    p.voice("guitar", OVERDRIVE, 38, GALAXY_RIFF_12 | {
        "C": "1*! - 1* 1* - 1* 1* - 1* 1* - 1*",
        "U": "1! - 1 1 - 1 1 - 1 1 - 1",                   # the bass note alone: its fifth would rub on the chord
        "V": "1! - 1 1 - 1 1* - 1* 1* - 1*",               # alone under the augmented half
    }, rep("X1 X1 X1 X2", 1) + (verse + chorus) * 2 + quiet(4) + verse + chorus, vel=86, gate=0.8, volume=94, pan=50)
    shuffle = rep("p p p q p-1 p-1 p-1 q-1 p p p r p+5 p+5 p+5 q+5", 1)
    low = rep("p+7 p+7 p+8 p+7", 2)
    p.voice("bass", PICKBASS, 26, {
        "p": "1 - 1 1 - 1 1 - 1 1 - 1",
        "q": "1 - 1 1 - 1 1 - b5 4 - b3",
        "r": "1 - 1 1 - 1 1 - b5 5 - 4",                   # the turn with no third
    }, quiet(4) + (shuffle + low) * 2 + rep("p p p q", 1) + shuffle + low, vel=106, gate=0.8, volume=115)
    chords = {
        "hM": "1M - - - - - - - - - - -", "hm": "1m - - - - - - - - - - -",          # held
        "hA": "1a - - - - - 1M - - - - -",
        "sM": ". . . 1M - . . . . 1M - .", "sm": ". . . 1m - . . . . 1m - .",          # on two and four
        "sA": ". . . 1a - . . . . 1M - .",
    }
    tune = galaxy_tune(shift=24)                                         # the organ's root 50: the tune on 74
    p.voice("organ", ORGAN, 50, chords | ENGINE_OVER_RIFF_12,
            quiet(20) + rep("hM-9 hm-5 hM-4 hA-5", 2) + tune + rep("sM-9 sm-5 sM-4 sA-5", 2) + quiet(4) + tune
            + rep("sM-9 sm-5 sM-4 sA-5", 2), vel=84, gate=0.9, volume=98, pan=74, reverb=50)
    sung = rep(GALAXY_SUNG, 1)
    p.voice("brass", SYNBRASS, 50, ENGINE_OVER_RIFF_12 | GALAXY_CHORUS_12, quiet(20) + sung + quiet(28) + tune + sung,
            vel=88, gate=0.97, volume=96, pan=56, reverb=50)
    p.voice("lead", OVERDRIVE, 50, GALAXY_CHORUS_12, quiet(44) + sung + quiet(20) + sung, vel=90, gate=0.97,
            volume=96, pan=40, reverb=60)
    p.drums({
        "h": {RIDE: "x.xx.xx.xx.x"},
        "a": {KICK: "x....xx.....", SNARE: "...x.....x..", HAT: "X.xX.xX.xX.x"},
        "f": {KICK: "x....x......", SNARE: "...x........", TOM2: "......x.x...", TOM4: ".........x.x",
              HAT: "X.xX.x......"},
        "c": {CRASH: "x...........", KICK: "x.....x.....", SNARE: "...x.....x..", RIDE: "x.xx.xx.xx.x"},
        "r": {KICK: "x.....x.....", SNARE: "...x.....x..", RIDE: "x.xx.xx.xx.x"},
    }, rep("h", 4, "a a a f", 4, "c r r f", 2, "a a a f", 4, "c r r f", 2, "a a a f", 5, "c r r f", 2), vel=96)
    return p


def galaxy_engine_piano():
    """A, 63 a minute. Made as Paradox Engine, Piano is: a piano alone, a cello later. The left hand has the riff
    at a quarter of its speed, four bars to one of Vadim's first four chords (home, a semitone lower, home with no
    third, the 4th); the right hand the first half of the Engine's tune at the four levels. In the chorus the left
    hand breaks his other four chords in eighths over the bass notes (E, E, F, E) and the right hand has the chorus
    tune. The second time the verse tune is walked through, the cello holds his top line (E, D sharp, E, F) and then
    the bass notes, and the chorus tune is in octaves."""
    p = Piece("Galaxy Engine, Piano", 63)
    verse = rep("a b a d a-1 b-1 a-1 d-1 an bn an dn a+5 b+5 a+5 d+5", 1)
    broken = rep("c1 c2 c3 c4", 2)
    # 56 bars: the left hand alone 4, verse 16, chorus 8, the left hand alone 4, verse 16 (the cello in), chorus 8
    p.voice("left hand", PIANO, 45, {
        "a": "1 - 5 - b2' - 1 - 5 - b3' - 1 - 5 -",
        "b": "b2' - 1 - 5 - 4' - 1 - b3' - 1 - 5 -",
        "d": "b5' - 1 - 5 - 4' - 1 - b3' - b2' - 1 -",
        "an": "1 - 5 - b2' - 1 - 5 - 4' - 1 - 5 -",                       # with no third
        "bn": "b2' - 1 - 5 - 5' - 1 - 4' - 1 - 5 -",
        "dn": "b5' - 1 - 5 - 5' - 1 - 4' - b2' - 1 -",
        "c1": "5, - b3 - b7 - b3' - 5' - b3' - b7 - b3 -",               # C over E
        "c2": "5, - 2 - 5 - b7 - 2' - b7 - 5 - 2 -",                     # E minor
        "c3": "b6, - b3 - b6 - b3' - 1' - b3' - b6 - b3 -",              # F: no A under the tune's B flat
        "c4": "5, - b3 - 5 - 7 - 2' - 7 - 5 - 2 -",                      # E augmented, E
    }, rep("a b a d", 1) + verse + broken + rep("a b a d", 1) + verse + broken, vel=70, gate=1.0, volume=90, pan=50,
            reverb=60)
    tunes = ENGINE_OVER_RIFF | {"W" + k[1:]: v for k, v in ENGINE_OVER_RIFF_2.items()} | GALAXY_CHORUS
    sung = [d + "-12" for d in GALAXY_SUNG.split()]                     # the chorus tune on 57, not 69
    p.voice("right hand", PIANO, 69, tunes, rep("_", 4) + galaxy_tune() + sung + rep("_", 4)
            + galaxy_tune("W1 W2 W3 W4") + sung, vel=82, gate=0.97, volume=100, pan=70, reverb=60)
    p.voice("right hand, octave", PIANO, 69, GALAXY_CHORUS, rep("_", 48, GALAXY_SUNG, 1), vel=70, gate=0.97,
            volume=88, pan=78, reverb=60)
    p.voice("cello", CELLO, 45, held(e="5", s="b5", f="b6"),
            rep("_", 32, "e T T T s T T T e T T T f T T T", 1, "e T f e", 2), vel=72, gate=1.0, volume=88, pan=40,
            reverb=80)
    return p


def galaxy_engine_night_shift():
    """E, 60 a minute, a 12/8 swing. Made as Paradox Engine, Night Shift is: the riff a fretless bass line four bars
    long, here four bars to each of Vadim's first four chords (home, a semitone lower, home with no third, the 4th);
    an electric piano puts the chord softly on two and four (a bare fifth where there is no third); a vibraphone has
    the verse tune at the four levels. In the chorus, his other four chords, the bass walks on each chord's notes over
    the bass notes (B, B, C, B) and a muted trumpet has the chorus tune; the second time round they change tunes.
    A closed hat and a side stick, soft."""
    muted_trumpet = 59
    p = Piece("Galaxy Engine, Night Shift", 60, steps=12, per_beat=3, sig=(12, 8))
    verse = rep("n1 n2 n3 n4 n1-1 n2-1 n3-1 n4-1 m1 m2 m3 m4 n1+5 n2+5 n3+5 n4+5", 1)
    walk = rep("w1 w2 w3 w4", 2)
    # 56 bars: the bass alone 4, verse 16, chorus 8, the riff 4, verse 16, chorus 8
    p.voice("fretless", FRETLESS, 28, {
        "n1": "1 - . 1 . 1 b2' - . 1 . 1", "n2": "b3' - . 1 . 1 b2' - . 1 . 1",
        "n3": "4' - . 1 . 1 b3' - . 1 . 1", "n4": "1 - . 1 . 1 b5' - 4' b3' - b2'",
        "m1": "1 - . 1 . 1 b2' - . 1 . 1", "m2": "4' - . 1 . 1 b2' - . 1 . 1",         # with no third
        "m3": "5' - . 1 . 1 4' - . 1 . 1", "m4": "1 - . 1 . 1 b5' - 5' 4' - b2'",
        "w1": "5 - - b7 - - b3' - - b7 - -",                                       # G over B
        "w2": "5 - - b7 - - 2' - - b7 - -",                                        # B minor
        "w3": "b6 - - b3' - - 1' - - b3' - -",                                     # C: no E under the tune's F
        "w4": "5 - - b3' - - 2' - - 7 - -",                                        # B augmented, B
    }, rep("n1 n2 n3 n4", 1) + verse + walk + rep("n1 n2 n3 n4", 1) + verse + walk, vel=98, gate=0.9, volume=112)
    chords = rep("E-9 e-5 E-4 A-5", 2)                                   # below the trumpet
    p.voice("electric piano", EPIANO, 52, {
        "e": ". . . 1m - . . . . 1m - .", "o": ". . . 1^ - . . . . 1^ - .",
        "E": ". . . 1M - . . . . 1M - .", "A": ". . . 1a - . . . . 1M - .",
    }, rep("_", 4, "e e e e e-1 e-1 e-1 e-1 o o o o e+5 e+5 e+5 e+5", 1) + chords
            + rep("e", 4, "e e e e e-1 e-1 e-1 e-1 o o o o e+5 e+5 e+5 e+5", 1) + chords, vel=58, gate=1.0,
            volume=78, pan=44, reverb=60)
    tunes = ENGINE_OVER_RIFF_12 | GALAXY_CHORUS_12
    sung = rep(GALAXY_SUNG, 1)
    p.voice("vibraphone", VIBES, 64, tunes, rep("_", 4) + galaxy_tune() + rep("_", 28) + [d + "-12" for d in sung],
            vel=84, gate=1.0, volume=96, pan=70, reverb=70)
    p.voice("muted trumpet", muted_trumpet, 52, tunes, rep("_", 20) + sung + rep("_", 4) + galaxy_tune(shift=12)
            + rep("_", 8), vel=86, gate=0.95, volume=98, pan=56, reverb=70)
    p.drums({
        "h": {HAT: "o.oo.oo.oo.o"},
        "a": {HAT: "o.oo.oo.oo.o", STICK: "...x.....x.."},
    }, rep("h", 4, "a", 52), vel=74, volume=86)
    return p


# --- on Garmonic's harmony: the five functions go between this line and the next marker ---


# --- on Mysterium's harmony: the five functions go between this line and TRACKS ---

# The chords held as three lines that move by step and keep their common notes, in semitones over the major key note
# (low, middle, top; over B flat 3: I = D4 F4 B flat 4, V = C4 F4 A4, IV = E flat 4 G4 B flat 4, vi = D4 G4 B flat 4,
# II = E4 G4 C5). Their notes taken an octave apart are also each chord's triad.
MYSTERIUM_LINES = {"I": (4, 7, 12), "V": (2, 7, 11), "IV": (5, 9, 12), "vi": (4, 9, 12), "II": (6, 9, 14)}


def mysterium_line(harmony, i, key, start=0, again=False):
    """One of the three held lines (0 low, 1 middle, 2 top) over a list of chord names, a bar each, as bar ->
    {step: pitch} for write(): a note that is the same as the bar before's is held, not struck again (unless
    `again`); nothing before bar `start`."""
    bars, last = [], None
    for b, chord in enumerate(harmony):
        pitch = key + MYSTERIUM_LINES[chord][i]
        bars.append({0: pitch} if again or pitch != last or b == start else {})
        last = pitch
    return bars


def mysterium_engine_choir():
    """B flat, 52 a minute. Paradox Engine's two tunes, not a note changed, with the Engine's D heard as the third of
    B flat major, in the manner of Mysterium II. A contrabass walks down the scale a note a bar, D to D, under verse
    and chorus alike; a warm pad, slow strings and a choir hold the chords as three lines, each keeping its note
    while it can, coming in one after the other in the first verse, which has no tune. Then a horn has the chorus
    tune and a clarinet the verse tune; the second time round both walk their long notes through and a vibraphone
    says each note again a beat later, an octave up; the third time they are plain again."""
    p = Piece("Mysterium Engine, Choir", 52)
    harmony = (MYSTERIUM_VERSE + " " + MYSTERIUM_CHORUS).split() * 3
    walk = [parse(t, 1)[1][0][2][0] for t in MYSTERIUM_BASS.split()] * 6         # semitones over the key, a bar each
    # 48 bars, three times verse and chorus: the bass and the three lines; the horn's chorus; both tunes walked
    # through with the vibraphone after them; both tunes plain
    p.voice("contrabass", CONTRABASS, 46, *write([{0: 46 + w} for w in walk], 46), vel=80, gate=1.0, volume=100)
    for i, (name, program, pan, start) in enumerate((("low line", WARMPAD, 88, 0), ("middle line", SLOWSTR, 36, 2),
                                                     ("top line", VOICE, 58, 4))):
        p.voice(name, program, 58, *write(mysterium_line(harmony, i, 58, start), 58, start=start), vel=64,
                gate=1.0, volume=86, pan=pan, reverb=85)
    tunes = (ENGINE_OVER_RIFF | {k.replace("Q", "W"): v for k, v in ENGINE_OVER_RIFF_2.items()}
             | ENGINE_CHORUS | {k.replace("S", "T"): v for k, v in ENGINE_CHORUS_2.items()})
    over, walked_over = "Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8", "W1 W2 W3 W4 W5 W6 W7 W8"
    sung, walked = "S1 S2 S3 S4 S5 S6 S7 S8", "T1 T2 T3 T4 T5 T6 T7 T8"
    p.voice("clarinet", CLARINET, 74, tunes, rep("_", 16, walked_over, 1, "_", 8, over, 1, "_", 8), vel=86,
            gate=0.97, volume=102, pan=66, reverb=70)
    p.voice("horn", HORN, 62, tunes, rep("_", 8, sung, 1, "_", 8, walked, 1, "_", 8, sung, 1), vel=86, gate=0.97,
            volume=102, pan=46, reverb=70)
    # the vibraphone: each note of the walked tunes a beat later and an octave up, held at most a beat and only
    # while the tune does not sound a semitone from it; a note left shorter than two steps is not said
    said, form = {}, ["_"] * p.bars
    for first, names, root in ((16, walked_over, 74), (24, walked, 62)):
        for b, name in enumerate(names.split(), first):
            events = parse(tunes[name], 16)[1]
            under = [None] * 16
            for s, n, (pitch,), _ in events:
                under[s:s + n] = [pitch] * n
            row = ["."] * 16
            for s, n, (pitch,), _ in events:
                end = s + 4
                while end < min(s + 4 + min(n, 4), 16) and (under[end] is None
                                                             or (under[end] - pitch) % 12 not in (1, 11)):
                    end += 1
                if end - s - 4 >= 2:
                    row[s + 4:end] = [token(root + pitch + 12, 74)] + ["-"] * (end - s - 5)
            said[f"v{b}"], form[b] = " ".join(row), f"v{b}"
    p.voice("vibraphone", VIBES, 74, said, form, vel=66, gate=1.0, volume=84, pan=28, reverb=80)
    return p


def mysterium_engine_piano():
    """B flat, 66 a minute. Paradox Engine's tunes on a piano, with the Engine's D heard as the third of B flat
    major, in the manner of Paradox Engine, Piano. The left hand goes in eighths: the bar's bass note (the scale
    walking down, D to D, a note a bar) and then the notes of the bar's chord above it, up and back. A verse of the
    left hand alone; then the right hand has the verse tune and the chorus tune; the second time both are walked
    through, the chorus in octaves, and a cello comes in with the bass line as long notes."""
    p = Piece("Mysterium Engine, Piano", 66)
    verse, chorus = MYSTERIUM_VERSE.split(), MYSTERIUM_CHORUS.split()
    harmony = verse * 2 + chorus + verse + chorus
    walk = [parse(t, 1)[1][0][2][0] for t in MYSTERIUM_BASS.split()] * 5
    key = 46                                                                    # B flat 2: the bass from D3 to D2
    # 40 bars: the left hand alone 8, verse 8, chorus 8, verse 8 (walked, the cello in), chorus 8 (walked, octaves)
    low, left = {}, {}                          # the bass note let ring through the bar, as under the pedal
    for b, chord in enumerate(harmony):
        bass = key + walk[b]
        triad = {x % 12 for x in MYSTERIUM_LINES[chord]}
        up = [q for q in range(bass + 1, bass + 20) if (q - key) % 12 in triad][:4]
        low[f"n{b}"] = token(bass, key) + " -" * 15
        left[f"n{b}"] = ". . " + " ".join(f"{token(q, key)} -" for q in up + up[2::-1])
    p.voice("left hand, bass", PIANO, key, low, list(low), vel=72, gate=1.0, volume=88, pan=50, reverb=60)
    p.voice("left hand", PIANO, key, left, list(left), vel=66, gate=1.0, volume=88, pan=50, reverb=60)
    tunes = (ENGINE_OVER_RIFF | {k.replace("Q", "W"): v for k, v in ENGINE_OVER_RIFF_2.items()}
             | ENGINE_CHORUS | {k.replace("S", "T"): v for k, v in ENGINE_CHORUS_2.items()})
    walked = "T1 T2 T3 T4 T5 T6 T7 T8"
    p.voice("right hand", PIANO, 62, tunes,                                     # the verse tune an octave up
            rep("_", 8) + [f"Q{i}+12" for i in range(1, 9)] + rep("S1 S2 S3 S4 S5 S6 S7 S8", 1)
            + [f"W{i}+12" for i in range(1, 9)] + rep(walked, 1), vel=84, gate=0.97, volume=100, pan=70, reverb=60)
    p.voice("right hand, octave", PIANO, 74, tunes, rep("_", 32, walked, 1), vel=70, gate=0.97, volume=88, pan=78,
            reverb=60)
    p.voice("cello", CELLO, key, *write([{0: key + w} for w in walk], key, start=24), vel=70, gate=1.0, volume=86,
            pan=40, reverb=80)
    return p


def mysterium_engine_music_box():
    """C, 96 a minute, in three. Paradox Engine's tunes as a slow waltz in C major, the Engine's key note E heard as
    its third, in the manner of Paradox Engine, Music Box. A plucked bass has the bar's bass note on the first beat
    (the scale walking down, E to E, a note a bar), a celesta the bar's chord on the second and third; both tunes
    cut for three beats on a music box. A verse of the waltz alone first; slow strings hold the chords from the
    second verse; a verse without the tune halfway; in the last chorus a voice has the chorus tune an octave under
    the music box."""
    p = Piece("Mysterium Engine, Music Box", 96, steps=12, per_beat=4, sig=(3, 4))
    verse, chorus = MYSTERIUM_VERSE.split(), MYSTERIUM_CHORUS.split()
    harmony = verse * 2 + chorus + verse + chorus + verse * 2 + chorus + verse + chorus
    walk = [parse(t, 1)[1][0][2][0] for t in MYSTERIUM_BASS.split()] * 10
    # 80 bars: the waltz 8, verse 8, chorus 8, verse 8 (the strings in), chorus 8, the waltz 8, verse 8, chorus 8,
    # verse 8, chorus 8 (the voice)
    # the bass is let ring through the bar, so that its note, not the celesta's, is the lowest on two and three
    p.voice("plucked bass", ACBASS, 36, {f"n{b}": token(36 + w, 36) + " -" * 11 for b, w in enumerate(walk)},
            [f"n{b}" for b in range(len(walk))], vel=82, gate=0.9, volume=98)
    triads = {"I": "1M", "V": "5,M", "IV": "4,M", "vi": "6,m", "II": "2M"}     # near C4, as they come
    p.voice("celesta", CELESTA, 60, {k: f". . . . {v} - - - {v} - - -" for k, v in triads.items()}, harmony,
            vel=62, gate=1.0, volume=82, pan=76, reverb=70)
    tunes = {
        "Q1": "1 - - - b2 - 1 - b7, - - -", "Q2": "1 - - - - - - - 5, - b7, -",
        "Q3": "1 - - - b2 - b3 - b2 - - -", "Q4": "1 - - - - - - - - - - -",
        "Q5": "5 - - - b6 - 5 - 4 - - -", "Q6": "b3 - - - 4 - b3 - b2 - - -",
        "Q7": "1 - - - b2 - - - b3 - 4 -", "Q8": "1' - - - - - - - - - - -",
        "S1": "1' - - - b6 - - - 1' - - -", "S2": "2' - - - b7 - - - 2' - - -",
        "S3": "4' - - - b3' - - - 1' - b7 -", "S4": "1' - - - - - - - - - - -",
        "S5": "4' - - - 1' - - - 4' - - -", "S6": "5' - - - 2' - - - 5' - - -",
        "S7": "5' - 4' - b3' - - - 4' - 5' -", "S8": "1'' - - - - - - - - - - -",
    }
    over, sung = [f"Q{i}+12" for i in range(1, 9)], rep("S1 S2 S3 S4 S5 S6 S7 S8", 1)    # both from B4 to E6
    p.voice("music box", MUSICBOX, 64, tunes, rep("_", 8) + (over + sung) * 2 + rep("_", 8) + (over + sung) * 2,
            vel=88, gate=1.0, volume=104, pan=50, reverb=70)
    for i, (name, pan) in enumerate((("strings, low", 34), ("strings, middle", 44), ("strings, top", 54))):
        p.voice(name, SLOWSTR, 48, *write(mysterium_line(harmony, i, 48, 24), 48, steps=12, start=24), vel=54,
                gate=1.0, volume=70, pan=pan, reverb=80)
    p.voice("voice", VOICE, 52, tunes, rep("_", 72) + sung, vel=70, gate=1.0, volume=88, pan=62, reverb=90)
    return p


def mysterium_engine_stream():
    """G, 76 a minute, 12/8. Paradox Engine's tunes flowing, with the Engine's key note B heard as the third of G
    major. A harp runs in triplets all through, twelve notes a bar: the bar's bass note (the scale walking down, B
    to B, a note a bar) and the notes of its chord rising two octaves and falling; a contrabass holds the bass note.
    A flute has the verse tune, a clarinet the chorus tune; strings hold the chords from the second time round; the
    third time the flute and the clarinet have both tunes together, an octave apart."""
    p = Piece("Mysterium Engine, Stream", 76, steps=12, per_beat=3, sig=(12, 8))
    verse, chorus = MYSTERIUM_VERSE.split(), MYSTERIUM_CHORUS.split()
    harmony = verse[4:] + (verse + chorus) * 3
    walk = [parse(t, 1)[1][0][2][0] for t in MYSTERIUM_BASS.split()]
    walk = walk[4:] + walk * 6
    key = 43                                                                    # G2: the bass from B2 to B1
    # 52 bars: the harp alone 4 (the verse's last four chords); verse, chorus; verse, chorus (the strings in); both
    # tunes an octave apart
    harp = {}
    for b, chord in enumerate(harmony):
        bass = key + walk[b]
        triad = {x % 12 for x in MYSTERIUM_LINES[chord]}
        up = [q for q in range(bass + 1, bass + 30) if (q - key) % 12 in triad][:6]
        harp[f"n{b}"] = " ".join(token(q, key) for q in [bass] + up + up[4::-1])
    p.voice("harp", HARP, key, harp, list(harp), vel=66, gate=1.0, volume=90, pan=40, reverb=80)
    p.voice("contrabass", CONTRABASS, key, *write([{0: key + w} for w in walk], key, steps=12, start=4), vel=76,
            gate=1.0, volume=96)
    for i, (name, pan) in enumerate((("strings, low", 80), ("strings, middle", 90), ("strings, top", 100))):
        p.voice(name, STRINGS, 55, *write(mysterium_line(harmony, i, 55, 20), 55, steps=12, start=20), vel=56,
                gate=1.0, volume=74, pan=pan, reverb=80)
    tunes = ENGINE_OVER_RIFF_12 | ENGINE_CHORUS_12
    over, sung = [f"Q{i}+12" for i in range(1, 9)], rep("S1 S2 S3 S4 S5 S6 S7 S8", 1)
    p.voice("flute", FLUTE, 71, tunes, rep("_", 4) + over + rep("_", 8) + over + rep("_", 8) + over + sung,
            vel=86, gate=0.97, volume=100, pan=60, reverb=70)                  # F sharp 5 to B6; the last chorus G5 up
    p.voice("clarinet", CLARINET, 59, tunes, rep("_", 12) + sung + rep("_", 8) + sung + over + sung,
            vel=86, gate=0.97, volume=100, pan=70, reverb=70)                  # G4 to B5; the last verse F sharp 4 up
    return p


def mysterium_engine_band():
    """B flat, 132 a minute. The Doom band playing in major: Paradox Engine's riff on a muted guitar in a middle
    octave, its hammered D now the third of B flat major, over a picked bass in eighths that walks down the scale a
    note a bar, D to D, and a rock organ holding the chords; plain driving drums, the ride in the chorus. Over the
    fourth chord the hammer steps up to that chord's root, E flat, the notes standing out of it unchanged (a D
    hammered under an E flat chord is a minor ninth for a whole bar). In the two bars of the chorus where E natural
    sounds (the chord from outside the key, and the chorus tune's E over the fifth chord) the guitar has the hammer
    alone, without the riff's E flat.
    Synth brass has the verse tune, an overdriven lead the chorus tune; the second time both are walked through;
    after a verse without tunes they are plain again, the brass with the lead in the last chorus."""
    p = Piece("Mysterium Engine, Band", 132)
    verse, chorus = MYSTERIUM_VERSE.split(), MYSTERIUM_CHORUS.split()
    harmony = ["I"] * 4 + verse * 2 + chorus + verse + chorus + verse * 2 + chorus
    walk = [parse(t, 1)[1][0][2][0] for t in MYSTERIUM_BASS.split()] * 8
    # 68 bars: the riff alone 4; verse 8 (bass and drums, the organ from its fifth bar); verse, chorus; verse,
    # chorus (walked); verse 8 without tunes; verse, chorus (the brass with the lead)
    bare = {first + i for first in (20, 36, 60) for i in (1, 5)}        # the choruses' bars 2 and 6: E natural
    p.voice("muted guitar", MUTED, 50, {
        "X1": "1! 1 b2' 1 1 b3' 1 1 b2' 1 1 4' 1 b3' 1 1",
        "X4": "b2! b2 b2' b2 b2 b3' b2 b2 b2' b2 b2 4' b2 b3' b2 b2",    # over the fourth chord: the hammer on its root
        "H": "1! 1 . 1 1 . 1 1 . 1 1 . 1 . 1 1",                         # the hammer alone
    }, ["H" if b in bare else "X4" if chord == "IV" else "X1" for b, chord in enumerate(harmony)], vel=82,
            gate=0.6, volume=90, pan=40)
    p.voice("bass", PICKBASS, 34, {f"n{b}": " ".join([token(34 + w, 34), "-"] * 8) for b, w in enumerate(walk)},
            rep("_", 4) + [f"n{b}" for b in range(len(walk))], vel=100, gate=0.8, volume=108)
    for i, (name, pan) in enumerate((("organ, low", 76), ("organ, middle", 84), ("organ, top", 92))):
        p.voice(name, ORGAN, 58, *write(mysterium_line(harmony, i, 58, 8, again=True), 58, start=8), vel=70,
                gate=0.95, volume=78, pan=pan, reverb=40)
    tunes = (ENGINE_OVER_RIFF | {k.replace("Q", "W"): v for k, v in ENGINE_OVER_RIFF_2.items()}
             | ENGINE_CHORUS | {k.replace("S", "T"): v for k, v in ENGINE_CHORUS_2.items()})
    over, walked_over = "Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8", "W1 W2 W3 W4 W5 W6 W7 W8"
    sung, walked = "S1 S2 S3 S4 S5 S6 S7 S8", "T1 T2 T3 T4 T5 T6 T7 T8"
    p.voice("brass", SYNBRASS, 74, tunes, rep("_", 12, over, 1, "_", 8, walked_over, 1, "_", 16, over, 1)
            + [s + "-12" for s in sung.split()], vel=96, gate=0.97, volume=104, pan=64, reverb=50)
    p.voice("lead", OVERDRIVE, 62, tunes, rep("_", 20, sung, 1, "_", 8, walked, 1, "_", 16, sung, 1), vel=96,
            gate=0.97, volume=104, pan=56, reverb=60)
    kick, snare = "x.....x.x.....x.", "....x.......x..."
    fill = {KICK: "x.....x.x.......", SNARE: "....x.....x.xx..", TOM2: "..............x.", TOM4: "...............x"}
    p.drums({
        "h": {HAT: "x.x.x.x.x.x.x.x."},
        "a": {KICK: kick, SNARE: snare, HAT: "X.x.X.x.X.x.X.x."},
        "e": {CRASH: "x...............", KICK: kick, SNARE: snare, HAT: "X.x.X.x.X.x.X.x."},
        "f": fill | {HAT: "X.x.X.x.X......."},
        "c": {CRASH: "x...............", KICK: kick, SNARE: snare, RIDE: "x.x.x.x.x.x.x.x."},
        "r": {KICK: kick, SNARE: snare, RIDE: "x.x.x.x.x.x.x.x."},
        "g": fill | {RIDE: "x.x.x.x.x......."},
    }, rep("h h h f", 1, "e a a f a a a f", 2, "c r r g r r r g", 1, "e a a f a a a f", 1, "c r r g r r r g", 1,
           "e a a f a a a f", 2, "c r r g r r r g", 1), vel=98)
    return p


TRACKS = [
    ("AJM_HING", "the plain Doom rocker: bass and guitar in one riff, organ stabs", hinges),
    ("AJM_GARF", "fast, the Doom way, on Vadim's sketch garmonic: one note held by a muted guitar, the riff slipping under it", garmonic_fast),
    ("AJM_SEVN", "the baroque one, a bar of seven: harpsichord, plucked strings, a cello", seven),
    ("AJM_AFTR", "the quiet one: strings, a low drone, timpani, a few piano notes", after_hours),
    ("AJM_ENGN", "the heavy one, Sigil's way: a chugging guitar, a brass tune over held fifths", engine),
    ("AJM_PORT", "the groove: a fingered bass riff, muted guitar, electric piano, vibes", porter),
    ("AJM_FIRE", "the fast rocker: a galloping riff, a guitar tune over held fifths", fire_door),
    ("AJM_DEAD", "the slow heavy one: a riff on the tritone, timpani, a choir, a bell", dead_letter),
    ("AJM_DSTB", "quiet, the lullaby: a music box over strings that sink a third, a voice a semitone apart", do_not_disturb),
    ("AJM_LUGG", "quiet, the empty hall: a fretless bass riff, electric piano, a vibraphone tune", left_luggage),
    ("AJM_LGHT", "quiet, the watch kept: a harp going round, trembling strings, a horn, then a flute", light_under_the_door),
    ("AJM_FLRS", "quiet, in five: five piano notes round and round, a cello, a held chord", between_floors),
    ("AJM_BELL", "quiet, a slow minor blues: an organ, a bell tolling, a desk bell nobody answers, a cello", night_bell),
    ("AJM_WATR", "quiet, the flooded floor: every chord a step lower, drips on a marimba, a clarinet", standing_water),
    ("AJM_STEP", "children's games, still: plucked steps that stop dead, a music box, a recorder far off", grandmothers_footsteps),
    ("AJM_KNOK", "children's games, the middle one: a recorder and castanets alone, the class joins, then the riff", knock_down_ginger),
    ("AJM_SALT", "children's games, skipping: a nursery tune in major over a bass going down, then the band in minor", salt_mustard),
    ("AJM_WOLF", "children's games, fast: a chug of three, three, seven; a call, the hour struck, a chase", mr_wolf),
    ("AJM_MOVE", "ambient: one note stays through six chords and one other moves at each change; vibes, a clarinet", everything_else_moves),
    ("AJM_GAL4", "ambient, Vadim's sketch distant_galaxy_theme with no two lines moving at once: each chord reached a note at a time", distant_galaxy_four),
    ("AJM_GAL2", "ambient, the same sketch turned: its semitone slip done twice, in slow harp notes", distant_galaxy_two),
    ("AJM_GAR1", "ambient, Vadim's sketch garmonic bar for bar: a held B flat, the notes under it slipping in turn", garmonic_one),
    ("AJM_GAR2", "ambient, the same sketch as a chain: every note falls a semitone, the chords climb by fifths", garmonic_two),
    ("AJM_GALF", "fast, the Doom way, on Vadim's sketch distant_galaxy_theme: a riff that slips a semitone and comes back", distant_galaxy_fast),
    ("AJM_MYS2", "ambient, on Lauridsen's harmony: thirds in the bass walking down, the top line always a step late", mysterium_two),
    # on Paradox Engine, the six kept of ten (26 to 31 in the lab)
    ("AJM_ENS5", "slow, on Paradox Engine: a piano, the riff in the left hand and the tunes in the right, a cello later", engine_piano),
    ("AJM_ENF2", "fast, on Paradox Engine: a heavy shuffle in 12/8; a rock organ has the tune, brass and a guitar the chorus", engine_shuffle),
    ("AJM_ENS4", "slow, on Paradox Engine: a 12/8 swing after dark, the riff on a fretless bass, vibes, a muted trumpet", engine_night_shift),
    ("AJM_ENF4", "fast, on Paradox Engine: the riff shared by a synth bass and a square wave, four on the floor, a saw lead", engine_machine),
    ("AJM_ENF5", "fast, on Paradox Engine: turned over, the key note on top on a muted guitar, the hidden notes a heavy riff below", engine_upside_down),
    ("AJM_ENS3", "slow, on Paradox Engine: a waltz, the riff as its accompaniment on a celesta, both tunes on a music box", engine_music_box),
    # on Distant Galaxy's harmony (32 to 36 in the lab): their lines go under this one
    ("AJM_EGA1", "on Distant Galaxy's harmony: fast, the Doom band: the Engine's riff on his four chords, a brass tune, a guitar tune in the chorus", galaxy_engine_band),
    ("AJM_EGA2", "on Distant Galaxy's harmony: fast, the riff shared by a synth bass and a square wave, four on the floor, a saw lead", galaxy_engine_machine),
    ("AJM_EGA3", "on Distant Galaxy's harmony: fast, a heavy shuffle in 12/8; a rock organ has the tune, brass and a guitar the chorus", galaxy_engine_shuffle),
    ("AJM_EGA4", "on Distant Galaxy's harmony: slow, a piano, the riff in the left hand and the tunes in the right, a cello later", galaxy_engine_piano),
    ("AJM_EGA5", "on Distant Galaxy's harmony: slow, a 12/8 swing after dark, the riff on a fretless bass, vibes, a muted trumpet", galaxy_engine_night_shift),
    # on Garmonic's harmony (37 to 41 in the lab): their lines go under this one
    # on Mysterium's harmony (42 to 46 in the lab): their lines go under this one
    ("AJM_EMY1", "on Mysterium's harmony: slow, a bass walking down, a choir, strings and a pad holding the chords, the tunes on a clarinet and a horn", mysterium_engine_choir),
    ("AJM_EMY2", "on Mysterium's harmony: slow, a piano breaking the major chords in the left hand, Paradox Engine's tunes in the right, a cello later", mysterium_engine_piano),
    ("AJM_EMY3", "on Mysterium's harmony: slow, a waltz in C major, plucked bass and celesta, Paradox Engine's tunes on a music box, strings later", mysterium_engine_music_box),
    ("AJM_EMY4", "on Mysterium's harmony: slow, a 12/8 stream in G major, a harp running in triplets, the tunes on a flute and a clarinet", mysterium_engine_stream),
    ("AJM_EMY5", "on Mysterium's harmony: fast, the Doom band in major: the riff on a muted guitar, a walking bass, organ, brass and a lead", mysterium_engine_band),
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
