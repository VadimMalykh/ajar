"""Act 3, level 1: "In the Long Run" (MAP21). PLAN.md, "MAP21 "In the Long
Run": the first version, as decided" and "... the first playable version";
"MAP21: colour doors by time, the pass office, and the way out built".

The institute twice: NOW (MAP11's look 3, Post Box: emptied, Doom's stone grown
through it, Doom's doors) and THEN, forty years before (look 2, Thaw: full,
every room locked for the night), THEN 8192 north of NOW (tools/ajarthen.py,
src/zscript/then.zs). The clocked door joins the two times: hung in a frame it
hangs in that frame's twin too, and each leads to the other. A colour door joins
places, never times: it has a far side at each time, and hung it leads to the
one at its frame's time.

Places (NOW's coordinates; x east, y north):
  hall      (0, 0, 1024, 768), the start: the machine in the middle with its
            frame 101 (the clocked door's alone, at both times; it hangs there
            at the start); north of it the desk on a dais. THEN the brass
            shutter in the north wall, open only while the machine runs (keys 1
            and 2 turned at the desk THEN and the clocked door in 101), and the
            night room (352..672, 784..1040) behind it: GREEN's far side in its
            west end, the brass frame HOME (GREEN only) in its east end; GREEN
            hung there is the way out, built. NOW the same room dead, GREEN's
            far side its only way in. NOW the hall is sealed: its only way is
            the vestibule's bolted door.
  vestibule (1040, 224, 1296, 544). THEN the security post: open to the hall,
            the goods edge (a drop of 40 into the pocket, never back) and the
            turnstile (a squeeze), and the pass office, a glazed booth on the
            south wall (1104..1232, 224..288), locked: BLUE's far side THEN is
            in it, with the megasphere (a secret). NOW bolted on both sides,
            the booth's footprint only; BLUE's far side NOW is in it, and
            arriving draws both bolts (the hall wakes).
  corridor  (1312, 160, 1504, 2256), floor -40. THEN only its first stretch,
            the pocket (y 160..640), behind a night grille. Frame 103 in its
            east wall (NOW the clocked door's alone, THEN any door's), frame 104
            in its south wall (any door, both times).
  cellar    west of the corridor: the landing (1056..1232, 1088..1600, -40)
            with frame 105 in its east wall, the pit (576..1056, floor -200)
            with a stair down, the ledge (576..704, 1280..1472, -56), the store
            behind a pressure door in the pit's north wall (NOW only: key 2).
            The valve THEN (open at the start): NOW the pit stands full to -72.
  goods bay east of the corridor (1568..2160, 1088..1536, -40), frame 108 in
            its north wall; the gallery (2032..2160, 56) along its east wall,
            RED on it. The belt THEN (standing at the start): NOW the hatch
            stair down to the bay cellar (the super shotgun, GREEN) is open;
            running, a heap of crates climbs to the gallery.
  optics    north of the corridor (1152..1664, 2320..2832, -40), frame 106 in
            its south wall. The beam THEN (at C at the start): NOW a burnt hole
            in wall A, B or C, a closet behind each (A: BLUE; B: a secret; C:
            the rocket launcher).
  lobby     MAP11's lobby and cloakroom, 2560 east (2560..3584, 0..640),
            sealed at both times; RED's far side at both times, frame 110.
Room doors NOW are Doom's (BIGDOOR2, USE); THEN the same doorways are the
institute's doors, locked for the night. The checks: src/zscript/map21.zs.
"""
import math

import ajarmap
import ajarthen
import ajarwater as W
import budget
import map_institute1 as I1
import puzzle21
from ajarmap import RED, BLUE, GREEN, far_id
from ajarthen import Times, Part, NOW, THEN, THEN_ID, heights
from udmf import Map

m = Map()
import gfx_institute
m.align |= gfx_institute.ALIGNED            # MAP11's walls are laid by where they are

OFF = (0, 8192)
t = Times(m, off=OFF, at=(512, 32))         # the AjarThen thing, in the hall NOW

# --- the apparatus THEN, and where it stood NOW (tools/gfx_longrun.py, src/zscript/apparatus.zs) -----------------
# The look each group of parts wears: 1 Lamps and Reels, 2 Copper and Porcelain, 3 Glass and Mercury. Vadim's
# choice is written here; AJAR_APPARATUS=1, 2 or 3 sets every group to that look (the look board's builds).
import os
import gfx_longrun as GL
APPARATUS = dict(cabinets=1, racks=1, benches=1, tanks=1, pumps=1, belt=1, consoles=1, pictures=1, things=1, emitter=1)
if os.environ.get("AJAR_APPARATUS"):
    APPARATUS = dict.fromkeys(APPARATUS, int(os.environ["AJAR_APPARATUS"]))
m.align |= GL.ALIGNED
TROLLEY_T, TALL_T, SMALL_T, EMITTER_LOOK_T = 20195, 20196, 20197, 20198      # (apparatus.zs)


def ap(part, group):
    """A part's texture in its group's look."""
    return GL.name(part, APPARATUS[group])


def apparatus(x, y, kind, solid=False):
    """A piece of apparatus THEN, a sprite (a trolley, a tall piece, a small thing): in the things' look;
    solid only where it stands flush against a wall and nobody walks."""
    t.then.thing(x, y, kind, args=(APPARATUS["things"], int(solid)))


def bank_front(a, b, group="cabinets"):
    """THEN: a cabinet bank's front a-b (64s from a multiple of 64): each 64 its own cabinet, by where it is."""
    (x1, y1), (x2, y2) = a, b
    n = (abs(x2 - x1) + abs(y2 - y1)) // 64
    for k in range(n):
        p = (x1 + (x2 - x1) * k // n, y1 + (y2 - y1) * k // n)
        q = (x1 + (x2 - x1) * (k + 1) // n, y1 + (y2 - y1) * (k + 1) // n)
        t.then.cut(p, q)
        t.then.line(p, q, lower=f"AJUCB{APPARATUS[group]}{'ABCD'[(p[0] + p[1]) // 64 % 4]}")


def picture(a, b, out, kind, part, group="pictures"):
    """THEN: the wall piece a-b, seen looking `out`, shows gfx_longrun's picture `kind` on the wall `part`."""
    sh = I1._shift(t.then.P(a), t.then.P(b), out)
    look = APPARATUS[group] if kind in GL.HOME else 2                   # (the notice and the calendar: one of a kind)
    hang_raw(t.then, a, b, GL.picture_name(kind, look, part, sh))


apic = picture          # (sections 4 to 6 have a picture() of their own: there the apparatus's is apic())


def ghost(a, b, out, part, rects, stubs=None):
    """NOW: the wall piece a-b, seen looking `out`, shows where things stood or hung THEN: `rects` (x1, y1,
    x2, y2) in the piece's picture, y from the top of the 256 (furniture h high: (x1, 256 - h, x2, 256);
    a picture: GL.RECT[kind])."""
    sh = I1._shift(a, b, out)
    w = abs(a[0] - b[0]) + abs(a[1] - b[1])
    hang_raw(t.now, a, b, GL.ghost_name(part, w, rects, sh, stubs))


def hang_raw(c, a, b, tex):
    c.cut(a, b)
    c.line(a, b, mid=tex, exact=True)

EX, EV, LB, CK, CO, LA, AR, PU = (Part(p) for p in ("EX", "EV", "LB", "CK", "CO", "LA", "AR", "PU"))
FE, FL, FC, FA, FR, FP = (Part(p) for p in ("FE", "FL", "FC", "FA", "FR", "FP"))
KE, KL, KC, KA, KP = (Part(p) for p in ("KE", "KL", "KC", "KA", "KP"))
H = 256                                     # every room is this high over its floor (MAP11's walls)
LOW = -40                                   # the corridor's floor, and the rooms off it
STONE, STONE_FLAT = "TANROCK2", "RROCK09"   # Doom's stone, grown through the building NOW
DOOM_DOOR, TRACK = "BIGDOOR2", "DOORTRAK"   # Doom's room doors NOW

# tags and tids
BOLTS = 2100            # the vestibule's two bolted doors (ajarmap.bolted)
SHUTTER = 2101          # the brass shutter THEN (opened by the machine)
MACHINE_LIGHT = 2102    # the hall THEN: brighter once the machine runs
BASIN, PDOOR, LAMP = 2110, 2111, 2112       # the cellar's pit (ajarwater), the store's pressure door, its lamps
HEAP = 2120             # the heap's steps (the belt)
HOLES = 2130            # optics' three holes (the beam)
BELT_TAG = 921          # THEN's belt (ajarmap.BELT_TAG + 21)
VALVE, BELT, BEAM = 11, 12, 13              # the causes' tids (then.zs, map21.zs)
DESK = 2140             # the desk (AjarLongRunDesk, map21.zs)
LOCKED = 2141           # THEN's room doors: "Locked for the night." (AjarThenLocked)
DESK_T = 20187

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE = 3004, 9, 3001, 3002, 58
CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS, ARACH = 65, 69, 3003, 66, 3006, 3005, 67, 68


def fit(c, box, features, **base):
    """ajarmap.fitted for one copy: the room `box` cut along every feature's
    edges; a feature's changes (later ones win), or None: no sector there."""
    xs = sorted({box[0], box[2]} | {v for r, _ in features for v in (r[0], r[2])})
    ys = sorted({box[1], box[3]} | {v for r, _ in features for v in (r[1], r[3])})
    for x1, x2 in zip(xs, xs[1:]):
        for y1, y2 in zip(ys, ys[1:]):
            props, there = dict(base), True
            for (a, b, cc, d), change in features:
                if a <= x1 and x2 <= cc and b <= y1 and y2 <= d:
                    if change is None:
                        there = False
                    else:
                        there = True
                        props.update(change)
            if there:
                c.room((x1, y1, x2, y2), **props)


def look(wall, ftex, ctex, floor=0, **k):
    return dict(wall=wall, ftex=ftex, ctex=ctex, floor=floor, ceil=floor + H, **k)


def box(height, top, side, floor=0):
    return dict(floor=floor + height, ftex=Part(top), side=Part(side))


def pillar(side, floor=0):                  # to the ceiling: the machine, a tank, a pillar
    return dict(floor=floor + H, side=Part(side))


def hang(c, a, b, part):
    """The wall piece a-b shows MAP11's picture `part` in the copy's look."""
    c.cut(a, b)
    c.line(a, b, mid=Part(part), exact=True)


def stone(c, a, b):
    """NOW: Doom's stone where the institute had a way (a wall piece)."""
    c.cut(a, b)
    c.line(a, b, mid=STONE, exact=True)


def frame(a, b, out, n, wall, floor=0, clock=None, **k):
    """A twinned frame; the wall over its mouth is the room's. `clock`: the
    copies where it takes only the clocked door."""
    if clock:
        t.clock_frame(a, b, out, n, floor, when=clock, **k)
    else:
        t.frame(a, b, out, n, floor, **k)
    t.line(a, b, upper=wall)


def sign(c, a, b, out, part, words, oh):
    """MAP11's plate with `words` over the way a-b, seen looking `out`, in the
    copy's look (map_institute1.SIGNS: gfx_institute draws it)."""
    w = abs(a[0] - b[0]) + abs(a[1] - b[1])
    key = (c.look, part, words, I1._shift(c.P(a), c.P(b), out), w, oh)
    c.line(a, b, upper=I1.SIGNS.setdefault(key, f"AJIS{c.look}{len(I1.SIGNS):02d}"), exact=True)


def room_door(a, b, out, floor, wall_near, wall_far, name, *, thick=64):
    """A room door in a wall `thick` deep; a-b its mouth on the corridor's
    side, `out` into the room. NOW Doom's: a door sector between two jamb
    strips, USE opens it (Door_Raise), monsters too. THEN the corridor
    beyond is not built: from inside the room the institute's door, shut,
    "Locked for the night." (AjarThenLocked); declare the rooms first.
    Over it inside the room, at both times, the same plate: CORRIDOR (THEN
    on the door's face, NOW over Doom's door); NOW `name` over it on the
    corridor's side."""
    def p(q, d):
        return (q[0] + out[0] * d, q[1] + out[1] * d)
    n = t.now
    a1, b1, a2, b2, a3, b3 = p(a, 16), p(b, 16), p(a, thick - 16), p(b, thick - 16), p(a, thick), p(b, thick)
    n.sector([a, b, b1, a1], floor=floor, ceil=floor + 96, wall=wall_near, ftex="FLAT20", ctex="FLAT20", light=140)
    n.sector([a2, b2, b3, a3], floor=floor, ceil=floor + 96, wall=wall_far, ftex="FLAT20", ctex="FLAT20", light=140)
    d = n.sector([a1, b1, b2, a2], floor=floor, ceil=floor, wall=DOOM_DOOR, ftex="FLAT20", ctex="FLAT20", light=140)
    for q1, q2 in ((a1, b1), (a2, b2)):
        n.line(q1, q2, back=d, special=12, args=(0, 32, 150), playeruse=True, monsteruse=True, repeatspecial=True)
    for q1, q2 in ((a, a3), (b, b3)):
        n.line(q1, q2, mid=TRACK, dontpegbottom=True)
    sign(n, a, b, out, wall_near, name, 96)
    sign(n, a3, b3, (-out[0], -out[1]), wall_far, "CORRIDOR", 96)
    th = t.then                                     # THEN: the door's face on the room's wall
    key = (th.look, wall_far, I1._shift(th.P(a3), th.P(b3), (-out[0], -out[1])), "", "CORRIDOR")
    th.cut(a3, b3)
    th.line(a3, b3, mid=I1.FACES.setdefault(key, f"AJID{th.look}{len(I1.FACES):02d}"), special=130, args=(LOCKED,),
            playeruse=True, repeatspecial=True, exact=True)


# =================================================================================================
# 1. THE MACHINE HALL (the start)
# =================================================================================================
HALL = look(EX, FE, KE)
MACHINE = [((384, 320, 480, 448), pillar("MC")), ((544, 320, 640, 448), pillar("MC")),
           ((480, 384, 544, 448), pillar("MC")), ((480, 320, 544, 384), None),      # 101's recess in its south face
           ((384, 256, 464, 320), pillar("MC")), ((560, 256, 640, 320), pillar("MC"))]   # its wings, either side of 101
# the desk it is run from, south of it on a dais: through 101 the other time's desk and machine are in view
DAIS = ((416, 112, 608, 208), dict(floor=8, side=Part("B4"), ftex=Part("FA")))
DESK_BOX = ((464, 144, 560, 176), box(40, "DT", "DS", floor=8))
# THEN the apparatus: two banks of cabinets against the west and east walls in the north half, two low consoles in
# the south half, cable ducts in the floor from the machine to the banks and from the dais to the machine (at both
# times: NOW their covers are gone). NOW the banks' and consoles' footprints, and on the walls where they stood.
BANKS = [(0, 448, 64, 704), (960, 448, 1024, 704)]                              # 128 high
CONSOLES = [(64, 128, 128, 256), (896, 128, 960, 256)]                          # 48 high
DUCTS = [(0, 416, 384, 448), (640, 416, 1024, 448), (416, 208, 448, 256), (576, 208, 608, 256)]
for c in t.copies:
    if c.then:
        furn = [(r, dict(floor=128, ftex=ap("CT", "cabinets"), side=ap("CS", "cabinets"))) for r in BANKS]
        furn += [(r, dict(floor=48, ftex=ap("CK", "consoles"), side=ap("CN", "consoles"))) for r in CONSOLES]
    else:
        furn = [(r, dict(ftex="AJIFE2")) for r in BANKS + CONSOLES]
    furn += [(r, dict(ftex="AJUDU3" if c.now else "AJUDU2")) for r in DUCTS]
    fit(c, (0, 0, 1024, 768), MACHINE + [DAIS, DESK_BOX] + furn, **HALL,
        **(dict(id=MACHINE_LIGHT, light=176) if c.then else {}))
    hang(c, (640, 0), (768, 0), "NB")                                           # the clock: going THEN, stopped NOW
bank_front((64, 448), (64, 704))
bank_front((960, 704), (960, 448))
BANK_GHOST = [(0, 128, 256, 256)]
ghost((0, 448), (0, 704), (-1, 0), "EX", BANK_GHOST, (2,))
ghost((1024, 448), (1024, 704), (1, 0), "EX", BANK_GHOST, (1,))
# by the doorway to the vestibule, where the player leaving the hall passes them: the notice and the calendar THEN;
# NOW the notice's ghost and the calendar's same page, yellowed
picture((1024, 256), (1024, 320), (1, 0), "NT", "EX")
ghost((1024, 256), (1024, 320), (1, 0), "EX", [GL.RECT["NT"]])
picture((1024, 416), (1024, 448), (1, 0), "CL", "EX")
hang_raw(t.now, (1024, 416), (1024, 448), GL.picture_name("CL", 3, "EX", I1._shift((1024, 416), (1024, 448), (1, 0))))
picture((576, 768), (704, 768), (0, 1), "SC", "EX")                            # the machine's schematic, THEN (NOW: stone)
apparatus(288, 736, TALL_T, solid=True)                                         # two tall pieces against the north wall,
apparatus(736, 736, TALL_T, solid=True)                                         # either side of the night room's wall
apparatus(168, 584, TROLLEY_T)                                                  # a trolley left by the west bank
apparatus(548, 158, SMALL_T)                                                    # on the desk
frame((480, 320), (544, 320), (0, 1), 101, Part("MC"), clock=(NOW, THEN))
t.clocked(512, 300, 90, frame=101)                                              # found hung in the machine
t.line((480, 176), (544, 176), special=130, args=(DESK,), playeruse=True, playeruseback=True, repeatspecial=True,   # its panel faces the machine
       now=dict(lower="AJTHK3"), then=dict(lower="AJTHK2"))
t.now.thing(512, 192, DESK_T, id=DESK)                                         # one desk thing: it tells the times apart
hang(t.then, (64, 768), (192, 768), "CP")                                       # the desk's old controls; a warning
hang(t.then, (832, 768), (896, 768), "WS")
# north wall: THEN the brass shutter and the night room; NOW Doom's stone (all of it)
t.then.sector([(480, 768), (544, 768), (544, 784), (480, 784)], floor=0, ceil=0, wall="AJSHUT", ftex="AJTRIMF",
              ctex="AJTRIMF", light=160, id=SHUTTER)
for x in (480, 544):
    t.then.line((x, 768), (x, 784), mid="AJTRIM", dontpegbottom=True)
# The way out is built by the player (Vadim, 2026-11-26: "I also don't like that exit is ready again. Let's
# make me build it"). THEN the night room behind the shutter: GREEN's far side (its copy THEN, far_id + THEN_ID)
# in its west end, the brass frame HOME in its east end, GREEN's alone (the brass inlaid with green; a THEN frame
# with no twin). NOW the same room on the same spot, dead: dark, no candelabra, GREEN's far side (its own id) in
# its west end, Doom's stone where the brass frame is THEN; no way in or out but GREEN.
NIGHT = (352, 784)
ajarmap.way_home(m, *t.then.P(NIGHT), GREEN, only=True, far=far_id(GREEN) + THEN_ID)
ajarmap.room(m, [352, 672], [784, 880, 944, 1040], lambda i, j: j == 1, ceil=160, light=70, wall="AJXW2",
             ftex="AJXG2", rug="AJXR2", ctex="AJXC2", floor=0)
ajarmap.recess(m, (352, 880), (352, 944), (-1, 0), 0, far_id(GREEN), far_id(GREEN) + THEN_ID, far_colour=GREEN)
stone(t.now, (672, 880), (672, 944))
for x0, x1 in ((0, 384), (384, 640), (640, 1024)):
    t.now.line((x0, 768), (x1, 768), mid=STONE)
t.now.cut((384, 768), (640, 768))
# the start: MAP20's sluice in the south wall, shut behind the player (NOW)
t.now.sector([(480, -16), (480, 0), (544, 0), (544, -16)], floor=0, ceil=0, wall="AJSHUT", ftex="AJTRIMF",
             ctex="AJTRIMF", light=120)
m.thing(512, 64, 1, angle=90)
# the hall NOW: Doom's lamps
for x, y in ((96, 96), (928, 96), (96, 672), (928, 672)):
    t.now.thing(x, y, 2028)                                                      # floor lamps
# --- the doorway to the vestibule: THEN open; NOW bolted on the vestibule's side
t.then.opening((1024, 352), (1024, 416), (1, 0))
ajarmap.bolted(m, (1024, 352), (1024, 416), (1, 0), 0, BOLTS)

# =================================================================================================
# 2. THE VESTIBULE
# =================================================================================================
VEST = look(AR, FR, KA)
BOOTH = (1104, 224, 1232, 288)              # the pass office THEN, against the south wall; NOW its footprint
fit(t.now, (1040, 224, 1296, 544), [((1232, 272, 1264, 336), dict(floor=-20, side=Part("B4"))),
                                    ((1264, 272, 1296, 336), dict(floor=-40, side=Part("B4"))),
                                    ((1104, 432, 1200, 496), dict(ftex="AJIFR2")),    # the porter's desk's footprint
                                    (BOOTH, dict(ftex="AJIFR2"))], **VEST)
fit(t.then, (1040, 224, 1296, 544), [((1104, 432, 1200, 496), box(40, "DT", "DS")),          # the porter's desk
                                     ((1256, 440, 1296, 504), dict(floor=-16, side=Part("B4"))),
                                     (BOOTH, None)], **VEST)
# (the turnstile's step: down 16 before the squeeze, whose ceiling (-20 + 64) leaves 60 over it; 56 over the
# vestibule's floor would not let the player in)
t.far((1136, 224), (1200, 224), (0, -1), BLUE)                                 # BLUE's far side, NOW and THEN
t.line((1136, 224), (1200, 224), upper=AR)
# THEN the pass office, around BLUE's far side: locked for the night, solid below and glazed above (nothing
# passes), PASSES over it; inside, the megasphere, and its floor is a secret (the lobby NOW no longer). Reached only through
# BLUE hung in a frame THEN, left only back through it (region boothT).
GLASS = dict(mid="AJGLAS", midboth=True, blocking=True, blockeverything=True, blockhitscan=True,
             blockprojectiles=True)
COUNTER = dict(floor=24, ceil=112, wall=AR, ftex=Part("DT"), ctex=KA, side=Part("DS"))
BOOTH_IN = dict(ceil=H, wall=AR, ftex=FR, ctex=KA, light=200)
t.then.room((1112, 224, 1224, 280), floor=0, special=1024, **BOOTH_IN)           # where BLUE lets one in: the secret
for r in ((1104, 280, 1232, 288), (1104, 224, 1112, 280), (1224, 224, 1232, 280)):
    t.then.room(r, **COUNTER)
for a, b in (((1104, 288), (1232, 288)), ((1104, 224), (1104, 288)), ((1232, 224), (1232, 288)),
             ((1112, 280), (1224, 280)), ((1112, 224), (1112, 280)), ((1224, 224), (1224, 280))):
    t.then.line(a, b, **GLASS)
sign(t.then, (1232, 288), (1104, 288), (0, -1), AR, "PASSES", 112)
t.then.thing(1168, 256, 83)                                                     # the megasphere, seen over the counter
ajarmap.unbolt(m, (1136, 224), (1200, 224), BOLTS)                              # arriving draws both bolts
ajarmap.bolted(m, (1312, 272), (1312, 336), (-1, 0), LOW, BOLTS)               # to the corridor (NOW)
# THEN: the goods edge (out with a door, never in) and the turnstile (empty hands, both ways)
t.then.room((1296, 272, 1312, 368), floor=0, ceil=128, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF", light=200)
t.then.line((1296, 272), (1296, 368), upper=AR)
ajarmap.squeeze(m, t.then.P((1296, 448)), t.then.P((1296, 496)), (1, 0), -20)
t.then.line((1296, 448), (1296, 496), upper=AR)
# THEN the pass and key board behind the porter's desk, the notice by the turnstile, a small thing on the desk;
# NOW where they hung (the south wall's strip is the pass office's: nothing of the apparatus there)
picture((1088, 544), (1216, 544), (0, 1), "PB", "AR")
ghost((1088, 544), (1216, 544), (0, 1), "AR", [GL.RECT["PB"]])
picture((1296, 376), (1296, 440), (1, 0), "NT", "AR")
ghost((1296, 376), (1296, 440), (1, 0), "AR", [GL.RECT["NT"]])
apparatus(1176, 476, SMALL_T)

# =================================================================================================
# 3. THE CORRIDOR (NOW) / THE POCKET (THEN)
# =================================================================================================
CORR = look(CO, FC, KC, LOW)
t.now.room((1312, 160, 1504, 2256), **CORR, light=104)
t.then.room((1312, 160, 1504, 640), **CORR)
t.then.room((1312, 640, 1504, 704), **dict(CORR, light=40))                     # beyond the night grille: dark
t.then.line((1312, 640), (1504, 640), mid="AJGRIL", midboth=True, blocking=True, dontpegbottom=True)
sign(t.then, (1312, 272), (1312, 368), (-1, 0), "CO", "NO DOORS BEYOND THIS POINT", 168)
t.then.line((1312, 448), (1312, 496), upper=CO)
for c in t.copies:
    hang(c, (1312, 512), (1312, 640), "NB")                                     # the clock in the pocket's stretch
picture((1504, 256), (1504, 384), (1, 0), "WN", "CO")                          # THEN a wall newspaper; NOW its ghost
ghost((1504, 256), (1504, 384), (1, 0), "CO", [GL.RECT["WN"]])
apparatus(1468, 194, TROLLEY_T)                                                 # a trolley parked in the corner
frame((1504, 448), (1504, 512), (1, 0), 103, CO, LOW, clock=(NOW,))
frame((1344, 160), (1408, 160), (0, -1), 104, CO, LOW)                         # the stretch's south end: any door, both times

# =================================================================================================
# 4. THE CELLAR (the valve: undo a cause)
# =================================================================================================
# --- THE CAUSES MADE READABLE (PLAN.md, "MAP21: the causes made readable"), sections 4 to 6: THEN the
# device does the thing, small; NOW its wreck is at the same spot and the result where it was putting
# it; the frame faces the spot that changes, the lever is on the frame's own wall beside it, the
# target(s) at the device opposite. Over each lever, at both times, a name plate. The pictures asked
# for here are drawn by tools/gfx_then.py (make_longrun); the things are map21.zs's.
GOODS_T, WRECK_T, STREAM_T, RUMBLE_T = 20188, 20189, 20191, 20192
PICTURES = {}       # (kind, look, part, shift, words): texture name, for gfx_then.make_longrun


def picture(c, kind, part, a, b, out, words=""):
    """A picture of `kind` (gfx_then.make_longrun: L a live lever THEN, D a dead one NOW, F the shut
    goods-in flap, P the pipe, B the plan board, S a wall's letter over where the beam strikes it) on the
    copy's wall `part` for the wall piece a-b seen looking `out`, its wall laid as the wall around it is."""
    key = (kind, c.look, part, I1._shift(c.P(a), c.P(b), out), words)
    return PICTURES.setdefault(key, f"AJ21{kind}{len(PICTURES):02d}")


def lever_plate(a, b, out, cause, words, part):
    """The cause's lever on the wall piece a-b (seen looking `out`), with a plate `words` over it."""
    t.lever(a, b, cause, tex={NOW: picture(t.now, "D", part, a, b, out, words),
                              THEN: picture(t.then, "L", part, a, b, out, words)})


PIT, WATER, LEDGE = -200, -72, -56
STEPS = [(1056 - 32 * (i + 1), LOW + (PIT - LOW) * (i + 1) // 7) for i in range(7)]       # x of each step's west edge, its floor
CELLAR = look(LA, FA, KA, LOW)
TANKS = [(672, 1104, 736, 1168), (864, 1520, 928, 1584), (736, 1520, 800, 1584)]     # 64 square, 256 high (TK)
PUMP = (576, 1104, 672, 1168)                       # the valve's pump, under its pipe run, west of its tank
CELLAR_CONSOLE = (1136, 1552, 1232, 1600)           # on the landing, against its north wall
for c in t.copies:
    tag = dict(id=BASIN) if c.now else {}
    feats = [((576, 1088, 1056, 1600), dict(floor=PIT, ftex=Part("FP"), **tag)),
             ((576, 1280, 704, 1472), dict(floor=LEDGE, side="AJULF3" if c.now else "AJULF2", ftex=Part("FA"), **tag))]
    feats += [((x, 1088, x + 32, 1184), dict(floor=f, side=Part("B4"), **tag)) for x, f in STEPS]
    if c.then:                                                                      # THEN: tanks in the dry pit
        feats += [(r, dict(floor=PIT + 256, ftex=ap("TT", "tanks"), side=ap("TK", "tanks"))) for r in TANKS]
        feats += [(PUMP, dict(floor=PIT + 48, ftex=ap("PT", "pumps"), side=ap("PM", "pumps"))),
                  (CELLAR_CONSOLE, dict(floor=LOW + 48, ftex=ap("CK", "consoles"), side=ap("CN", "consoles")))]
    else:                                                                           # NOW: where they stood
        feats += [(r, dict(ftex="AJIFP2")) for r in TANKS + [PUMP]]
        feats += [(CELLAR_CONSOLE, dict(ftex="AJIFA2"))]
    fit(c, (576, 1088, 1232, 1600), feats, **CELLAR)
room_door((1312, 1440), (1312, 1504), (-1, 0), LOW, CO, LA, "CELLAR", thick=80)
frame((1232, 1248), (1232, 1312), (1, 0), 105, LA, LOW)
# the store (NOW): behind a pressure door in the pit's north wall; it cannot see 105
t.now.room((608, 1632, 736, 1760), floor=PIT, ceil=PIT + 128, wall=LA, ftex=FP, ctex=KA, light=96)
W.pressure_door(m, (640, 1600), (704, 1600), (0, 1), PIT, PDOOR, (BASIN, 0), LAMP,
                look=dict(wall="SPCDOOR1", ftex="FLAT20", ctex="FLAT20"), strip=dict(wall="SUPPORT2", ftex="FLAT20"))
ajarmap.key(m, 2, 672, 1712)
W.basin(m, BASIN, 480 * 512, LOW, floor=PIT, at=(800, 1350))
W.rate(m, 900, 1350, 0, 0, W.FLOAT)                                             # the player floats up when idle in it
t.cause(1144, 1500, VALVE, 2, basin=BASIN, depth=WATER - PIT, start=1)           # 0 shut (dry), 1 open (full): found open
lever_plate((1232, 1328), (1232, 1392), (1, 0), VALVE, "VALVE", LA)             # on the landing's east wall, beside 105
t.target(588, 1376, VALVE, z=44)                                                # on the ledge, across the pit: 105 sees it
apic((576, 1312), (576, 1440), (-1, 0), "GB", "LA", group="pumps")              # the valve's gauges, over the target
ghost((576, 1312), (576, 1440), (-1, 0), "LA", [GL.RECT["GB"]])                 # (NOW where they hung)
apic((1072, 1600), (1136, 1600), (0, 1), "PP", "LA")                            # on the landing: a pipe run THEN,
ghost((1072, 1600), (1136, 1600), (0, 1), "LA", [GL.RECT["PP"]])                # its ghost NOW; the console's ghost
ghost((1136, 1600), (1232, 1600), (0, 1), "LA", [(0, 208, 96, 256)], (2,))
# the pipe on the pit's west wall, just south of the ledge, at both times: its mouth at MOUTH, over NOW's
# water. Open, a thin stream falls from it: THEN to the pit's floor (a wet patch there), NOW onto the water;
# shut, the pipe is dry (AjarStream, map21.zs, shown by the valve's setting at once)
MOUTH, PIPE = -16, ((576, 1216), (576, 1280))
for c in t.copies:
    c.cut(*PIPE)
    c.line(*PIPE, mid=picture(c, "P", LA, *PIPE, (-1, 0)), exact=True)
    c.thing(582, 1248, STREAM_T, args=(VALVE, 1, MOUTH - PIT, BASIN if c.now else 0))
for c in t.copies:
    hang(c, (1088, 1088), (1216, 1088), "NB")                                   # the clock on the landing

# =================================================================================================
# 5. THE GOODS BAY (the belt: make a cause)
# =================================================================================================
BAY = look(AR, FR, KA, LOW)
UP_ = 56                                                                         # the gallery
RACKS = [(1616, 1376, 1696, 1440), (1760, 1376, 1840, 1440)]
MOTOR = (1568, 1216, 1632, 1264)                    # THEN the belt's motor, at the flap's end, north of the belt
BAY_CONSOLE = (1760, 1488, 1840, 1536)              # THEN a console against the north wall, west of the lever
HEAP_STEPS = [(1840, -64, -16), (1904, -88, 8), (1968, -112, 32)]               # x, floor standing (0), running (1)
# The belt, at both times: out of the goods-in flap in the west wall, east along the south side to the hatch
# (the heap's footprint). THEN it runs and crates ride it into the hatch, an open hole, railed (players may
# not cross its rail, monsters not its north side; crates drop through), dark inside; new ones come out of the flap
# (AjarGoodsIn, map21.zs). NOW the same belt, rusted and still; the flap shut; the crates that stood on it
# THEN stand on it in dust while it never ran; the hatch is the stair down or under the heap.
FLAP, BELT_END, HATCH = 1520, 1840, (1840, 1088, 2032, 1216)        # the goods-in alcove THEN is FLAP..1568
HATCH_FLOOR = LOW - 128
BELT_SPEED = 2          # units a tic: a crate takes about 4 s from the flap to the hatch (MODE=4 measures it)
for c in t.copies:
    feats = [((2032, 1088, 2160, 1536), dict(floor=UP_, side=Part("B6"), ftex=Part("FA")))]
    feats += [((1568, 1120, BELT_END, 1216), None)]                                 # the belt's band
    if c.now:
        feats += [((x, 1088, x + 64, 1216), dict(floor=f0, side="AJDSTOR", id=HEAP,
                                                 raw=heights(floors=(f0, f1), raised="AJDSTOF")))
                  for x, f0, f1 in HEAP_STEPS]
        feats += [(r, dict(ftex="AJIFR2")) for r in RACKS + [MOTOR, BAY_CONSOLE]]  # where the apparatus stood
    else:
        feats += [(HATCH, None)]
        feats += [(r, dict(floor=LOW + 96, ftex=ap("RT", "racks"), side=ap("RS", "racks"))) for r in RACKS]
        feats += [(MOTOR, dict(floor=LOW + 48, ftex=ap("BT", "belt"), side=ap("BM", "belt"))),
                  (BAY_CONSOLE, dict(floor=LOW + 48, ftex=ap("CK", "consoles"), side=ap("CN", "consoles")))]
    fit(c, (1568, 1088, 2160, 1536), feats, **BAY)
    first = len(m.sectors)
    ajarmap.belt(m, c.P((1568, 1168)), c.P((BELT_END, 1168)), BELT_TAG if c.then else 0, floor=LOW, scroll=False,
                 light=c.light)
    for sec in m.sectors[first:]:                                               # under the room's own ceiling
        sec.update(ceil=LOW + H, ctex=c.tex(KA), wall=c.tex(AR))
        bed = sec["ftex"] == "FLAT20"
        if c.now:                                                               # rusted and still
            sec.update(ftex="AJ21BT3" if bed else "AJ21CT3", side="AJ21CS3")
        else:                                                                   # THEN new: the apparatus's belt
            sec.update(ftex=ap("BB" if bed else "BC", "belt"), side=ap("BS", "belt"))
    if c.then:
        # the goods-in alcove behind the flap: low and dark, where the crates come from out of sight
        first = len(m.sectors)
        ajarmap.belt(m, c.P((FLAP, 1168)), c.P((1568, 1168)), BELT_TAG, floor=LOW, scroll=False, light=48)
        for sec in m.sectors[first:]:
            sec.update(ceil=LOW + 40, ctex="FLAT20", wall=c.tex(AR), side=ap("BS", "belt"),
                       ftex=ap("BB" if sec["ftex"] == "FLAT20" else "BC", "belt"))
        for y1, y2 in ((1120, 1136), (1136, 1200), (1200, 1216)):
            c.line((1568, y1), (1568, y2), dontpegtop=True, **(dict(mid="AJ21FLP") if y1 == 1136 else {}))
        # the hatch: a rim of 8 at the floor along the walls, and the hole, dark (its ceiling lit as the room's)
        x1, y1, x2, y2 = HATCH
        for r in ((x1, y1, x2, y1 + 8), (x2 - 8, y1 + 8, x2, y2)):
            c.room(r, floor=LOW, ceil=LOW + H, wall=AR, side="SUPPORT2", ftex=FR, ctex=KA)
        c.room((x1, y1 + 8, x2 - 8, y2), floor=HATCH_FLOOR, ceil=LOW + H, wall=AR, ftex="CEIL5_1", ctex=KA, light=40,
               raw=dict(lightceiling=c.light, lightceilingabsolute=True))
        c.line((x1, y2), (x2, y2), mid="AJ21RAL", blockplayers=True, blockmonsters=True)     # its rail, posts and a bar
        # over the belt's end the bar only, and players only: a monster-blocking line stops every thing that
        # is not a player, crates too (THEN has no monsters but those come through a door)
        c.line((x1, y1), (x1, y2), mid="AJ21RAW", blockplayers=True)
    else:
        c.cut((1568, 1136), (1568, 1200))                                           # the flap, shut
        c.line((1568, 1136), (1568, 1200), mid=picture(c, "F", AR, (1568, 1136), (1568, 1200), (-1, 0)),
               dontpegbottom=True)
for x1, y1, x2, y2 in RACKS:                                                    # THEN the racks' long faces
    for y in (y1, y2):
        t.then.cut((x1, y), (x2, y))
        t.then.line((x1, y), (x2, y), lower=ap("RF", "racks"))
ghost((1568, 1216), (1568, 1264), (-1, 0), "AR", [(0, 208, 48, 256)], (1,))     # NOW where the motor stood
ghost((1760, 1536), (1840, 1536), (0, 1), "AR", [(0, 208, 80, 256)], (2,))      # ... and the console
room_door((1504, 1280), (1504, 1344), (1, 0), LOW, CO, AR, "GOODS")
frame((1904, 1536), (1968, 1536), (0, 1), 108, AR, LOW)                       # looking straight at the hatch
lever_plate((1840, 1536), (1904, 1536), (0, 1), BELT, "BELT", AR)               # beside it
# the bay cellar (NOW): the hatch stair's foot, south of the last step; and a secret beside it
t.now.room((1968, 1024, 2032, 1088), floor=-112, ceil=-40, wall="SUPPORT2", ftex="FLAT20", ctex="FLAT20", light=110)
t.now.room((1904, 880, 2096, 1024), floor=-112, ceil=16, wall=PU, ftex=FP, ctex=KP, light=110)
t.now.room((2096, 912, 2112, 976), floor=-112, ceil=-16, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF", light=100)
t.now.room((2112, 880, 2240, 1008), floor=-112, ceil=16, wall=PU, ftex=FP, ctex=KP, light=90, special=1024)
t.now.thing(2000, 940, 82)                                                      # the super shotgun
ajarmap.door(m, GREEN, 1928, 952, angle=0)                                      # GREEN, against the west wall
t.cause(1700, 1300, BELT, 2, tag=HEAP)                                          # 0 standing (found), 1 running
t.belt_run(1700, 1340, BELT, BELT_TAG, (BELT_SPEED, 0))
t.then.thing(1544, 1168, GOODS_T, args=(BELT, 4, 68, 1568 - 1544))             # the goods-in: 4 crates on it, 68 apart
t.target(1936, 1100, BELT, z=LOW + 46 - HATCH_FLOOR)                            # over the hatch, clear of its rail
t.now.thing(1936, 1152, RUMBLE_T, args=(BELT,))                                 # NOW: the heap's rumble while it moves
ajarmap.door(m, RED, 2096, 1480, angle=270)                                     # on the gallery

# =================================================================================================
# 6. OPTICS (the beam: choose a cause)
# =================================================================================================
OPT = look(LA, FA, KA, LOW)
OPT_BENCHES = [(1216, 2400, 1312, 2448), (1216, 2688, 1296, 2736)]       # clear of the lines from 126 to the targets and of the beams
for c in t.copies:
    feats = [((1344, 2512, 1472, 2640), dict(ftex=Part("FN")))]                     # an inlay under the emitter, both times
    feats += [(r, dict(floor=LOW + 48, ftex=ap(("OTA", "OTB")[i], "benches"), side=ap("OB", "benches")) if c.then
               else dict(ftex="AJIFA2")) for i, r in enumerate(OPT_BENCHES)]
    if c.now:       # light from a gap in the roof along the north wall, and on the walls A and C: the plan board
        feats += [((1152, 2704, 1664, 2832), dict(light=184)),       # and the plates read from 106 and through it
                  ((1152, 2480, 1216, 2672), dict(light=168)), ((1600, 2480, 1664, 2672), dict(light=168))]
    fit(c, (1152, 2320, 1664, 2832), feats, **OPT)
    hang(c, (1664, 2672), (1664, 2800), "NB")
room_door((1376, 2256), (1440, 2256), (0, 1), LOW, CO, LA, "OPTICS")
frame((1536, 2320), (1600, 2320), (0, -1), 106, LA, LOW)
lever_plate((1600, 2320), (1664, 2320), (0, -1), BEAM, "BEAM", LA)              # beside 106
# opposite 106 on the north wall, at both times (NOW faded): the plan board, the room as one faces it, the
# emitter in the middle (OFF), A the west wall on the left, B the north wall at the top, C the east wall on
# the right. THEN its four targets sit on it at those places (B and OFF 24 apart across, so that a shot,
# autoaimed or not, takes the one aimed at)
BOARD = ((1472, 2832), (1664, 2832))
for c in t.copies:
    c.cut(*BOARD)
    c.line(*BOARD, mid=picture(c, "B", LA, *BOARD, (0, 1)), exact=True)
BOARD_TARGETS = ((1556, 0, 72), (1504, 1, 72), (1580, 2, 136), (1632, 3, 72))     # x, setting, the middle's height
OPEN = LOW + 96
HOLE_AT = {1: ((1136, 2544, 1152, 2608), (1008, 2512, 1136, 2640), (1152, 1136)),       # A, west: hole, closet, faces
           2: ((1376, 2832, 1440, 2848), (1344, 2848, 1472, 2976), (2832, 2848)),       # B, north
           3: ((1664, 2544, 1680, 2608), (1680, 2512, 1808, 2640), (1664, 1680))}       # C, east
for n, (hole, closet, faces) in HOLE_AT.items():
    ceils = tuple(OPEN if s == n else LOW for s in range(4))
    t.now.room(hole, floor=LOW, ceil=ceils[3], wall="ASHWALL2", ftex="AJTRIMF", ctex="AJTRIMF", id=HOLES,
               raw=heights(ceils=ceils, hold=True))
    t.now.room(closet, floor=LOW, ceil=LOW + 128, wall=LA, ftex=FA, ctex=KA, light=100,
               **(dict(special=1024) if n == 2 else {}))
    x1, y1, x2, y2 = hole
    look_at = {1: (-1, 0), 2: (0, 1), 3: (1, 0)}[n]
    for f in faces:                                                                 # shut, the wall goes on over it
        a, b = ((f, y1), (f, y2)) if n != 2 else ((x1, f), (x2, f))
        if f == faces[0]:                   # the room's side: its letter over it, at both times (THEN where the beam strikes)
            t.now.line(a, b, upper=picture(t.now, "S", LA, a, b, look_at, "ABC"[n - 1]), dontpegtop=True)
            t.then.cut(a, b)
            t.then.line(a, b, mid=picture(t.then, "S", LA, a, b, look_at, "ABC"[n - 1]), exact=True)
        else:
            t.now.line(a, b, upper=LA, dontpegtop=True)
t.cause(1408, 2700, BEAM, 4, tag=HOLES, start=3)                                # 0 off, 1 A, 2 B, 3 C: found at C
t.beam(1408, 2576, BEAM, (180, 90, 0))
t.now.thing(1408, 2576, WRECK_T, args=(APPARATUS["emitter"],))                   # NOW: the emitter's wreck, on the inlay
t.then.thing(1408, 2576, EMITTER_LOOK_T, args=(APPARATUS["emitter"], 0, BEAM))      # THEN: the emitter, lit or OFF
apparatus(1184, 2352, TALL_T, solid=True)                                       # tall pieces in the west corners
apparatus(1184, 2800, TALL_T, solid=True)
apic((1152, 2400), (1152, 2464), (-1, 0), "PP", "LA")                           # a pipe run on the west wall
ghost((1152, 2400), (1152, 2464), (-1, 0), "LA", [GL.RECT["PP"]])
for x, setting, z in BOARD_TARGETS:                                             # off, A, B, C: on the plan board
    t.target(x, 2820, BEAM, setting, z=z - 10 - LOW)
ajarmap.door(m, BLUE, 1056, 2576, angle=0)                                      # behind A
t.now.thing(1416, 2920, 2013)                                                   # behind B, the secret: a soul sphere
t.now.thing(1376, 2900, 2046)                                                   # ... rockets
t.now.thing(1744, 2576, 2003)                                                   # behind C: the rocket launcher
t.now.thing(1760, 2540, 2046)

# =================================================================================================
# 7. THE LOBBY (MAP11's, 2560 east): RED's far side THEN; frame 110
# =================================================================================================
LX = 2560
LOBBY = look(LB, FL, KL)
for c in t.copies:
    feats = [((LX + 384, 352, LX + 640, 416), box(40, "DT", "DS")),
             ((LX + 224, 160, LX + 288, 224), pillar("PI")), ((LX + 736, 160, LX + 800, 224), pillar("PI")),
             ((LX + 224, 416, LX + 288, 480), pillar("PI")), ((LX + 736, 416, LX + 800, 480), pillar("PI"))]
    fit(c, (LX, 0, LX + 1024, 640), feats, **LOBBY)
    fit(c, (LX - 336, 64, LX - 16, 256), [((LX - 336, 64, LX - 304, 256), box(48, "UT", "US"))],
        floor=0, ceil=160, wall=CK, ftex=FC, ctex=KC, light=c.light - 40)
    c.opening((LX, 128), (LX, 192), (-1, 0))
    c.line((LX, 128), (LX, 192), upper=LB)
    c.line((LX - 16, 128), (LX - 16, 192), upper=CK)
    hang(c, (LX + 448, 0), (LX + 576, 0), "ST")                                    # the street doors
    hang(c, (LX + 64, 640), (LX + 320, 640), "MO")
    hang(c, (LX + 768, 640), (LX + 896, 640), "NB")
    for y in (64, 128, 192):
        hang(c, (LX - 336, y), (LX - 336, y + 64), "CT")
    c.cut((LX + 384, 640), (LX + 640, 640))                                         # the way north, sealed
    c.line((LX + 384, 640), (LX + 640, 640), mid="AJSHUT" if c.then else STONE, exact=True)
t.far((LX, 288), (LX, 352), (-1, 0), RED)                                      # RED's far side, NOW and THEN
t.line((LX, 288), (LX, 352), upper=LB)
frame((LX + 1024, 288), (LX + 1024, 352), (1, 0), 110, LB)
t.then.thing(LX + 512, 470, ajarmap.KEY_T["1"])                                 # key 1, on the porter's board behind the desk
t.then.thing(LX - 240, 160, 8)                                                  # a backpack in the cloakroom
for x, y, k in ((LX + 300, 300, 18), (LX + 700, 120, 19), (LX + 820, 520, 20), (LX + 160, 560, 15), (LX + 600, 200, 10)):
    t.now.thing(x, y, k)                                                        # MAP11's fight, forty years on

# =================================================================================================
# THE FIGHTS AND WHAT IS PICKED UP (Doom's monsters NOW; THEN is quiet but for key 1's ambush)
# =================================================================================================
AREAS = {   # name: the box things stand in (NOW's coordinates unless THEN), its copy
    "hall": ((48, 480, 976, 736), NOW), "hallS": ((48, 48, 360, 288), NOW),
    "corrS": ((1328, 560, 1488, 1000), NOW), "corrM": ((1328, 1000, 1488, 1900), NOW),
    "corrN": ((1328, 1900, 1488, 2240), NOW),
    "landing": ((1072, 1104, 1216, 1584), NOW), "pit": ((720, 1200, 1040, 1584), NOW),
    "bay": ((1584, 1232, 2016, 1520), NOW), "gallery": ((2040, 1104, 2152, 1440), NOW),
    "baycell": ((1912, 888, 2088, 1016), NOW),
    "optics": ((1168, 2336, 1648, 2816), NOW),
    "lobbyT": ((LX + 320, 40, LX + 992, 150), THEN), "lobbyE": ((LX + 850, 180, LX + 1000, 600), THEN),
}
AVOID = [(512, 300), (512, 64), (512, 160), (512, 230), (1040, 384), (1168, 240), (1490, 480), (1296, 304), (1248, 1280), (1300, 1472),
         (1520, 1312), (1936, 1520), (1408, 2272), (1568, 2336), (1408, 2576), (LX + 1008, 320), (LX + 16, 320),
         (2096, 1480), (1056, 2576), (1144, 1500), (LX + 512, 470),
         (1000, 1136), (1200, 1360), (672, 1616), (1408, 2700), (720, 1560), (1632, 2352),
         (1376, 176), (1928, 952)]                                       # frame 104's mouth, GREEN
TAKEN = []
R = {CACO: 31, MANCUBUS: 48, ARACH: 64, BARON: 24, KNIGHT: 24, DEMON: 30, SPECTRE: 30}
PART_OF = []            # (thing index, part) for every monster and pickup: the budget by part
PROBLEMS = []


def halton(i, b):
    f, r = 1, 0
    while i:
        f /= b
        r += f * (i % b)
        i //= b
    return r


def spot(name, r=20):
    """A free place for a thing of radius r in area `name` (a Halton sequence: the same every build)."""
    (x1, y1, x2, y2), when = AREAS[name]
    for k in range(1, 4000):
        x = round((x1 + r + halton(k, 2) * (x2 - x1 - 2 * r)) / 8) * 8
        y = round((y1 + r + halton(k, 3) * (y2 - y1 - 2 * r)) / 8) * 8
        if not (x1 + r <= x <= x2 - r and y1 + r <= y <= y2 - r):
            continue
        if any(max(abs(x - tx), abs(y - ty)) < r + tr + 8 for tx, ty, tr, tw in TAKEN if tw == when):
            continue
        if any(math.hypot(x - ax, y - ay) < 72 + r for ax, ay in AVOID):
            continue
        px, py = t.copies[when].P((x, y))
        if any(math.hypot(px - th["x"], py - th["y"]) < r + 28 for th in m.things):     # lamps, pickups, the others
            continue
        TAKEN.append((x, y, r, when))
        return x, y
    PROBLEMS.append(f"no room in {name}")
    return x1 + 64, y1 + 64


def mark(part, first):
    PART_OF.extend((i, part) for i in range(first, len(m.things)))


def put(part, name, kind, n, angle=0):
    first = len(m.things)
    for _ in range(n):
        x, y = spot(name, R.get(kind, 20))
        t.copies[AREAS[name][1]].thing(x, y, kind, angle=angle)
    mark(part, first)


def ambush(part, name, cause, kind, n, *, arg=None, angle=0, after=0, near=0):
    """An ambush of n at free spots of `name`: ajarmap's (cause 1..49), or
    ajarthen's (cause 62, 63: `arg`), or the water's (61: `arg` (tag, height))."""
    first = len(m.things)
    spots = [t.copies[AREAS[name][1]].P(spot(name, R.get(kind, 20))) for _ in range(n)]
    if cause == W.AMBUSH_UNDER:
        W.water_ambush(m, False, arg[0], arg[1], kind, *spots, angle=angle, after=after, near=near)
    elif cause >= 62:
        ajarthen.ambush(m, cause, arg, kind, *spots, angle=angle, after=after, near=near)
    else:
        ajarmap.ambush(m, cause, kind, *spots, angle=angle, after=after, near=near)
    mark(part, first)


def items(part, *spec):
    """Pickups: (x, y, kind) in NOW's coordinates, or (x, y, kind, THEN)."""
    first = len(m.things)
    for x, y, kind, *when in spec:
        t.copies[when[0] if when else NOW].thing(x, y, kind)
    mark(part, first)


# --- the hall: the start's shotgun; it wakes when the bolts are drawn (the level's biggest fight)
items("hall", (384, 64, 2001), (640, 64, 2049), (400, 160, 2049), (624, 160, 2048), (160, 400, 2046),
      (864, 400, 2046), (160, 560, 17), (864, 560, 17), (128, 240, 2012), (896, 240, 2012), (512, 200, 2018),
      (288, 112, 2049), (736, 112, 2049))
ambush("hall", "hall", ajarthen.AMBUSH_BOLTS, MANCUBUS, 2, arg=BOLTS, angle=270)
ambush("hall", "hall", ajarthen.AMBUSH_BOLTS, KNIGHT, 3, arg=BOLTS, angle=270, after=1)
ambush("hall", "hall", ajarthen.AMBUSH_BOLTS, REVENANT, 2, arg=BOLTS, angle=270, after=2)
ambush("hall", "hall", ajarthen.AMBUSH_BOLTS, CACO, 3, arg=BOLTS, angle=270, after=3)
ambush("hall", "hall", ajarthen.AMBUSH_BOLTS, BARON, 1, arg=BOLTS, angle=270, after=4)
ambush("hall", "hallS", ajarthen.AMBUSH_BOLTS, IMP, 4, arg=BOLTS, angle=90, after=2)
# --- the corridor: the first fight on stepping out of 103; chaingunners at its far end; demons from the rooms
items("corridor", (1456, 400, 2002), (1360, 400, 2048), (1360, 1200, 2048), (1456, 1700, 2049), (1360, 2000, 2049),
      (1456, 2100, 2048), (1456, 900, 2011), (1360, 1600, 2012), (1408, 1100, 2049), (1456, 1500, 2048),
      (1408, 1950, 2015), (1360, 640, 2049))
put("corridor", "corrS", ZOMBIE, 6, 270)
put("corridor", "corrS", SERGEANT, 4, 270)
put("corridor", "corrS", IMP, 4, 270)
put("corridor", "corrM", IMP, 4, 270)
put("corridor", "corrM", DEMON, 4, 270)
put("corridor", "corrM", SERGEANT, 2, 270)
put("corridor", "corrN", CHAINGUNNER, 4, 270)
put("corridor", "corrN", IMP, 3, 270)
# --- the cellar: on the landing; spectres and demons in the dry pit, a knight by the store; cacodemons and
# lost souls over the water when it first stands full again. On the ledge the plasma rifle.
items("cellar", (640, 1376, 2004), (656, 1440, 2047), (640, 1312, 2019), (1080, 1560, 2049), (1200, 1120, 2048),
      (1176, 1560, 2012), (900, 1500, 2046), (1000, 1250, 17))
put("cellar", "landing", IMP, 3, 180)
put("cellar", "landing", SERGEANT, 3, 180)
ambush("cellar", "pit", W.AMBUSH_UNDER, SPECTRE, 3, arg=(BASIN, PIT + 8), angle=0, after=1)
ambush("cellar", "pit", W.AMBUSH_UNDER, DEMON, 3, arg=(BASIN, PIT + 8), angle=0, after=2)
first = len(m.things)
W.water_ambush(m, False, BASIN, PIT + 8, KNIGHT, (720, 1560), angle=270, after=3)
mark("cellar", first)
ambush("cellar", "pit", ajarthen.AMBUSH_CAUSE, CACO, 3, arg=VALVE * 16 + 1, angle=0, after=1)
ambush("cellar", "pit", ajarthen.AMBUSH_CAUSE, SOUL, 4, arg=VALVE * 16 + 1, angle=0, after=2)
# --- the goods bay: among the racks and on the gallery; revenants; an ambush when RED is taken
items("bay", (1600, 1500, 2049), (1640, 1500, 2048), (2120, 1120, 2046), (2000, 960, 2049), (1960, 960, 2049),
      (1600, 1260, 2012), (1800, 1500, 2008), (1840, 1500, 2008))
put("bay", "bay", SERGEANT, 4, 180)
put("bay", "bay", IMP, 4, 180)
put("bay", "bay", REVENANT, 2, 180)
put("bay", "gallery", IMP, 2, 180)
put("bay", "gallery", SERGEANT, 2, 180)
put("bay", "baycell", IMP, 2, 90)
ambush("bay", "bay", 10 + RED, IMP, 3, angle=0, after=1)
ambush("bay", "bay", 10 + RED, KNIGHT, 2, angle=0, after=2)
ambush("bay", "bay", 10 + RED, CHAINGUNNER, 2, angle=0, after=3)
# ... and when GREEN is taken in the bay cellar: four in the bay above, so that the player climbs the stair into it
ambush("bay", "bay", 10 + GREEN, IMP, 2, angle=270, after=1)
ambush("bay", "bay", 10 + GREEN, KNIGHT, 1, angle=270, after=1)
ambush("bay", "bay", 10 + GREEN, CHAINGUNNER, 1, angle=270, after=2)
# --- optics: knights and an arachnotron; an ambush through the holes when BLUE is taken
items("optics", (1200, 2360, 2047), (1620, 2360, 2047), (1200, 2780, 17), (1620, 2780, 2046), (1300, 2780, 2048),
      (1500, 2780, 2049), (1408, 2360, 2011), (1300, 2360, 2049))
put("optics", "optics", KNIGHT, 3, 270)
put("optics", "optics", ARACH, 1, 270)
put("optics", "optics", IMP, 4, 270)
ambush("optics", "optics", 10 + BLUE, CACO, 2, angle=270, after=1)
ambush("optics", "optics", 10 + BLUE, SOUL, 3, angle=270, after=1)
ambush("optics", "optics", 10 + BLUE, REVENANT, 1, angle=270, after=2)
ambush("optics", "optics", 10 + BLUE, DEMON, 3, angle=270, after=2)
# --- the lobby THEN: key 1 taken, the ruin's monsters come in (THEN's only fight)
items("lobby", (LX + 128, 96, 2049, THEN), (LX + 896, 96, 2048, THEN), (LX + 128, 544, 2046, THEN),
      (LX + 896, 544, 2049, THEN), (LX + 448, 96, 2012, THEN))
ambush("lobby", "lobbyT", 1, IMP, 4, angle=90, after=0)
ambush("lobby", "lobbyT", 1, SERGEANT, 3, angle=90, after=1)
ambush("lobby", "lobbyE", 1, KNIGHT, 1, angle=180, after=1)
ambush("lobby", "lobbyE", 1, CACO, 2, angle=180, after=3)
items("night", (416, 912, 2015), (480, 912, 2015), (544, 912, 2015), (608, 912, 2015))   # the dead night room NOW
items("secrets", (LX + 960, 320, 2019), (2176, 944, 2023), (2200, 920, 2018), (2160, 980, 2046))

# --- the budget, part by part: each part's ammunition does at least 1.6 times its monsters' health (Resident)
SKILLS = m._skills()
BUDGET = {}
for part in dict.fromkeys(p for _, p in PART_OF):
    idx = [i for i, p in PART_OF if p == part]
    for level in (3, 1):
        BUDGET[(part, level)] = budget.reckon([m.things[i] for i in idx], [SKILLS[i] for i in idx], level)
    r = BUDGET[(part, 3)]
    if part != "secrets":
        assert r["dmg"] >= 1.6 * r["hp"], budget.line(part, r, 3)
MONSTERS = {lv: sum(budget.reckon(m.things, SKILLS, lv)["monsters"].values()) for lv in (1, 2, 3, 4)}
assert 110 <= MONSTERS[3] <= 140, MONSTERS
assert not PROBLEMS, PROBLEMS

# =================================================================================================
# THE PUZZLE (tools/puzzle21.py, as built): solved in the full build; nothing stuck, nothing lost
# =================================================================================================
PUZZLE = puzzle21.BUILT

if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["budget"]:
        for (part, level), r in BUDGET.items():
            print(budget.line(part, r, level))
        print("monsters by skill:", MONSTERS)
    else:
        sys.stdout.write(m.textmap())
