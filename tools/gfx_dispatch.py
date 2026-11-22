"""MAP17's goods dispatch (map_dispatch.py, map17.zs): the line and what
rides it, in the institute's look (gfx_institute).

Flats:
  AJDBELT  a belt: black rubber, steel slats across it every 16 (belts run
           along x, so the slats are seen to move)
  AJDSCAL  a weighing stretch: steel slats between yellow edges (a checker
           on a belt, and the bay's scale, which does not move)
  AJDCRBF  a curb's top: hazard stripes       AJDKILF  the kiln's tunnel roof: brick in the glow
Textures:
  AJDCRBS  64x16  a curb's side               AJDBRDS  64x128 a notice board's back: steel
  AJDHOPR  64x256 the hopper's chute (seen from 96 up)
  AJDPRSS  64x256 the press                   AJDKILN  64x192 the kiln: firebrick, glowing
  AJDGANT  64x256 labelling's gantry
  AJDNP1, AJDNK2  64x112  the notes of orders 1 and 2 on their boards (the
           board's top at 112)
  map_dispatch.NOTES: a note on a room's wall (the hidden order's, in the
           press's cell, and the blank crate's, in the hall: each the lower
           part of a sheet torn across, no pin), the bay's shutter with order
           3's note on it, and the two panels by the shutter, each with the
           stub of one of those sheets pinned to it (the top strip, the pin,
           the torn edge that matches)
  AJDSTOR  64x64  crates stacked in the store behind the hopper; AJDSTOF their lids (a flat)
  AJR<s><c> 64x128  a panel of the dispatcher's board (ajarmap.route_board;
           AjarHandler.BoardTick): s is the outlet (H the hopper's 101, P the
           press's 102, K the kiln's 103, L labelling's 104, D the bay's 105,
           X the night room's brass frame),
           c the colour of what hangs there (0 nothing; 1..6 the doors, 7 a
           Stray door, 8 TEAL, 9 ORANGE)
Sprites:
  AJB*     the crate (AjarCrate), its stamps as bands, the first lowest:
           AJB0 A none; AJB1 A-D one; AJB2 A-P two; AJBA-AJBD A-P three (the
           first band's colour picks the name); AJBE-AJBH the same with more
           than three (a hatched top). A band: RED, GREEN, BLUE, or grey for
           any other stamp (the belt lab's 8). Frame = 4 * second + third.
  AJQL A-C a checker's lamp: dark, red (refused), green (filled)
A note is a picture of the crate as it is wanted: no words to read.
"""
import random

import gfx_institute as GI
from gfx import Img, shade, text, digit, DOOR_COLOURS, PAIR_COLOURS
from gfx_bus import blend
from gfx_cinema import paste

ORDERS = {"press": (1,), "kiln": (1, 3), "bay": (3, 2, 1), "secret": (2, 1, 3), "blank": ()}  # what each note wants
TORN = {"secret": 1, "blank": 2}                                                    # the sheets torn across: their tears
BAND = {1: (214, 44, 34), 3: (46, 176, 66), 2: (52, 92, 222)}                      # RED, GREEN, BLUE
GREY = (150, 150, 146)
CARD = (172, 128, 78)
STEEL = (120, 128, 136)
INK = (28, 26, 26)
HAZ = ((224, 182, 40), (34, 32, 30))
NAMES = {"H": ("HOPPER", "101"), "P": ("PRESS", "102"), "K": ("KILN", "103"), "L": ("LABELS", "104"),
         "D": ("BAY", "105"), "X": ("WAY OUT", "")}
COLOUR_NAMES = {1: "RED", 2: "BLUE", 3: "GREEN", 4: "YELLOW", 5: "VIOLET", 6: "PINK", 7: "STRAY", 8: "TEAL",
                9: "ORANGE"}


def colour(c):
    if c in DOOR_COLOURS:
        return DOOR_COLOURS[c]
    if c in PAIR_COLOURS:
        return PAIR_COLOURS[c]
    return (232, 224, 200) if c == 7 else (46, 46, 52)


def hazard(im, x1, y1, x2, y2, w=8):
    for y in range(y1, y2):
        for x in range(x1, x2):
            im.set(x, y, HAZ[((x + y) // w) % 2])


# === the line ====================================================================
def belt():
    im = Img(64, 64, (38, 38, 42))
    rnd = random.Random(1701)
    for y in range(64):
        for x in range(64):
            k = x % 16
            if k in (0, 1):
                c = (20, 20, 22)                                    # the gap between slats
            elif k == 2:
                c = (118, 122, 128)                                 # a slat's lit edge
            elif k < 6:
                c = (92, 96, 102)
            else:
                c = (44, 44, 48)
            im.set(x, y, shade(c, 1 + rnd.uniform(-0.05, 0.05)))
    for y in (6, 57):                                               # rivets along each side
        for x in range(4, 64, 16):
            im.disc(x, y, 1, (150, 152, 156))
    return im


def scale_flat():
    im = Img(64, 64, STEEL)
    rnd = random.Random(1702)
    for y in range(64):
        for x in range(64):
            k = x % 16
            c = (70, 74, 80) if k in (0, 1) else shade(STEEL, 1.25 if k == 2 else 1)
            im.set(x, y, shade(c, 1 + rnd.uniform(-0.04, 0.04)))
    for y1 in (0, 58):
        hazard(im, 0, y1, 64, y1 + 6, 6)
    return im


def curb_flat():
    im = Img(64, 64)
    hazard(im, 0, 0, 64, 64, 8)
    im.noise(6, 1703)
    return im


def curb_side():
    im = Img(64, 16)
    hazard(im, 0, 0, 64, 16, 8)
    im.rect(0, 0, 64, 2, (60, 58, 52))
    im.noise(6, 1704)
    return im


def board_side():
    im = Img(64, 128, STEEL)
    im.frame(0, 0, 64, 128, shade(STEEL, 0.6), 2)
    for y in (4, 123):
        for x in (6, 57):
            im.disc(x, y, 1, shade(STEEL, 1.4))
    im.noise(5, 1705)
    return im


def hopper():
    """The chute over the belt's head, seen from its mouth (96) up: a steel
    funnel narrowing to the mouth, a plate."""
    im = Img(64, 256, (60, 64, 60))
    rnd = random.Random(1706)
    metal = (112, 118, 98)
    for y in range(256):
        for x in range(64):
            g = 1 + 0.12 * ((x % 32) / 32 - 0.5) + rnd.uniform(-0.04, 0.04)
            im.set(x, y, shade(metal, g))
    for y in range(0, 160, 32):                                     # seams and rivets
        im.rect(0, y, 64, y + 2, shade(metal, 0.55))
        for x in range(4, 64, 12):
            im.disc(x, y + 6, 1, shade(metal, 1.4))
    hazard(im, 0, 148, 64, 160, 8)                                  # the mouth's lip
    im.rect(12, 60, 52, 74, (222, 216, 190))
    im.frame(12, 60, 52, 74, (90, 84, 70), 1)
    text(im, "HOPPER", 15, 65, (170, 44, 36), 1)
    im.rect(0, 160, 64, 256, (30, 30, 32))
    return im


def press():
    """The press: heavy dark steel, ribs, a hazard band at the hatch's head."""
    im = Img(64, 256)
    rnd = random.Random(1707)
    base = (70, 84, 80)
    for y in range(256):
        for x in range(64):
            k = x % 32
            g = 1.25 if k in (2, 3) else 0.7 if k in (29, 30) else 1
            im.set(x, y, shade(base, g + rnd.uniform(-0.04, 0.04)))
    for y in (24, 120, 200):
        im.rect(0, y, 64, y + 3, shade(base, 0.5))
        for x in range(6, 64, 16):
            im.disc(x, y + 1, 2, (170, 176, 172))
    hazard(im, 0, 204, 64, 216, 8)                                  # z 52..40 with its top at 256
    im.rect(10, 80, 54, 94, (222, 216, 190))
    im.frame(10, 80, 54, 94, (90, 84, 70), 1)
    text(im, "PRESS", 17, 85, (170, 44, 36), 1)
    for _ in range(30):                                             # oil
        x, y = rnd.randrange(64), rnd.randrange(100, 250)
        for k in range(rnd.randrange(4, 14)):
            blend(im, x, y + k, (30, 26, 20), 0.5)
    return im


def kiln():
    """The kiln: firebrick, soot, a red heat in the joints near the foot."""
    im = Img(64, 192)
    rnd = random.Random(1708)
    brick = (150, 70, 46)
    for y in range(192):
        row = y // 12
        for x in range(64):
            xx = (x + (16 if row % 2 else 0)) % 32
            joint = y % 12 == 0 or xx == 0
            c = (90, 80, 70) if joint else shade(brick, 1 + 0.08 * ((row * 7 + (x + 16 * (row % 2)) // 32) % 3 - 1))
            heat = max(0.0, (y - 110) / 82)
            if joint and heat:
                c = (int(90 + 165 * heat), int(80 + 90 * heat), int(70 - 40 * heat))
            soot = max(0.0, (60 - y) / 60) * 0.6
            im.set(x, y, shade(c, 1 - soot + rnd.uniform(-0.05, 0.05)))
    return im


def kiln_roof():
    im = Img(64, 64)
    for y in range(64):
        for x in range(64):
            joint = y % 16 == 0 or (x + (16 if (y // 16) % 2 else 0)) % 32 == 0
            im.set(x, y, (255, 170, 80) if joint else (170, 70, 40))
    im.noise(8, 1709)
    return im


def gantry():
    """Labelling's gantry: a yellow housing over the belt, its print head, a plate."""
    im = Img(64, 256)
    rnd = random.Random(1710)
    paint = (196, 160, 52)
    for y in range(256):
        for x in range(64):
            im.set(x, y, shade(paint, 1 + rnd.uniform(-0.04, 0.04)))
    for y in (40, 120):
        im.rect(0, y, 64, y + 3, shade(paint, 0.55))
    im.rect(0, 150, 64, 184, (60, 62, 66))                         # the head, at the housing's foot (72 from 256)
    for x in range(4, 64, 8):
        im.rect(x, 170, x + 4, 184, (30, 30, 32))
        im.rect(x + 1, 182, x + 3, 184, (230, 230, 220))           # a label coming out
    im.rect(10, 70, 54, 84, (222, 216, 190))
    im.frame(10, 70, 54, 84, (90, 84, 70), 1)
    text(im, "LABELS", 13, 75, (170, 44, 36), 1)
    im.rect(0, 184, 64, 256, (40, 40, 42))
    return im


# === the crate ===================================================================
def crate(bands, more=False):
    """The crate, 32 by 32: a plywood box, a band of colour for each stamp
    from the foot up (at most three are drawn); `more`: a hatched lid."""
    im = Img(32, 32, CARD)
    rnd = random.Random(1720)
    for y in range(32):
        for x in range(32):
            g = 1 + 0.05 * ((x // 8) % 2) + rnd.uniform(-0.04, 0.04)
            im.set(x, y, shade(CARD, g))
    for i, c in enumerate(bands[:3]):
        y2 = 30 - i * 9
        im.rect(2, y2 - 7, 30, y2, c)
        im.rect(2, y2 - 7, 30, y2 - 6, shade(c, 1.3))
        im.rect(2, y2 - 1, 30, y2, shade(c, 0.6))
    if more:
        for y in range(2, 5):
            for x in range(2, 30):
                im.set(x, y, (240, 240, 236) if (x + y) // 2 % 2 else INK)
    im.frame(0, 0, 32, 32, shade(CARD, 0.5), 2)                     # its edges
    for x, y in ((3, 3), (28, 3), (3, 28), (28, 28)):
        im.disc(x, y, 1, (60, 50, 40))
    return im


def band(c):
    return BAND.get(c, GREY)


def crates(out):
    keys = [1, 3, 2, 0]                                             # RED, GREEN, BLUE, any other: index 0..3
    cols = [band(k) for k in keys]
    letters = "ABCDEFGHIJKLMNOP"
    out["sprites/AJB0A0.png"] = crate([]).png(grab=(16, 32))
    for a in range(4):
        out[f"sprites/AJB1{letters[a]}0.png"] = crate([cols[a]]).png(grab=(16, 32))
        for b in range(4):
            out[f"sprites/AJB2{letters[4 * a + b]}0.png"] = crate([cols[a], cols[b]]).png(grab=(16, 32))
            for c in range(4):
                for more, first in ((False, "ABCD"), (True, "EFGH")):
                    out[f"sprites/AJB{first[a]}{letters[4 * b + c]}0.png"] = \
                        crate([cols[a], cols[b], cols[c]], more).png(grab=(16, 32))


def lamps(out):
    for f, lit in zip("ABC", (None, (240, 50, 36), (60, 230, 80))):
        im = Img(16, 24, (0, 0, 0, 0))
        im.rect(6, 14, 10, 24, (70, 74, 80))                        # its stem
        im.rect(1, 12, 15, 16, (90, 94, 100))
        im.disc(7.5, 7.5, 7, (50, 52, 56))
        im.disc(7.5, 7.5, 5.5, lit or (66, 40, 36))
        if lit:
            im.disc(6, 6, 2, shade(lit, 1.5))
        out[f"sprites/AJQL{f}0.png"] = im.png(grab=(8, 24))


# === the notes ======================================================================
def tear(w, at, seed):
    """Where a sheet w wide is torn across, about `at` from its top: a row for each column."""
    rnd = random.Random(1750 + seed)
    ys, y = [], at
    for _ in range(w):
        y = max(at - 3, min(at + 3, y + rnd.choice((-1, 0, 0, 1))))
        ys.append(y)
    return ys


def paper(seq, w=40, h=56, seed=0, tilt=0, torn=0, part=None):
    """A sheet with the crate as it is wanted on it. `torn` (a tear's number)
    and `part`: the sheet torn across under its pin, and "stub" the strip
    above the tear (the pin in it), "rest" what is below."""
    im = Img(w, h, (236, 232, 214))
    rnd = random.Random(1730 + seed)
    for y in range(h):
        for x in range(w):
            im.set(x, y, shade((236, 232, 214), 1 + rnd.uniform(-0.03, 0.03)))
    pic = crate([band(c) for c in seq])
    paste(im, pic, (w - 32) // 2, h - 38)
    im.rect(w // 2 - 2, 2, w // 2 + 2, 6, (180, 40, 34))           # a pin
    for x in range(4, w - 4):                                       # a ruled line under it
        im.set(x, h - 4, (150, 150, 170))
    if part:
        ys = tear(w, 9, torn)
        for x in range(w):
            for y in range(h):
                if (y > ys[x]) if part == "stub" else (y <= ys[x]):
                    im.px[y * w + x] = [0, 0, 0, 0]
            edge = ys[x] if part == "stub" else ys[x] + 1           # the torn edge: paper's white fibres
            im.set(x, edge, (252, 250, 244))
    if tilt:                                                         # pinned askew: shear it by a pixel a step
        sh = Img(w + 4, h, (0, 0, 0, 0))
        for y in range(h):
            dx = (y * tilt) // (h // 2)
            for x in range(w):
                sh.px[y * sh.w + x + 2 + dx] = list(im.px[y * w + x])
        im = sh
    return im


def note_board(seq, seed):
    """64 by 112, the board's top at row 0: the note pinned to the steel board."""
    im = Img(64, 112, STEEL)
    im.frame(0, 0, 64, 112, shade(STEEL, 0.6), 2)
    im.noise(5, 1740 + seed)
    paste(im, paper(seq, 44, 60, seed), 10, 8)
    return im


def note_on_wall(n, part, shift, seq, seed, torn=0, piece=None):
    im = GI.on_wall(n, part, 64, shift)
    p = paper(seq, 36, 50, seed, tilt=1, torn=torn, part=piece)
    paste(im, p, 12, im.h - 120)
    return im


def stub(n, part, shift, what):
    """A panel in the wall (laid from the ceiling, as the wall is) with the
    stub of the sheet `what` pinned to it, where the whole sheet would be."""
    if n:
        return note_on_wall(n, part, shift, ORDERS[what], 4, TORN[what], "stub")
    im = Img(64, 256, (188, 184, 176))                              # (the plain level: as its notes are drawn)
    paste(im, paper(ORDERS[what], torn=TORN[what], part="stub"), 12, im.h - 120)
    return im


def stacked():
    """Crates stacked in the store: four to a 64, as they ride the belt, unstamped."""
    side, lid = Img(64, 64), Img(64, 64)
    box = crate([])
    for x in (0, 32):
        for y in (0, 32):
            paste(side, box, x, y)
            paste(lid, box, x, y)
    return side, lid


def shutter_note(n, part, shift):
    """The bay's shutter, in the wing's wall: the wall to 160 (laid from the
    ceiling down), the shutter's slats below, order 3's note on them, a plate."""
    im = GI.on_wall(n, part, 64, shift) if n else Img(64, 256, (188, 184, 176))
    steel = (132, 138, 148)
    im.rect(0, 160, 64, 256, steel)
    for y in range(160, 256, 8):
        im.rect(0, y, 64, y + 1, shade(steel, 0.5))
        im.rect(0, y + 1, 64, y + 2, (176, 182, 192))
    im.rect(0, 248, 64, 256, shade(steel, 0.6))
    im.rect(24, 250, 40, 254, (200, 204, 210))
    paste(im, paper(ORDERS["bay"], 44, 60, 9), 10, 176)
    if n:
        GI.plate(im, "BAY", 32, 142, n)
    return im


# === the dispatcher's board ============================================================
def panel(s, c):
    name, num = NAMES[s]
    im = Img(64, 128, (32, 36, 42))
    im.frame(0, 0, 64, 128, (90, 86, 76), 2)
    im.frame(3, 3, 61, 125, (20, 22, 26), 1)
    text(im, name, 32 - len(name) * 3, 10, (232, 224, 200), 1)
    for i, ch in enumerate(num):
        digit(im, ch, 22 + i * 8, 22, (232, 224, 200), 2)
    lit = colour(c)
    im.disc(31.5, 66, 16, (16, 16, 18))
    im.disc(31.5, 66, 14, lit)
    if not num:                                                      # the night room's brass frame
        im.rect(18, 24, 46, 28, (200, 160, 70))
        im.rect(18, 28, 46, 29, (120, 92, 40))
    if c:
        im.disc(27, 61, 4, shade(lit, 1.35))
        word = COLOUR_NAMES[c]
        text(im, word, 32 - len(word) * 3, 94, shade(lit, 1.2), 1)
    else:
        im.rect(26, 96, 38, 98, (90, 90, 96))
    return im


def make(out, notes={}, look=None):
    """`notes`: map_dispatch.NOTES, {name: (wall part, shift, what)}."""
    import map_institute1
    n = map_institute1.LOOK if look is None else look

    def put(kind, name, im):
        key = f"{kind}/{name}.png"
        assert key not in out, key
        out[key] = im.png()
    put("flats", "AJDBELT", belt())
    put("flats", "AJDSCAL", scale_flat())
    put("flats", "AJDCRBF", curb_flat())
    put("flats", "AJDKILF", kiln_roof())
    put("textures", "AJDCRBS", curb_side())
    put("textures", "AJDBRDS", board_side())
    put("textures", "AJDHOPR", hopper())
    put("textures", "AJDPRSS", press())
    put("textures", "AJDKILN", kiln())
    put("textures", "AJDGANT", gantry())
    put("textures", "AJDNP1", note_board(ORDERS["press"], 1))
    put("textures", "AJDNK2", note_board(ORDERS["kiln"], 2))
    for name, (part, shift, what) in notes.items():
        if what == "shutter":
            put("textures", name, shutter_note(n, part, shift))
        elif what.startswith("stub:"):
            put("textures", name, stub(n, part, shift, what[5:]))
        else:
            t = TORN.get(what, 0)
            im = note_on_wall(n, part, shift, ORDERS[what], 4, t, "rest" if t else None) if n else \
                paper(ORDERS[what], torn=t, part="rest" if t else None)
            put("textures", name, im)
    side, lid = stacked()
    put("textures", "AJDSTOR", side)
    put("flats", "AJDSTOF", lid)
    for s in NAMES:
        for c in range(10):
            put("textures", f"AJR{s}{c}", panel(s, c))
    crates(out)
    lamps(out)
