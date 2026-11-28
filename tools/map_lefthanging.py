"""Act 3, level 4: "Left Hanging" (MAP24). PLAN.md, "MAP24 "Left Hanging": the
first version, as decided" and "... the first playable version"; the labs: "The
three times lab", "The old door lab".

The endurance wing three times (tools/ajarthen.py, Times(before=True, old=True);
src/zscript/then.zs): NOW (the ruin, look 3), THEN (the 1960s, look 2, the doors
on test), THEN = NOW + (0, 8192), and BEFORE (ten years before THEN, the wing's
site under the sky, look 1), BEFORE = NOW + (0, 16384). A colour door hung at an
earlier time is an old door in the same frame at every later time.

Three doors: the clocked door (NOW and THEN; leans in the lobby NOW), the ten-year
door (THEN and BEFORE; hangs on test in 122 / 142 at the start), GREEN (hangs
BEFORE in the first frame 141 at the start: old GREEN THEN in 121, ten years, and
NOW in 101, fifty, from the first tic). GREEN's far side: NOW the sump, THEN the
store, BEFORE the old building's cellar.

Places (NOW's coordinates; x east, y north):
  lobby    (0, 0, 640, 512) the start; frame 105 (B) in its west wall (no BEFORE);
           the clocked door leaning; in its north wall the test room's mouth
           (256..384), open only while a colour door hangs BEFORE in 141 (a cause
           that follows that frame, AjarThenFrameCause; it waits for anything
           standing in the mouth)
  test room (128, 528, 512, 912) THEN and NOW: frame 101 / 121 (A) in its east
           wall, THEN under the notice ON TEST. DO NOT REMOVE.; NOW the brass
           door (keys 1 and 2) in its north wall, and behind it the night room,
           the way out
  hall     (640, 0, 2048, 384): bay C (704, 384, 960, 576) off its north side with
           frame 102 / 122 (the test rig THEN); the sump's landing (NOW) or the
           store's wall (THEN) at x 1024..1600; the wet bay E (1664, 384, 1920,
           768) five steps down, 120 under the hall, frame 103 / 123 in its north
           wall: NOW the cistern (filled 96 deep by the valve THEN), THEN the dry
           pump bay; the strongroom's blank wall on its south side (x 1536..2048)
  sump / store (1024, 384, 1600, 1024): NOW the store's floor fallen in, a landing
           at the hall's level along its south side, a broken stair down the west
           side to the bottom 128 under the hall, GREEN's far side 203 in the
           bottom's north wall, and across the pit the ledge (1440, 864, 1600,
           1024) 112 over the bottom with key 2, 352 from the stair and 416 from
           the landing; a basin (96 deep when joined by old GREEN to the full
           cistern: the ledge then 16 over the water). THEN the store, locked for
           the night, its only way in GREEN's far side 223: the chaingun
  strongroom (1536, -512, 2048, -16): no way in but frame 104 / 124 in its south
           wall. NOW key 1 and the plasma rifle; THEN the megasphere (a secret)
  hoist bay (2048, 0, 2432, 384) off the hall's east end: a stair up to its top
           (2048, 384, 2176, 512) at 128, the hoist's shaft (2176, 384, 2304, 512),
           the gallery (2304, 384, 2560, 704) at 128 beyond it. The landing in the
           shaft is up (128) THEN and NOW only while the hoist was left up BEFORE;
           down is a drop. THEN the valve's lever on the gallery's east wall; NOW
           the rocket launcher (a secret)
  the site BEFORE: yard A (-192, -384, 1024, 1216) with frame 141 standing free
           in its pier (GREEN in it) and pier 142; yard B (1600, -704, 2624,
           1216) with piers 143 and 144 (the strongroom's ground) and the hoist
           (its platform where the landing will be, its lever on a pier where the
           hoist bay's east wall will stand). Between them the old building
           (1024, 384, 1600, 1216: its cellar, GREEN's far side 243, inside) and
           the dig (1024, -384, 1600, 384) behind railings: no way across, in sight
Water (water.zs): the cistern NOW (held by the valve), the sump (a basin), and an
outfall before every other frame NOW (the test room's, the lobby's, bay C's, the
strongroom's), so that the sump's water runs out through an old GREEN hung there.
The checks: src/zscript/map24.zs (MODE=1..3 tools/smoke.sh).
"""
import math

import ajarmap
import ajarthen
import ajarwater as W
import budget
import gfx_lefthanging as G
import map_institute1 as I1
import puzzle24
from ajarmap import GREEN
from ajarthen import Times, Part, NOW, THEN, BEFORE, THEN_ID, heights
from udmf import Map, rect

m = Map()
import gfx_institute
m.align |= gfx_institute.ALIGNED            # MAP11's walls are laid by where they are

OFF = (0, 8192)                             # THEN north of NOW, BEFORE north of THEN
t = Times(m, off=OFF, at=(1024, 200), before=True, old=True)

CO, LA, AR, LB = Part("CO"), Part("LA"), Part("AR"), Part("LB")
FL, FC, FA, FR = Part("FL"), Part("FC"), Part("FA"), Part("FR")
KL, KC, KA = Part("KL"), Part("KC"), Part("KA")
TRIM, TRIMF = "AJTRIM", "AJTRIMF"
GRATE = "AJGRATE"                           # an outfall's grate before its frame (NOW)
RAIL = dict(mid="AJRAIL", midboth=True, blocking=True, dontpegbottom=True)    # BEFORE: the dig's railings
H = 256
LATER = (NOW, THEN)

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE = 3004, 9, 3001, 3002, 58
CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS, VILE, PAIN = 65, 69, 3003, 66, 3006, 3005, 67, 64, 71

# tags, tids, causes (map24.zs has the same)
MOUTH_TAG, HOIST_TAG = 2401, 2402           # the test room's mouth (THEN and NOW); the hoist's landing (all times)
CISTERN, SUMP = 2410, 2411                  # NOW's basins
OUT_A, OUT_B, OUT_C, OUT_D = 2412, 2413, 2414, 2415     # NOW's outfalls: before 101, 105, 102, 104
MOUTH, HOIST, VALVE = 11, 12, 13            # the causes' tids: the mouth follows 141; the hoist BEFORE; the valve THEN
BRASS_LINE = 2490                           # the brass door's mouth in the test room (the tests)
A_FRAME = 141


def fit(c, box, features, **base):
    """The room `box` cut along every feature's edges; a feature's changes (later ones win), or None: no
    sector there."""
    xs = sorted({box[0], box[2]} | {v for r, _ in features for v in (r[0], r[2])})
    ys = sorted({box[1], box[3]} | {v for r, _ in features for v in (r[1], r[3])})
    for x1, x2 in zip(xs, xs[1:]):
        for y1, y2 in zip(ys, ys[1:]):
            props, there = dict(base), True
            for (a, b, cc, d), change in features:
                if a <= x1 and x2 <= cc and b <= y1 and y2 <= d:
                    there = change is not None
                    if change:
                        props.update(change)
            if there:
                c.room((x1, y1, x2, y2), **props)


OVER = dict(dontpegtop=True)                # the wall over a way through: laid from the ceiling, as the wall beside it
PIERS = []          # BEFORE: what stands in the yards, (x1, y1, x2, y2) in NOW's coordinates


def pier(a, b, out):
    """BEFORE: a frame's pier, 16 of jamb either side, 16 behind its stub (as the labs')."""
    d = ajarmap.DEPTH + ajarmap.STUB + 16
    xs, ys = (a[0], b[0], a[0] + out[0] * d, b[0] + out[0] * d), (a[1], b[1], a[1] + out[1] * d, b[1] + out[1] * d)
    x1, x2, y1, y2 = min(xs), max(xs), min(ys), max(ys)
    if out[1]:
        x1, x2 = x1 - 16, x2 + 16
    else:
        y1, y2 = y1 - 16, y2 + 16
    PIERS.append((x1, y1, x2, y2))


def frame(a, b, out, n, wall, *, times=(NOW, THEN, BEFORE), floors=None, tags=None):
    """Frame n at `times` (n NOW, n + 20 THEN, n + 40 BEFORE), each its own floor (`floors` {time: z}) and
    recess tag (`tags`); the wall over its mouth the room's. BEFORE it stands in a pier, its mouth turned to
    face the yard (drawn before the yard round it, the use line would face into the recess)."""
    floors, tags = floors or {}, tags or {}
    for c in t.copies:
        if c.when not in times:
            continue
        others = [w for w in times if w != c.when]
        target = n + THEN_ID * (THEN if THEN in others else others[0])
        first = len(m.polys)
        c.frame(a, b, out, n, floors.get(c.when, 0), target=target, **({"tag": tags[c.when]} if c.when in tags else {}))
        if c.before:
            pier(a, b, out)
            a2, b2 = c.P(a), c.P(b)
            recess = next(i for i in range(first, len(m.polys)) if a2 in m.polys[i] and b2 in m.polys[i])
            m.line(a2, b2, back=recess)
        else:
            c.line(a, b, upper=wall, **OVER)


def far(a, b, out, colour, *, floors, tags=None):
    """A colour door's far side at every time, the same spot, each its own floor: line id 200 + colour NOW,
    + 20 THEN, + 40 BEFORE (Times.far, with a floor for each copy)."""
    tags = tags or {}
    for c in t.copies:
        other = t.copies[0 if c.then else 1]
        t.used(c.far_line(colour), f"far side {colour}")
        ajarmap.recess(m, c.P(a), c.P(b), out, floors[c.when], c.far_line(colour), other.far_line(colour),
                       far_colour=colour, **({"tag": tags[c.when]} if c.when in tags else {}))


# =================================================================================================================
# 1. THE LOBBY AND THE TEST ROOM (NOW and THEN)
# =================================================================================================================
LOBBY = (0, 0, 640, 512)
MOUTH_BOX = (256, 512, 384, 528)            # the test room's mouth: 128 wide, the wall's 16 deep
TEST = (128, 528, 512, 912)
FIRST = (288, 352)                          # the first frame 101 / 121 in the test room's north wall, in line with
                                            # the mouth and the start: the first sight of the level
BRASS = (432, 496)                          # NOW: the brass door in the same wall, east of it
GRATE_B = (16, 224, 48, 288)                # NOW: the outfall before 105
GRATE_A = (288, 864, 352, 912)              # NOW: ... before 101
LAMP_A = (256, 800, 384, 912)               # NOW: a working lamp over the first frame (a lit strip of ceiling)


def lobby(c):
    if c.before:
        return
    grate = [(GRATE_B, dict(ftex=GRATE, id=OUT_B))] if c.now else []
    fit(c, LOBBY, grate, floor=0, ceil=H, wall=LB, ftex=FL, ctex=KL)
    c.room(MOUTH_BOX, floor=0, ceil=128, wall=LB, ftex=FL, ctex=FL, id=MOUTH_TAG, light=c.light + (40 if c.now else 0),
           raw=heights(ceils=(0, 128), hold=True))                  # (drawn open: GREEN hangs in 141 at the start)
    for y in (512, 528):
        c.line((MOUTH_BOX[0], y), (MOUTH_BOX[2], y), upper=LB, dontpegtop=True)
    lamp = [(LAMP_A, dict(ctex="TLITE6_4", light=208))] if c.now else []
    grate = [(GRATE_A, dict(ftex=GRATE, id=OUT_A))] if c.now else []
    fit(c, TEST, lamp + grate, floor=0, ceil=H, wall=LA, ftex=FA, ctex=KA, light=c.light + (24 if c.then else 40))


t.both(lobby)
frame((0, 288), (0, 224), (-1, 0), 105, LB, times=LATER, tags={NOW: OUT_B})
frame((FIRST[0], 912), (FIRST[1], 912), (0, 1), 101, LA, tags={NOW: OUT_A})
# THEN: the notice over the first frame (tools/gfx_lefthanging.py)
assert (t.then.look, I1._shift((FIRST[0], 912), (FIRST[1], 912), (0, 1))) == (G.LOOK, G.SHIFT)
t.then.line((FIRST[0], 912), (FIRST[1], 912), upper=G.NOTICE, exact=True, **OVER)
t.frame_cause(320, 400, MOUTH, A_FRAME, tag=MOUTH_TAG)
t.clocked(96, 128, 0)                                                   # leaning in the lobby NOW
START = (320, 96)
m.thing(*START, 1, angle=90)                                            # facing the test room: the old door in it, lit
# NOW: the brass door (keys 1 and 2) in the test room's north wall, and the night room behind it
ajarmap.roomdoor(m, (BRASS[0], 912), (BRASS[1], 912), (0, 1), 0, keys="12", line_id=BRASS_LINE)
m.sector(rect(BRASS[0], 928, BRASS[1], 992), floor=0, ceil=112, light=150, wall="AJXW2", ftex="AJXG2", ctex="AJXC2")
ajarmap.way_out(m, BRASS[0] - 128, 992, None)                          # (a passage of 64: clear of the first frame's stub)

# =================================================================================================================
# 2. THE HALL, BAY C, THE WET BAY, THE STRONGROOM (NOW and THEN)
# =================================================================================================================
HALL = (640, 0, 2048, 384)
BAY_C = (704, 384, 960, 576)
GRATE_C = (800, 528, 864, 576)
WET = (1664, 384, 1920, 768)
WET_LOW = -120                              # five steps down
STRONG = (1536, -512, 2048, -16)
GRATE_D = (1760, -512, 1824, -464)


def hall(c):
    if c.before:
        return
    c.room(HALL, floor=0, ceil=H, wall=CO, ftex=FC, ctex=KC)
    grate = [(GRATE_C, dict(ftex=GRATE, id=OUT_C))] if c.now else []
    fit(c, BAY_C, grate, floor=0, ceil=H, wall=LA, ftex=FA, ctex=KA, light=c.light + 16)
    # the wet bay: five steps of 24 down, then its bottom; NOW the cistern (a basin)
    tag = dict(id=CISTERN) if c.now else {}
    lit = dict(light=c.light + 64) if c.now else {}                     # NOW lit enough to be seen through the bars
    for k in range(1, 6):
        y1 = WET[1] + 32 * (k - 1)
        c.room((WET[0], y1, WET[2], y1 + 32), floor=-24 * k, ceil=160, wall=CO, ftex=FC, ctex=KC,
               **(tag if k > 1 else {}), **lit)
    c.room((WET[0], WET[1] + 160, WET[2], WET[3]), floor=WET_LOW, ceil=160, wall=CO, ftex=FC, ctex=KC, **tag, **lit)
    grate = [(GRATE_D, dict(ftex=GRATE, id=OUT_D))] if c.now else []
    secret = dict(special=1024) if c.then else {}
    fit(c, STRONG, grate, floor=0, ceil=192, wall=AR, ftex=FR, ctex=KA, light=c.light - 8, **secret)


t.both(hall)
frame((800, 576), (864, 576), (0, 1), 102, LA, tags={NOW: OUT_C})
frame((1760, 768), (1824, 768), (0, 1), 103, CO, floors={NOW: WET_LOW, THEN: WET_LOW}, tags={NOW: CISTERN})
frame((1760, -512), (1824, -512), (0, -1), 104, AR, tags={NOW: OUT_D})
# NOW the wet bay's mouth is barred (a fallen grating): water, sight and shots pass, the player and monsters do not.
# Frame 103 NOW is entered only through a door in it (the clocked door hung THEN in 123; old GREEN from the sump)
t.now.line((WET[0], WET[1]), (WET[2], WET[1]), mid="MIDBARS3", midboth=True, blocking=True, wrapmidtex=True)
# the ten-year door on test in 122 (its other leaf in 142)
t.ten_year(832, 480, 90, frame=122 + 0, when=THEN)
W.basin(m, CISTERN, 256 * 224 + 256 * 128, 0, floor=WET_LOW, at=(1792, 640))
t.cause(1792, 600, VALVE, 2, basin=CISTERN, depth=96)                  # THEN: the valve (its lever on the gallery)
for tag, box in ((OUT_A, GRATE_A), (OUT_B, GRATE_B), (OUT_C, GRATE_C), (OUT_D, GRATE_D)):
    W.basin(m, tag, (box[2] - box[0]) * (box[3] - box[1]), 0, floor=0, kind=W.OUTFALL,
            at=((box[0] + box[2]) / 2, (box[1] + box[3]) / 2))

# =================================================================================================================
# 3. THE SUMP (NOW) AND THE STORE (THEN)
# =================================================================================================================
SUMP_BOX = (1024, 384, 1600, 1024)
LANDING_Y = 448                             # NOW: the landing at the hall's level, y 384..448
STAIR_X = (1024, 1088)                      # NOW: the broken stair down the west side, y 448..704
LEDGE = (1440, 864, 1600, 1024)             # NOW: 112 over the bottom (key 2)
BOTTOM = -128
SUMP_CEIL = 192


def store(c):
    if c.before:
        return
    if c.then:
        c.room((1024, 400, 1600, 1024), floor=0, ceil=SUMP_CEIL, wall=AR, ftex=FR, ctex=KA, light=c.light - 32)
        return
    c.room((1024, 384, 1600, LANDING_Y), floor=0, ceil=SUMP_CEIL, wall=AR, ftex=FR, ctex=KA, light=168)
    for k in range(8):                                                  # 16 a step, 32 deep
        y1 = LANDING_Y + 32 * k
        c.room((STAIR_X[0], y1, STAIR_X[1], y1 + 32), floor=-16 * (k + 1), ceil=SUMP_CEIL, wall=AR, ftex=FR, ctex=KA,
               side="TANROCK2", light=160, id=SUMP)
    fit(c, (1024, LANDING_Y, 1600, 1024), [((STAIR_X[0], LANDING_Y, STAIR_X[1], LANDING_Y + 256), None),
                                          (LEDGE, dict(floor=BOTTOM + 112, side="TANROCK2", ctex="TLITE6_4", light=224))],
        floor=BOTTOM, ceil=SUMP_CEIL, wall=AR, ftex="RROCK09", ctex=KA, light=152, id=SUMP)    # (a lamp over the ledge)


t.both(store)
far((1152, 1024), (1216, 1024), (0, 1), GREEN, floors={NOW: BOTTOM, THEN: 0, BEFORE: -64}, tags={NOW: SUMP})
W.basin(m, SUMP, 576 * 576 - 64 * 256, 0, floor=BOTTOM, at=(1280, 640))
W.rate(m, 1300, 600, 0, 0, W.FLOAT)                                     # the player floats up when idle under water

# =================================================================================================================
# 4. THE HOIST AND THE GALLERY (all times); the hoist's lever BEFORE, the valve's THEN
# =================================================================================================================
BAY = (2048, 0, 2432, 384)
STAIR_TOP = (2048, 384, 2176, 512)
SHAFT = (2176, 384, 2304, 512)
GALLERY = (2304, 384, 2560, 704)
UP, DOWN = 128, 16                          # the hoist's deck: up, or a step over the ground
DECK = dict(ftex="FLAT23", side="SUPPORT3")  # the deck's plate and edge, at every time


def hoist(c):
    # (the landing is drawn up: then.zs puts it at its setting at once, Snap; so itemcheck, which knows nothing of
    # causes, walks it)
    landing = dict(floor=UP, id=HOIST_TAG, raw=heights(floors=(DOWN, UP)), **DECK)
    if c.before:
        c.room(SHAFT, **dict(dict(wall=LA, ctex="F_SKY1", ceil=H, light=240), **landing))     # the hoist's deck
        PIERS.append(SHAFT)
        return
    c.room((BAY[0], BAY[1], BAY[2], 128), floor=0, ceil=320, wall=LA, ftex=FA, ctex=KA)
    c.room((2176, 128, BAY[2], BAY[3]), floor=0, ceil=320, wall=LA, ftex=FA, ctex=KA)
    for k in range(8):                                                  # the stair, 16 a step, up to 128
        c.room((2080, 128 + 32 * k, 2176, 160 + 32 * k), floor=16 * (k + 1), ceil=320, wall=LA, ftex=FA, ctex=KA)
    c.room((2048, 128, 2080, 384), floor=0, ceil=320, wall=LA, ftex=FA, ctex=KA)
    c.room(STAIR_TOP, floor=UP, ceil=320, wall=LA, ftex=FA, ctex=KA)
    c.room(SHAFT, ceil=320, wall=LA, ctex=KA, **landing)                 # the same deck, a landing
    secret = dict(special=1024) if c.now else {}
    c.room((2304, 384, 2432, 512), floor=UP, ceil=320, wall=LA, ftex=FA, ctex=KA)
    c.room((2432, 384, 2560, 704), floor=UP, ceil=288, wall=LA, ftex=FA, ctex=KA, light=c.light - 8, **secret)
    c.room((2304, 512, 2432, 704), floor=UP, ceil=288, wall=LA, ftex=FA, ctex=KA, light=c.light - 8, **secret)


t.both(hoist)
# BEFORE the hoist's gantry: two posts at the deck's south corners and a beam between them over its edge; the
# lever on a post of its own beside the deck's west side, facing frame 143's side of the yard
POSTS = [(2160, 368, 2176, 384), (2304, 368, 2320, 384)]
BEAM = (2176, 368, 2304, 384)
LEVER_POST = (2096, 416, 2112, 480)            # (64 from the deck: room to walk between)
PIERS.extend(POSTS + [BEAM, LEVER_POST])
t.cause(2240, 300, HOIST, 2, tag=HOIST_TAG, when=BEFORE)
t.lever((2560, 576), (2560, 640), VALVE)                                # THEN: the valve, on the gallery's east wall

# =================================================================================================================
# 5. BEFORE: THE SITE (two yards, the old building and its cellar, the dig)
# =================================================================================================================
YARD = dict(wall=LA, ftex="FLAT10", ctex="F_SKY1", ceil=H, light=240)
YARD_A = (-192, -384, 1024, 1216)
YARD_B = (1600, -704, 2624, 1216)
OLD = (1024, 384, 1600, 1216)               # the old building (a block), its cellar inside
CELLAR = (1088, 704, 1536, 1024)
DIG = (1024, -384, 1600, 384)


def tiles(area, holes):
    """The rectangle `area` less the rectangles `holes`, as rectangles (map_before.tiles)."""
    x1, y1, x2, y2 = area
    xs = sorted({x1, x2} | {h[0] for h in holes if x1 < h[0] < x2} | {h[2] for h in holes if x1 < h[2] < x2})
    out, open_ = [], {}
    for xa, xb in zip(xs, xs[1:]):
        cover = sorted((h[1], h[3]) for h in holes if h[0] <= xa and h[2] >= xb)
        spans, y = [], y1
        for ha, hb in cover:
            if ha > y:
                spans.append((y, ha))
            y = max(y, hb)
        if y < y2:
            spans.append((y, y2))
        for s in [s for s in open_ if s not in spans]:
            out.append((open_.pop(s), s[0], xa, s[1]))
        for s in spans:
            open_.setdefault(s, xa)
    out += [(xa, s[0], x2, s[1]) for s, xa in open_.items()]
    return out


b = t.before
b.room(CELLAR, floor=-64, ceil=64, wall=LA, ftex=FA, ctex=KA, light=144)
b.room(DIG, floor=-160, ceil=H, wall="TANROCK2", ftex="RROCK09", ctex="F_SKY1", light=220)
for area in (YARD_A, YARD_B):
    for r in tiles(area, [p for p in PIERS if p[0] < area[2] and p[2] > area[0] and p[1] < area[3] and p[3] > area[1]]):
        b.room(r, **YARD)
b.room(BEAM, floor=0, ceil=200, wall="SUPPORT3", ftex="FLAT10", ctex="FLAT23", light=240)
b.cut((LEVER_POST[0], LEVER_POST[1]), (LEVER_POST[0], LEVER_POST[3]))
b.line((LEVER_POST[0], LEVER_POST[1]), (LEVER_POST[0], LEVER_POST[3]), special=130, args=(HOIST,), playeruse=True,
       repeatspecial=True, mid=ajarthen.LIVE[BEFORE], exact=True, dontpegbottom=True)
for x1, y1, x2, y2 in POSTS + [LEVER_POST]:                            # the posts: plain steel
    for e in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x1, y2), (x2, y2))) + ((((x1, y1), (x1, y2)),)
                                                                                 if x1 != LEVER_POST[0] else ()):
        b.line(*e, mid="SUPPORT3")
for x in (DIG[0], DIG[2]):                                              # the railings along the dig, both yards
    b.cut((x, DIG[1]), (x, DIG[3]))
    b.line((x, DIG[1]), (x, DIG[3]), **RAIL)
door_at = t.before.P((320, 950))
ajarmap.door(m, GREEN, *door_at, frame=A_FRAME)                         # GREEN, hung BEFORE in 141 from the start

# =================================================================================================================
# THE TIMES' IDS (frames n, n + 20, n + 40; GREEN's far side 203, 223, 243)
# =================================================================================================================
problems = ajarthen.check_ids(m)
assert not problems, problems

# =================================================================================================================
# COMPANY, SUPPLIES, THE BUDGET (Doom's monsters NOW and THEN; BEFORE is empty)
# =================================================================================================================
PART_OF = []            # (thing index, part) for every monster and pick-up: the budget by part
TAKEN = {NOW: [], THEN: []}
AVOID = {NOW: [START, (96, 128), (320, 470), (320, 870), (832, 560), (1792, 740), (1792, -490), (32, 256),
               (1184, 1000), (1520, 944), (464, 880), (2240, 440), (1792, 400)],
         THEN: [(320, 870), (832, 560), (1792, 740), (1792, -490), (32, 256), (2240, 440), (1792, 400), (320, 470)]}


def halton(i, base):
    f, r = 1, 0
    while i:
        f /= base
        r += f * (i % base)
        i //= base
    return r


def spot(box, r=20, when=NOW):
    """A free place for a thing of radius r in `box` (NOW's coordinates; a Halton sequence: the same every
    build)."""
    x1, y1, x2, y2 = box
    taken = TAKEN[when]
    for k in range(1, 4000):
        x = round((x1 + r + 8 + halton(k, 2) * (x2 - x1 - 2 * r - 16)) / 8) * 8
        y = round((y1 + r + 8 + halton(k, 3) * (y2 - y1 - 2 * r - 16)) / 8) * 8
        if any(max(abs(x - tx), abs(y - ty)) < r + tr + 12 for tx, ty, tr in taken):
            continue
        if any(math.hypot(x - ax, y - ay) < 72 + r for ax, ay in AVOID[when]):
            continue
        dy = OFF[1] * when
        if any(math.hypot(x - th["x"], y + dy - th["y"]) < r + 28 for th in m.things):
            continue
        taken.append((x, y, r))
        return x, y
    raise ValueError(f"no room in {box}")


R = {CACO: 31, MANCUBUS: 48, BARON: 24, KNIGHT: 24, DEMON: 30, SPECTRE: 30, REVENANT: 20, PAIN: 31, VILE: 20}


def mark(part, first):
    PART_OF.extend((i, part) for i in range(first, len(m.things)))


def put(part, box, kind, k, angle=0, when=NOW, **more):
    first = len(m.things)
    for _ in range(k):
        x, y = spot(box, R.get(kind, 20), when)
        m.thing(x, y + OFF[1] * when, kind, angle=angle, **more)
    mark(part, first)


def ambush(part, box, cause, kind, k, *, angle=0, after=0, near=0, arg=None, when=NOW):
    first = len(m.things)
    spots = [spot(box, R.get(kind, 20), when) for _ in range(k)]
    spots = [(x, y + OFF[1] * when) for x, y in spots]
    if arg is None:
        ajarmap.ambush(m, cause, kind, *spots, angle=angle, after=after, near=near)
    else:
        ajarthen.ambush(m, cause, arg, kind, *spots, angle=angle, after=after, near=near)
    mark(part, first)


def items(part, *spec, when=NOW):
    first = len(m.things)
    for x, y, kind in spec:
        m.thing(x, y + OFF[1] * when, kind)
    mark(part, first)


DEAF = dict(ambush=True)
HALL_IN = (656, 16, 2032, 368)
LOBBY_IN = (16, 16, 624, 496)
TEST_IN = (144, 544, 496, 896)
SUMP_IN = (1104, 464, 1424, 1008)
# --- the lobby NOW: the start; the shotgun; the last fight when GREEN is hung back in 141
items("lobby", (448, 160, 2001), (480, 200, 2008), (560, 120, 2008), (160, 400, 2011), (560, 440, 2049),
      (96, 440, 2012))
put("lobby", (320, 220, 624, 496), ZOMBIE, 4, 270)
put("lobby", (320, 220, 624, 496), SERGEANT, 3, 270)
_last = MOUTH * 16 + 1
ambush("lobby", LOBBY_IN, ajarthen.AMBUSH_CAUSE, KNIGHT, 3, angle=90, after=1, arg=_last)
ambush("lobby", LOBBY_IN, ajarthen.AMBUSH_CAUSE, IMP, 4, angle=90, after=1, arg=_last)
ambush("lobby", (656, 16, 1400, 368), ajarthen.AMBUSH_CAUSE, REVENANT, 3, angle=180, after=2, arg=_last)
ambush("lobby", (656, 16, 1400, 368), ajarthen.AMBUSH_CAUSE, BARON, 1, angle=180, after=3, arg=_last)
ambush("lobby", LOBBY_IN, ajarthen.AMBUSH_CAUSE, CACO, 2, angle=90, after=3, arg=_last)
items("lobby", (64, 64, 2046), (600, 64, 2049), (600, 480, 2046), (64, 480, 17), (320, 300, 2012))
# --- the test room NOW: a few imps round the old door
put("test room", TEST_IN, IMP, 3, 0)
items("test room", (200, 600, 2049), (180, 860, 2048))
# --- the hall NOW: the first fight; the super shotgun in bay C; the ambush when key 1 is taken
items("hall", (900, 448, 82), (760, 448, 2049), (1500, 64, 2048), (1300, 320, 2049), (1980, 64, 2046),
      (700, 300, 2012), (1980, 320, 2049), (1150, 64, 2048), (960, 200, 2012), (1800, 200, 17))
put("hall", HALL_IN, IMP, 7, 180)
put("hall", HALL_IN, SERGEANT, 5, 180)
put("hall", HALL_IN, CHAINGUNNER, 3, 180)
put("hall", HALL_IN, DEMON, 3, 180)
put("hall", HALL_IN, SPECTRE, 2, 180)
put("hall", (2192, 16, 2416, 368), IMP, 3, 180)                         # the hoist bay
ambush("hall", HALL_IN, 1, IMP, 4, angle=270, after=1)
ambush("hall", HALL_IN, 1, KNIGHT, 2, angle=270, after=1)
ambush("hall", HALL_IN, 1, REVENANT, 2, angle=180, after=2)
ambush("hall", HALL_IN, 1, CACO, 2, angle=180, after=2)
ambush("hall", (2192, 16, 2416, 368), 1, CHAINGUNNER, 2, angle=180, after=1)
# --- the wet bay NOW: what lives at the cistern's foot (it drowns when the valve is opened)
put("wet bay", (1680, 560, 1904, 752), IMP, 2, 270)
items("wet bay", (1700, 340, 2049), (1880, 340, 2048))                          # (before the bars, in the hall)
# --- the sump NOW: imps at its bottom; when key 2 is taken, cacodemons over the water
put("sump", SUMP_IN, IMP, 4, 270)
put("sump", SUMP_IN, DEMON, 2, 270)
items("sump", (1060, 420, 2049), (1560, 420, 2046), (1300, 420, 2012), (1500, 950, ajarmap.KEY_T["2"]),
      (1560, 1000, 2013))
ambush("sump", SUMP_IN, 2, CACO, 4, angle=90, after=1)
ambush("sump", SUMP_IN, 2, PAIN, 1, angle=90, after=2)
items("sump", (1100, 420, 17), (1250, 420, 2047))
# --- the strongroom NOW: key 1 and the plasma rifle
items("strongroom", (1792, -300, ajarmap.KEY_T["1"]), (1700, -200, 2004), (1900, -200, 17), (1600, -64, 2012))
# --- the gallery NOW: a secret (the rocket launcher); two revenants keep it
items("gallery", (2496, 640, 2003), (2496, 560, 2046), (2368, 640, 2046), (2496, 440, 2019))
put("gallery", (2320, 528, 2544, 688), REVENANT, 2, 270)
# --- THEN: a few at the start in the hall; more come into it when the valve is opened; the store's chaingun
put("hall then", HALL_IN, ZOMBIE, 4, 180, when=THEN)
put("hall then", HALL_IN, SERGEANT, 3, 180, when=THEN)
put("hall then", (2192, 16, 2416, 368), IMP, 2, 180, when=THEN)
items("hall then", (1100, 64, 2049), (1500, 320, 2048), (700, 64, 2012), (1980, 200, 2049), when=THEN)
_valve = VALVE * 16 + 1
ambush("hall then", HALL_IN, ajarthen.AMBUSH_CAUSE, IMP, 4, angle=90, after=1, arg=_valve, when=THEN)
ambush("hall then", HALL_IN, ajarthen.AMBUSH_CAUSE, DEMON, 3, angle=90, after=1, arg=_valve, when=THEN)
ambush("hall then", HALL_IN, ajarthen.AMBUSH_CAUSE, CHAINGUNNER, 2, angle=90, after=2, arg=_valve, when=THEN)
ambush("hall then", (2192, 16, 2416, 368), ajarthen.AMBUSH_CAUSE, KNIGHT, 1, angle=90, after=2, arg=_valve,
       when=THEN)
items("store then", (1300, 700, 2002), (1250, 760, 2048), (1350, 760, 2048), (1300, 900, 2049), when=THEN)
items("gallery then", (2496, 480, 2049), (2368, 640, 2012), when=THEN)
# --- secrets: the strongroom THEN (the megasphere); BEFORE: the cellar (armour, stimpacks)
items("secrets", (1792, -300, 83), (1700, -120, 2049), when=THEN)
items("cellar", (1200, 900, 2018), (1300, 900, 2011), (1400, 900, 2011), (1300, 800, 2011), when=BEFORE)

SKILLS = m._skills()
BUDGET = {}
for part in dict.fromkeys(p for _, p in PART_OF):
    idx = [i for i, p in PART_OF if p == part]
    for level in (3, 1):
        BUDGET[(part, level)] = budget.reckon([m.things[i] for i in idx], [SKILLS[i] for i in idx], level)
ALL = [i for i, _ in PART_OF]
for level in (3, 1):
    BUDGET[("the level", level)] = budget.reckon([m.things[i] for i in ALL], [SKILLS[i] for i in ALL], level)
MONSTERS = {lv: sum(budget.reckon([m.things[i] for i in ALL], [SKILLS[i] for i in ALL], lv)["monsters"].values())
            for lv in (1, 2, 3, 4)}
assert 90 <= MONSTERS[3] <= 120, MONSTERS
r = BUDGET[("the level", 3)]
assert r["dmg"] >= 1.6 * r["hp"], budget.line("the level", r, 3)

PUZZLE = puzzle24.PUZZLE24

if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["budget"]:
        for (part, level), r in BUDGET.items():
            print(budget.line(part, r, level))
        print("monsters by skill:", MONSTERS)
    else:
        sys.stdout.write(m.textmap())
