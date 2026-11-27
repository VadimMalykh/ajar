"""Act 3, level 3: "Sleeping Dogs" (MAP23). PLAN.md, "MAP23 "Sleeping Dogs": the
first version, as decided" (with its part "Corrected by the solver") and "... the
first playable version"; the lab: "The kennel lab".

The institute's animal house twice: NOW (night, the ruin, Doom's tenants; the runs
open to the hall, their gates and turnstiles gone) and THEN, forty years before
(day; every part locked for the night from the next and entered only by the
clocked door; the specimens in their runs). THEN is NOW + (0, -8192), south of it
(tools/ajarthen.py, src/zscript/then.zs): a monster THEN that is after a player
NOW walks north, so every pen and stall lies on the south side or at the south
end of its run, and one left with its gate open walks away from it.

A monster alive THEN shows NOW as its bones while the clocked door hangs nowhere
(from the first tic); killed THEN, its bones are there for good. Bones weigh (pen
1's scales, AjarKennelScales) and a big one's are a step (AjarKennel, kennel.zs).
Each run THEN has a Doom gate that stocks it (AjarStockGate, map23.zs).

Places (NOW's coordinates; x east, y north):
  yard     (0, -256, 640, 512) the start: line 6's shelter, the clocked door
           leaning in it, a shotgun. North: the house's front door (Doom's, USE;
           THEN locked) into the hall, and frame 101 (the clocked door's alone).
           East: glass onto the big run (nothing passes, monsters do not see
           through), and the big run's gateway (open NOW, shut THEN). THEN
           sealed; behind the shelter a secret.
  hall     (0, 592, 768, 1216) NOW only: the hub.
  kennels  west of the hall: the run (-912, 960, -16, 1216), three pens along its
           south side (pen 1 the scales), the keeper's passage (-1040, 544, -16,
           672) south of the pens with a hatch into each and its leg up the west
           side to the turnstile; frame 102 in the passage's south wall; S1 in it
           (key 1, the super shotgun) and the second shutter (a secret).
  stalls   east: the run (1152, 640, 1408, 1536), at its south end behind a
           funnel the stall (1240, 304, 1320, 496), the passage south of it (frame
           103) and its leg up the east side to the turnstile. NOW the ledge at
           48 along both sides and round the end: key 2 and a soul sphere.
  guards   north of the hall: THEN the isolation run (0, 1280, 768, 1472), frame
           124 in its west end, the turnstile into the passage (0, 1488, 1040,
           1616) north of it, the pen at its east end (784, 1280, 1024, 1472).
           NOW the antechamber (frame 104), a doorway, the guard room: two barons
           and an arch-vile; RED on its far side.
  big run  (656, -896, 912, 560) east of the yard; at its south end behind a
           funnel the crush (720, -1296, 848, -1040). NOW the big one's bones in
           its middle; the ledge round the crush and in its east wall the brass
           door (keys 1 and 2) to the night room. THEN the cyberdemon.
  big run's keeper's passage (560, -1456, 1072, -1312 THEN; -1360 NOW): sealed at
           both times, RED's far side and frame 105; THEN the crush's hatch, the
           pier, the lever behind it.
The checks: src/zscript/map23.zs (MODE=1..4 tools/smoke.sh).
"""
import math

import ajarmap
import ajarthen
import budget
import puzzle23
from ajarmap import RED
from ajarthen import Times, Part, NOW, THEN, heights
from udmf import Map, rect

m = Map()
import gfx_institute
m.align |= gfx_institute.ALIGNED            # MAP11's walls are laid by where they are

OFF = (0, -8192)                            # THEN is south of NOW
t = Times(m, off=OFF, at=(320, 64))

CO, LA, AR, LB = Part("CO"), Part("LA"), Part("AR"), Part("LB")
FL, FC, FA, FR = Part("FL"), Part("FC"), Part("FA"), Part("FR")
KL, KC, KA = Part("KL"), Part("KC"), Part("KA")
STONE = "TANROCK2"                          # Doom's stone NOW
PAD = "GATE3"                               # a Doom gate's pad THEN
TRIM, TRIMF = "AJTRIM", "AJTRIMF"
GLASS = dict(mid="AJGLAS", midboth=True, blocking=True, blockeverything=True, blockhitscan=True,
             blockprojectiles=True, blocksight=True, blocksound=True)
CRUSH_GLASS = {k: v for k, v in GLASS.items() if k != "blocksound"}

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE = 3004, 9, 3001, 3002, 58
CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS, VILE, CYBER = 65, 69, 3003, 66, 3006, 3005, 67, 64, 16

# tags, tids, causes (map23.zs has the same)
KEN_DOGS, STALL_DOGS, BIG_ONE, GUARDS = 2311, 2312, 2313, 2314      # the specimens' tids (not counted as kills)
KEN_RUN, STALL_RUN, BIG_RUN, CRUSH = 2321, 2322, 2323, 2324         # THEN: the sectors a Doom gate watches; the crush
PEN1_GATE, STALL_GATE, ISO_GATE, CRUSH_GATE = 21, 22, 23, 24        # THEN: the gates' causes (tid), lever by lever
GATE_TAG = {PEN1_GATE: 61, STALL_GATE: 62, ISO_GATE: 63, CRUSH_GATE: 64}
S1, S2 = 71, 72                             # NOW: pen 1's shutters (400: key 1; 1000: the secret)
PEN1 = 81                                   # NOW: pen 1's floor, the scales
BRASS_TAG = 2330                            # NOW: the brass door's sector (its ambush when it first opens)
LOCKED = 2340                               # THEN: "Locked for the night." (the house's front door)
BRASS_LINE = 2390                           # its mouth on the crush's side (the tests)
SCALES_T, GATE_T = 20193, 20194             # AjarKennelScales (kennel.zs), AjarStockGate (map23.zs)
HATCH_FLOOR, HATCH_CEIL = 24, 56
LEDGE = 48


def moreids(*tags):
    return {"moreids": " ".join(str(x) for x in tags)}


def fit(c, box, features, **base):
    """The room `box` cut along every feature's edges; a feature's changes, or
    None: no sector there (a pier)."""
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


def hatch(c, box):
    """A feeding hatch: 64 wide, floor 24, 32 high (the lab's): sight and shots pass, nobody walks through."""
    c.room(box, floor=HATCH_FLOOR, ceil=HATCH_CEIL, wall=TRIM, ftex=TRIMF, ctex=TRIMF, light=c.light)


def gate(c, box, cause, high, *, tags=(), start=1):
    """A pen's or a stall's gate THEN: a shutter on its lever (found open), held while anything stands under
    it; NOW gone (open floor). `tags`: more tags for the sector THEN (the run a Doom gate watches)."""
    if c.then:
        c.room(box, floor=0, ceil=high, wall="AJSHUT", ftex=TRIMF, ctex=TRIMF, light=c.light, id=GATE_TAG[cause],
               raw=dict(heights(ceils=(0, high), hold=True), **moreids(*tags)))
        x1, y1, x2, y2 = box
        across = (x2 - x1) > (y2 - y1)
        for e in (((x1, y1), (x2, y1)), ((x1, y2), (x2, y2))) if across else (((x1, y1), (x1, y2)), ((x2, y1), (x2, y2))):
            c.line(*e, upper="AJSHUT", dontpegtop=True)
    else:
        c.room(box, floor=0, ceil=high, wall=TRIM, ftex=TRIMF, ctex=TRIMF, light=c.light)


def shut_gate(c, box, high):
    """A pen's gate THEN that is shut and has no lever (pens 2 and 3): a closed shutter."""
    c.room(box, floor=0, ceil=0, wall="AJSHUT", ftex=TRIMF, ctex=TRIMF, light=c.light)


def turnstile(c, box, along_x):
    """The turnstile THEN (the lab's): a gap 64 wide, 96 high, two block-monsters lines; the player passes
    both ways with a door or without. NOW gone: a plain gap."""
    c.room(box, floor=0, ceil=96, wall="SUPPORT3", ftex="FLAT23", ctex="FLAT23", light=c.light)
    if c.then:
        x1, y1, x2, y2 = box
        for e in ((((x1, y1), (x1, y2)), ((x2, y1), (x2, y2))) if along_x else (((x1, y1), (x2, y1)), ((x1, y2), (x2, y2)))):
            c.line(*e, blockmonsters=True)


def lever_then(a, b, cause):
    """A gate's lever THEN on the 64-long wall piece a-b (USE steps its cause)."""
    t.then.cut(a, b)
    t.then.line(a, b, special=130, args=(cause,), playeruse=True, repeatspecial=True, mid=ajarthen.LEVER[THEN],
                exact=True, dontpegbottom=True)


def stone(c, a, b):
    """NOW: Doom's stone on the wall piece a-b (where a hatch was)."""
    c.cut(a, b)
    c.line(a, b, mid=STONE, exact=True)


def run(c, box, pad_box, tag, ceil):
    """A run: THEN its sectors carry `tag` (its Doom gate watches them) and the gate's pad (Doom's stone, a
    teleporter's, flush with the floor) is cut into it; NOW plain."""
    base = dict(floor=0, ceil=ceil, wall=CO, ftex=FC, ctex=KC, light=c.light)
    if c.then:
        # one whole pad, laid from the box's own corner and as large as the box: the pads are not on the 64 grid
        # (a flat is laid from the world's), and the big one's is 128 square
        w = pad_box[2] - pad_box[0]
        laid = dict(xpanningfloor=float(-pad_box[0] % w), ypanningfloor=float(pad_box[3] % w),
                    xscalefloor=64.0 / w, yscalefloor=64.0 / w)
        fit(c, box, [(pad_box, dict(ftex=PAD, light=c.light + 24, raw=dict(moreids(tag), **laid)))],
            raw=moreids(tag), **base)
    else:
        c.room(box, **base)


# =================================================================================================================
# 1. THE YARD (the start)
# =================================================================================================================
YARD = (0, -256, 640, 512)
SHELTER = (32, 128, 192, 320)
GLASS_Y = (-176, 336)
GATEWAY_Y = (384, 496)


def yard(c):
    fit(c, YARD, [(SHELTER, dict(ceil=112, ctex=KL, light=c.light - 16))], floor=0, ceil=256, wall=LB, ftex=FL,
        ctex="F_SKY1", light=c.light + 16)
    # the glass onto the big run: a strip 16 deep, sill 8, 128 of glass; nothing passes, nobody sees through
    c.room((640, GLASS_Y[0], 656, GLASS_Y[1]), floor=8, ceil=136, wall=TRIM, ftex=TRIMF, ctex=TRIMF, light=c.light)
    for x in (640, 656):
        c.line((x, GLASS_Y[0]), (x, GLASS_Y[1]), **GLASS)
    # the big run's gateway: open NOW, shut THEN
    if c.now:
        c.room((640, GATEWAY_Y[0], 656, GATEWAY_Y[1]), floor=0, ceil=160, wall=TRIM, ftex=TRIMF, ctex=TRIMF,
               light=c.light)
    else:
        for x in (640, 656):
            c.cut((x, GATEWAY_Y[0]), (x, GATEWAY_Y[1]))
            c.line((x, GATEWAY_Y[0]), (x, GATEWAY_Y[1]), mid="AJSHUT", exact=True)
    # the house's front door: NOW Doom's (USE), THEN the institute's, locked for the night
    if c.now:
        c.room((288, 512, 352, 528), floor=0, ceil=96, wall="DOORTRAK", ftex="FLAT20", ctex="FLAT20", light=c.light)
        d = c.room((288, 528, 352, 576), floor=0, ceil=0, wall="BIGDOOR2", ftex="FLAT20", ctex="FLAT20", light=c.light)
        c.room((288, 576, 352, 592), floor=0, ceil=96, wall="DOORTRAK", ftex="FLAT20", ctex="FLAT20", light=c.light)
        for y in (528, 576):
            c.line((288, y), (352, y), back=d, special=12, args=(0, 32, 150), playeruse=True, monsteruse=True,
                   repeatspecial=True)
        for x in (288, 352):
            for y1, y2 in ((512, 528), (576, 592)):
                c.line((x, y1), (x, y2), mid="DOORTRAK", dontpegbottom=True)
    else:
        c.room((288, 512, 352, 528), floor=0, ceil=128, wall=TRIM, ftex=TRIMF, ctex=TRIMF, light=c.light)
        c.line((288, 528), (352, 528), mid="AJHDOR", special=130, args=(LOCKED,), playeruse=True, repeatspecial=True,
               exact=True, dontpegbottom=True)
    # THEN: the secret behind the shelter (a gap in the yard's west wall, a closet)
    if c.then:
        c.room((-16, 192, 0, 256), floor=0, ceil=96, wall=LB, ftex=FL, ctex=KL, light=c.light - 40)
        c.room((-112, 176, -16, 272), floor=0, ceil=96, wall=LB, ftex=FL, ctex=KL, light=c.light - 40, special=1024)


t.both(yard)
t.clock_frame((480, 512), (544, 512), (0, 1), 101, when=(NOW, THEN))
t.line((480, 512), (544, 512), upper=LB, dontpegtop=True)
t.locked(320, 480, LOCKED)
t.clocked(112, 224, 0)                                                  # leaning in the shelter
START = (320, 32)
m.thing(*START, 1, angle=10)                                            # facing the glass: the bones beyond it

# =================================================================================================================
# 2. THE HALL (NOW only)
# =================================================================================================================
HALL = (0, 592, 768, 1216)
n = t.now
n.room(HALL, floor=0, ceil=192, wall=LB, ftex=FL, ctex=KL, light=136)
n.room((-16, 600, 0, 664), floor=0, ceil=128, wall=LB, ftex=FL, ctex=KL, light=128)        # to the kennels' passage
n.room((-16, 1056, 0, 1184), floor=0, ceil=160, wall=LB, ftex=FL, ctex=KL, light=128)      # to the kennels' run
n.room((96, 1216, 160, 1280), floor=0, ceil=128, wall=LB, ftex=FL, ctex=KL, light=128)     # to the antechamber
n.room((768, 1024, 1152, 1152), floor=0, ceil=160, wall=CO, ftex=FC, ctex=KC, light=120)   # to the stalls' run

# =================================================================================================================
# 3. THE KENNELS
# =================================================================================================================
KRUN = (-912, 960, -16, 1216)
PENS = ((-880, -640), (-608, -368), (-336, -96))
PMID = tuple((a + b) // 2 for a, b in PENS)                             # -760, -488, -216
PEN_Y = (688, 944)
KPASS = (-1040, 544, -16, 672)
KLEG = (-1040, 672, -928, 1216)
KTURN = (-928, 1056, -912, 1120)
S1_BOX, CLOSET = (-792, 528, -728, 544), (-808, 448, -712, 528)
S2_BOX, SECRET2 = (-824, 456, -808, 520), (-920, 440, -824, 536)
KPAD = (-144, 1056, -80, 1120)


def kennels(c):
    run(c, KRUN, KPAD, KEN_RUN, 160)
    for i, (x1, x2) in enumerate(PENS):
        tags = dict(id=PEN1) if c.now and i == 0 else dict(raw=moreids(KEN_RUN)) if c.then else {}
        c.room((x1, PEN_Y[0], x2, PEN_Y[1]), floor=0, ceil=128, wall=AR, ftex=FR, ctex=KA, **tags)
        mid = PMID[i]
        box = (mid - 64, PEN_Y[1], mid + 64, PEN_Y[1] + 16)
        if i == 0:
            gate(c, box, PEN1_GATE, 128, tags=(KEN_RUN,))
        elif c.then:
            shut_gate(c, box, 128)
        else:
            gate(c, box, PEN1_GATE, 128)
        hatch(c, (mid - 32, 672, mid + 32, 688))
    c.room(KPASS, floor=0, ceil=128, wall=LA, ftex=FA, ctex=KA)
    c.room(KLEG, floor=0, ceil=128, wall=LA, ftex=FA, ctex=KA)
    turnstile(c, KTURN, True)
    if c.now:                                                           # S1 and its closet; the second shutter, the secret
        c.room(S1_BOX, floor=0, ceil=0, wall="AJSHUT", ftex=TRIMF, ctex=TRIMF, id=S1)
        for y in (528, 544):
            c.line((S1_BOX[0], y), (S1_BOX[2], y), upper="AJSHUT", dontpegtop=True)
        c.room(CLOSET, floor=0, ceil=112, wall=LA, ftex=FA, ctex=KA, light=144)
        c.room(S2_BOX, floor=0, ceil=0, wall="AJSHUT", ftex=TRIMF, ctex=TRIMF, id=S2)
        for x in (-824, -808):
            c.line((x, S2_BOX[1]), (x, S2_BOX[3]), upper="AJSHUT", dontpegtop=True)
        c.room(SECRET2, floor=0, ceil=112, wall=LA, ftex=FA, ctex=KA, light=160, special=1024)


t.both(kennels)
t.frame((-400, 544), (-336, 544), (0, -1), 102)
t.line((-400, 544), (-336, 544), upper=LA, dontpegtop=True)
t.lever((PMID[0] + 112, 672), (PMID[0] + 48, 672), PEN1_GATE)           # pen 1's gate, east of its hatch (dead NOW)
t.cause(PMID[0], 620, PEN1_GATE, 2, tag=GATE_TAG[PEN1_GATE], start=1)
t.now.thing(PMID[0] - 72, 670, SCALES_T, angle=270, height=40, args=(PEN1, 400, S1, 96))   # the readout, west of the hatch
t.now.thing(-760, 450, SCALES_T, angle=90, height=40, args=(PEN1, 1000, S2, 96))        # ... and in the closet: 1000
t.then.thing(-112, 1088, GATE_T, angle=180, args=(KEN_RUN, DEMON, KEN_DOGS))
for x, y in ((-600, 1088), (-480, 1136), (-360, 1040)):                 # three demons, asleep, facing the turnstile
    t.then.thing(x, y, DEMON, angle=180, id=KEN_DOGS, skill=1)

# =================================================================================================================
# 4. THE STALLS
# =================================================================================================================
SRUN = (1152, 640, 1408, 1536)
STALL = (1240, 304, 1320, 496)                                          # 80 wide, 192 deep
SFUNNEL = [(1152, 640), (1408, 640), (1320, 512), (1240, 512)]
SGATE = (1240, 496, 1320, 512)
SHATCH = (1248, 288, 1312, 304)
SPASS = {THEN: (1088, 160, 1536, 288), NOW: (1088, 160, 1536, 224)}
SLEG = {THEN: (1424, 288, 1536, 1536), NOW: (1424, 224, 1536, 1536)}
STURN = (1408, 1344, 1424, 1408)
SLEDGES = [(1176, 240, 1240, 496), (1320, 240, 1384, 496), (1240, 240, 1320, 304)]   # NOW: west, east, round the end
SPAD = (1248, 1440, 1312, 1504)


def stalls(c):
    run(c, SRUN, SPAD, STALL_RUN, 160)
    c.sector(SFUNNEL, floor=0, ceil=160, wall=CO, ftex=FC, ctex=KC, **(dict(raw=moreids(STALL_RUN)) if c.then else {}))
    gate(c, SGATE, STALL_GATE, 128, tags=(STALL_RUN,))
    if c.then:
        c.room(STALL, floor=0, ceil=128, wall=AR, ftex=FR, ctex=KA, raw=moreids(STALL_RUN))
        hatch(c, SHATCH)
    else:
        c.room((1240, 304, 1320, 496), floor=0, ceil=128, wall=AR, ftex=FR, ctex=KA)
        for box in SLEDGES:
            c.room(box, floor=LEDGE, ceil=128, wall=AR, ftex=FR, ctex=KA, side=TRIM)
    c.room(SPASS[c.when], floor=0, ceil=128, wall=LA, ftex=FA, ctex=KA)
    c.room(SLEG[c.when], floor=0, ceil=128, wall=LA, ftex=FA, ctex=KA)
    turnstile(c, STURN, True)


t.both(stalls)
stone(t.now, (1312, 240), (1248, 240))                                  # the hatch NOW: Doom's stone behind the ledge
t.frame((1216, 160), (1152, 160), (0, -1), 103)
t.line((1216, 160), (1152, 160), upper=LA, dontpegtop=True)
lever_then((1392, 288), (1328, 288), STALL_GATE)                        # the stall's gate, east of its hatch
t.cause(1280, 224, STALL_GATE, 2, tag=GATE_TAG[STALL_GATE], start=1)
t.then.thing(1280, 1472, GATE_T, angle=270, args=(STALL_RUN, KNIGHT, STALL_DOGS))
for x, y in ((1232, 1152), (1328, 1248)):                               # two knights, asleep, facing the turnstile
    t.then.thing(x, y, KNIGHT, angle=0, id=STALL_DOGS, skill=1)

# =================================================================================================================
# 5. THE GUARDS
# =================================================================================================================
IRUN = (0, 1280, 768, 1472)
IGATE = (768, 1312, 784, 1440)
IPEN = (784, 1280, 1024, 1472)
IHATCH = (872, 1472, 936, 1488)
IPASS = (0, 1488, 1040, 1616)
ITURN = (176, 1472, 240, 1488)


def guards(c):
    if c.then:
        c.room(IRUN, floor=0, ceil=160, wall=CO, ftex=FC, ctex=KC)
        gate(c, IGATE, ISO_GATE, 128)
        c.room(IPEN, floor=0, ceil=128, wall=AR, ftex=FR, ctex=KA)
        hatch(c, IHATCH)
        c.room(IPASS, floor=0, ceil=128, wall=LA, ftex=FA, ctex=KA)
        turnstile(c, ITURN, False)
    else:
        c.room((0, 1280, 256, 1472), floor=0, ceil=160, wall=CO, ftex=FC, ctex=KC)       # the antechamber
        c.room((256, 1344, 272, 1408), floor=0, ceil=128, wall=TRIM, ftex=TRIMF, ctex=TRIMF)
        c.room((272, 1280, 1024, 1472), floor=0, ceil=160, wall=CO, ftex=FC, ctex=KC, light=104)   # the guard room


t.both(guards)
t.frame((0, 1408), (0, 1344), (-1, 0), 104)
t.line((0, 1408), (0, 1344), upper=CO, dontpegtop=True)
lever_then((952, 1488), (1016, 1488), ISO_GATE)                         # the pen's gate, east of its hatch
t.cause(904, 1552, ISO_GATE, 2, tag=GATE_TAG[ISO_GATE], start=1)
for x, y, kind in ((600, 1328, BARON), (600, 1424, BARON), (760, 1376, VILE)):     # NOW, facing the doorway
    t.now.thing(x, y, kind, angle=180, id=GUARDS, ambush=True, skill=1)
ajarmap.door(m, RED, 984, 1376, angle=180)                              # RED, on the guard room's far side

# =================================================================================================================
# 6. THE BIG RUN, THE CRUSH, ITS PASSAGE
# =================================================================================================================
BRUN = (656, -896, 912, 560)
BFUNNEL = [(656, -896), (912, -896), (848, -1024), (720, -1024)]
BGATE = (720, -1040, 848, -1024)
CRUSH_BOX = (720, -1296, 848, -1040)                                    # 128 wide, 256 deep
CGLASS = (720, -1312, 848, -1296)                                       # THEN: the crush's end wall, glass (sill 24, to 120)
CLEDGES = [(656, -1344, 720, -1040), (848, -1344, 912, -1040), (720, -1344, 848, -1296)]
BPASS = {THEN: (560, -1456, 1072, -1312), NOW: (560, -1456, 1072, -1360)}
BONES_LIT = (720, 32, 848, 160)                                         # NOW: a hole in the roof over the big one's bones
DOOR_LIT = (848, -1168, 912, -1040)                                     # NOW: the east ledge before the brass door, lit
BPAD = (720, 416, 848, 544)
BIG_AT = (784, 96)                                                      # the big one THEN; its bones NOW
BRASS_Y = (-1136, -1072)


def big(c):
    if c.then:
        run(c, BRUN, BPAD, BIG_RUN, 192)
    else:
        fit(c, BRUN, [(BONES_LIT, dict(light=200, ctex="F_SKY1"))], floor=0, ceil=192, wall=CO, ftex=FC, ctex=KC,
            light=c.light)
    c.sector(BFUNNEL, floor=0, ceil=192, wall=CO, ftex=FC, ctex=KC, **(dict(raw=moreids(BIG_RUN)) if c.then else {}))
    gate(c, BGATE, CRUSH_GATE, 160, tags=(BIG_RUN,))
    if c.then:
        c.room(CRUSH_BOX, floor=0, ceil=160, wall=AR, ftex=FR, ctex=KA, id=CRUSH, raw=moreids(BIG_RUN))
        # the glass that shows one way: the player sees the whole crush and its gate from the passage; nothing
        # passes, no shot, and the big one never sees him (blocksight); sound passes
        c.room(CGLASS, floor=24, ceil=120, wall=TRIM, ftex=TRIMF, ctex=TRIMF, light=c.light)
        for y in (CGLASS[1], CGLASS[3]):
            c.line((CGLASS[0], y), (CGLASS[2], y), **CRUSH_GLASS)
        c.room(BPASS[THEN], floor=0, ceil=128, wall=LA, ftex=FA, ctex=KA)
    else:
        c.room(CRUSH_BOX, floor=0, ceil=160, wall=AR, ftex=FR, ctex=KA)
        for box in CLEDGES:
            lit = [(DOOR_LIT, dict(light=208))] if box[0] == 848 else []
            fit(c, box, lit, floor=LEDGE, ceil=160, wall=AR, ftex=FR, ctex=KA, side=TRIM, light=c.light)
        c.room(BPASS[NOW], floor=0, ceil=128, wall=LA, ftex=FA, ctex=KA)


t.both(big)
stone(t.now, (816, -1344), (752, -1344))                                # the hatch NOW: Doom's stone behind the ledge
t.clock_frame((560, -1376), (560, -1440), (-1, 0), 105, when=(NOW, THEN))
t.line((560, -1376), (560, -1440), upper=LA, dontpegtop=True)
t.far((928, -1456), (864, -1456), (0, -1), RED)
t.line((928, -1456), (864, -1456), upper=LA, dontpegtop=True)
lever_then((848, -1312), (912, -1312), CRUSH_GATE)                      # the crush's gate, beside its glass
t.cause(1000, -1400, CRUSH_GATE, 2, tag=GATE_TAG[CRUSH_GATE], start=1)
t.then.thing(784, 480, GATE_T, angle=270, args=(BIG_RUN, CYBER, BIG_ONE, CRUSH))
t.then.thing(*BIG_AT, CYBER, angle=270, id=BIG_ONE, ambush=True, skill=1)    # deaf: it wakes by scent (the passage)
# NOW: the brass door in the crush's east wall, on the ledge (keys 1 and 2), and the night room, the way out
first = len(m.sectors)
ajarmap.roomdoor(m, (912, BRASS_Y[0]), (912, BRASS_Y[1]), (1, 0), LEDGE, keys="12", line_id=BRASS_LINE)
m.sectors[first]["id"] = BRASS_TAG
m.sector(rect(928, BRASS_Y[0], 944, BRASS_Y[1]), floor=LEDGE, ceil=LEDGE + 112, light=150, wall="AJXW2", ftex="AJXG2",
         ctex="AJXC2")
ajarmap.way_out(m, 944, BRASS_Y[0] - 128, None, floor=LEDGE, turned=True)

# =================================================================================================================
# COMPANY, SUPPLIES, THE BUDGET (NOW's tenants; the specimens apart)
# =================================================================================================================
PART_OF = []            # (thing index, part) for every monster and pick-up: the budget by part
TAKEN = []
AVOID = [START, (512, 540), (320, 540), (112, 224), (-368, 512), (1184, 128), (-32, 1376), (528, -1408),
         (896, -1488), BIG_AT, (1280, 272), (984, 1376), (920, -1104)]


def halton(i, b):
    f, r = 1, 0
    while i:
        f /= b
        r += f * (i % b)
        i //= b
    return r


def spot(box, r=20):
    """A free place for a thing of radius r in `box` (NOW; a Halton sequence: the same every build)."""
    x1, y1, x2, y2 = box
    for k in range(1, 4000):
        x = round((x1 + r + 8 + halton(k, 2) * (x2 - x1 - 2 * r - 16)) / 8) * 8
        y = round((y1 + r + 8 + halton(k, 3) * (y2 - y1 - 2 * r - 16)) / 8) * 8
        if any(max(abs(x - tx), abs(y - ty)) < r + tr + 12 for tx, ty, tr in TAKEN):
            continue
        if any(math.hypot(x - ax, y - ay) < 72 + r for ax, ay in AVOID):
            continue
        if any(math.hypot(x - th["x"], y - th["y"]) < r + 28 for th in m.things):
            continue
        TAKEN.append((x, y, r))
        return x, y
    raise ValueError(f"no room in {box}")


R = {CACO: 31, MANCUBUS: 48, BARON: 24, KNIGHT: 24, DEMON: 30, SPECTRE: 30, REVENANT: 20}


def mark(part, first):
    PART_OF.extend((i, part) for i in range(first, len(m.things)))


def put(part, box, kind, k, angle=0, **more):
    first = len(m.things)
    for _ in range(k):
        m.thing(*spot(box, R.get(kind, 20)), kind, angle=angle, **more)
    mark(part, first)


def ambush(part, box, cause, kind, k, *, angle=0, after=0, near=0, arg=None):
    first = len(m.things)
    spots = [spot(box, R.get(kind, 20)) for _ in range(k)]
    if arg is None:
        ajarmap.ambush(m, cause, kind, *spots, angle=angle, after=after, near=near)
    else:
        ajarthen.ambush(m, cause, arg, kind, *spots, angle=angle, after=after, near=near)
    mark(part, first)


def items(part, *spec):
    first = len(m.things)
    for x, y, kind in spec:
        m.thing(x, y, kind)
    mark(part, first)


DEAF = dict(ambush=True)
# --- the yard: a few zombies by the gateway; the shotgun
items("yard", (448, -64, 2001), (480, -160, 2008), (560, -200, 2008), (240, -200, 2049), (400, 420, 2011))
put("yard", (360, 160, 620, 480), ZOMBIE, 5, 180)
# --- the hall: the first fight; the chaingun
items("hall", (384, 640, 2002), (420, 660, 2048), (64, 1160, 2049), (704, 1160, 2049), (64, 640, 2048),
      (704, 640, 2012), (384, 1160, 2046), (600, 900, 2049), (160, 900, 2048), (384, 1100, 2012))
put("hall", (32, 720, 736, 1184), IMP, 8, 270)
put("hall", (32, 720, 736, 1184), SERGEANT, 5, 270)
put("hall", (32, 720, 736, 1184), ZOMBIE, 4, 270)
put("hall", (32, 720, 736, 1184), CHAINGUNNER, 3, 270)
# --- the kennels NOW: demons and spectres in the run, imps in the passage; S1's closet: key 1 and the super
# shotgun; behind the second shutter the secret (a megasphere and the plasma rifle)
items("kennels", (-760, 480, ajarmap.KEY_T["1"]), (-736, 500, 82), (-780, 500, 2049), (-872, 500, 83), (-872, 470, 2004),
      (-860, 496, 17), (-600, 620, 2049), (-200, 620, 2049), (-860, 1180, 2048), (-100, 1180, 2012), (-984, 1000, 2049),
      (-40, 1000, 2046), (-500, 1180, 2008))
put("kennels", (-880, 980, -48, 1200), DEMON, 5, 0)
put("kennels", (-880, 980, -48, 1200), SPECTRE, 4, 0)
put("kennels", (-1020, 560, -40, 656), IMP, 5, 0)
ambush("kennels", (-1020, 560, -40, 656), 1, IMP, 4, angle=270, after=1)
ambush("kennels", (-880, 980, -48, 1200), 1, SERGEANT, 2, angle=270, after=1)
ambush("kennels", (-880, 980, -48, 1200), 1, KNIGHT, 1, angle=270, after=2)
# --- the stalls NOW: imps, revenants, a knight; the rocket launcher; on the ledge key 2 and a soul sphere
items("stalls", (1280, 272, ajarmap.KEY_T["2"]), (1352, 272, 2013), (1280, 900, 2003), (1250, 920, 2046),
      (1320, 920, 2046), (1180, 1500, 2049), (1380, 1500, 2048), (1480, 600, 2046), (1480, 1200, 2049),
      (1180, 700, 2012), (1380, 700, 2010), (1380, 760, 2010), (1112, 192, 2046), (1500, 192, 2049))
put("stalls", (1168, 700, 1392, 1520), IMP, 7, 270)
put("stalls", (1168, 700, 1392, 1520), REVENANT, 4, 270)
put("stalls", (1168, 1200, 1392, 1520), KNIGHT, 1, 270)
put("stalls", (1440, 300, 1520, 1500), CHAINGUNNER, 1, 270)
ambush("stalls", (1168, 700, 1392, 1520), 2, IMP, 3, angle=270, after=1)
ambush("stalls", (1168, 700, 1392, 1520), 2, REVENANT, 2, angle=270, after=2)
ambush("stalls", (1440, 300, 1520, 1500), 2, CHAINGUNNER, 2, angle=180, after=1)
# --- the guards' wing NOW: when RED is taken, in the antechamber and the hall
items("guards", (128, 1440, 2049), (64, 1300, 17), (200, 1300, 2012), (640, 1176, 2046))
ambush("guards", (16, 1296, 240, 1456), 10 + RED, IMP, 4, angle=0, after=1)
ambush("guards", (32, 720, 736, 1184), 10 + RED, DEMON, 2, angle=90, after=1)
ambush("guards", (32, 720, 736, 1184), 10 + RED, CACO, 2, angle=90, after=3)
# --- the big run NOW: cacodemons, lost souls, a mancubus at the crush; the last fight when the brass door opens
items("big run", (700, 500, 2049), (870, 500, 17), (700, -800, 2046), (870, -800, 2012), (680, 300, 2047),
      (880, 300, 2047), (680, -400, 2049), (880, -400, 17), (784, -600, 2046), (680, -1200, 2012),
      (880, -1250, 17))
_first = len(m.things)
m.thing(784, -848, MANCUBUS, angle=90, **DEAF)                          # at the crush
TAKEN.append((784, -848, 48))
mark("big run", _first)
put("big run", (672, -880, 896, 540), CACO, 5, 90, **DEAF)
put("big run", (672, -880, 896, 540), SOUL, 7, 90, **DEAF)
ambush("big run", (672, -880, 896, -300), 62, KNIGHT, 2, angle=270, after=1, arg=BRASS_TAG)
ambush("big run", (672, -880, 896, -300), 62, IMP, 3, angle=270, after=1, arg=BRASS_TAG)
ambush("big run", (672, -880, 896, 200), 62, CACO, 2, angle=270, after=2, arg=BRASS_TAG)
ambush("big run", (672, -880, 896, -300), 62, REVENANT, 1, angle=270, after=3, arg=BRASS_TAG)
items("secrets", (-64, 224, 2019), (-96, 200, 2049))                    # THEN behind the shelter (THEN's coordinates below)
for i, _ in PART_OF[-2:]:
    m.things[i]["y"] += OFF[1]

SKILLS = m._skills()
SPECIMENS = {KEN_DOGS, STALL_DOGS, BIG_ONE, GUARDS}
BUDGET = {}
for part in dict.fromkeys(p for _, p in PART_OF):
    idx = [i for i, p in PART_OF if p == part]
    for level in (3, 1):
        BUDGET[(part, level)] = budget.reckon([m.things[i] for i in idx], [SKILLS[i] for i in idx], level)
ALL = [i for i, _ in PART_OF]
for level in (3, 1):
    BUDGET[("the level", level)] = budget.reckon([m.things[i] for i in ALL], [SKILLS[i] for i in ALL], level)
SPEC = [i for i, th in enumerate(m.things) if th.get("id") in SPECIMENS]
BUDGET[("specimens (not paid for)", 3)] = budget.reckon([m.things[i] for i in SPEC], [SKILLS[i] for i in SPEC], 3)
for part in ("yard", "hall", "kennels", "stalls", "guards", "big run", "the level"):
    r = BUDGET[(part, 3)]
    assert r["dmg"] >= 1.6 * r["hp"], budget.line(part, r, 3)
MONSTERS = {lv: sum(budget.reckon([m.things[i] for i in ALL], [SKILLS[i] for i in ALL], lv)["monsters"].values())
            for lv in (1, 2, 3, 4)}
assert 90 <= MONSTERS[3] <= 120, MONSTERS

PUZZLE = puzzle23.PUZZLE23

# THE LOOK (PLAN.md, "Look: MAP23, the animal house"): AJAR_DOGS unset (or mix) the picks (tools/dogs23.py, MIX:
# The Kennels since 2026-11-27), 1, 2, 3 a look for every group; 0 the plain level, and the look's files are not
# imported
import os                                                               # noqa: E402
if (os.environ.get("AJAR_DOGS") or "mix").strip() != "0":
    import sys                                                          # noqa: E402
    import dogs23                                                       # noqa: E402
    DOGS = dogs23.setting()
    dogs23.apply(sys.modules[__name__], DOGS)

if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["budget"]:
        for (part, level), r in BUDGET.items():
            print(budget.line(part, r, level))
        print("monsters by skill (the specimens apart):", MONSTERS)
    else:
        sys.stdout.write(m.textmap())
