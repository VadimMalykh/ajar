"""The kennel lab (map KENNEL): MAP=KENNEL ./run.sh

An engine lab for MAP23 "Sleeping Dogs" (PLAN.md, "MAP23 "Sleeping Dogs": the
animal house, chosen" and "The kennel lab"): a monster led into THEN and penned
there is a tool NOW, by its bones (then.zs: a monster alive THEN shows NOW as
an old corpse while no clocked door joins the times). One place built twice
(tools/ajarthen.py, the then and now lab's two looks: NOW dark and bare, THEN
lit), no monsters THEN at the start. THEN is NOW + (0, -4096): south of NOW,
not north as in the THEN lab, because a monster goes after where its target is
(Doom's chase knows no times): penned THEN while the player is NOW and going
after him straight, it walks north, to the back of its pen, its hatch and pen
2's ledge, where its bones are of use (a knight in 129 tics, MODE=2); one that
is making for the clocked door's lure instead does not (PLAN.md, "The kennel
lab", measured).

  The run      x 0..768, y 0..256. Frame 101 (NOW) / 121 (THEN) in its west
               wall (y 96..160), the clocked door leaning beside it NOW. The
               start is here NOW (a shotgun, a chaingun, ammunition). NOW in
               its east half, deaf and facing east: 2 demons, an imp, a hell
               knight, a baron.
  Three pens   north of the run: pen 1 x 0..240 and pen 3 512..752, y 272..528,
               each opening on the run by a gate 128 wide (y 256..272); pen 2
               a stall (below). Middles 120, 376, 632. THEN each gate is a
               shutter (cause 21, 22, 23; found open) worked by its lever in
               the keeper's passage, held up while anything stands under it.
               NOW the gates are gone.
  The passage  the keeper's passage, 128 wide: y 544..672 from x 0 to 896, and
               its east leg x 784..896 from y 0 up to it. In each pen's back wall
               (y 528..544) a feeding hatch 64 wide, floor 24, ceiling 56: sight
               and shots pass, nobody walks through. THEN the gate levers are on
               the passage's south wall, east of each hatch.
  The turnstile  in the run's east wall (x 768..784, y 96..160): 64 wide, into
               the passage's east leg. The player passes both ways, with or
               without a door; no monster does (a block-monsters line).
  Pen 1, the scales  AjarKennelScales (kennel.zs) reads the weight of the old
               corpses lying in pen 1 NOW (sector tag 81); at 400 or more its
               shutter NOW (the passage's north wall, x 88..152) stands open on
               a closet with a soul sphere. Each pen has the readout, on the
               passage's south wall west of its hatch.
  Pen 2, the step  a stall as MAP23 will have it: 80 wide inside (x 336..416; a
               knight or a baron is 48 across, a demon 60), 192 deep (y
               336..528), its hatch in the end wall. Its gate (80 wide, y
               320..336) is at its mouth, reached from the run by a lane of the
               stall's width (y 256..320). Along both long sides, for the
               whole depth and at both times, a ledge at 48, 64 deep (x
               272..336 and 416..480): NOW a megasphere on the west one, a soul
               sphere on the east one. Big bones (Mass 1000 or more) NOW are a
               solid step 24 high; from bones anywhere in the stall one ledge
               or the other is in reach (PLAN.md, "The kennel lab"). It
               replaces the first pen 2 (a ledge along the back wall, the
               hatch a notch through it), whose bones in front of the hatch
               were a dead zone.
  Pens 2 and 3  THEN a shuttered opening between them (cause 24, found shut),
               of the hatch's shape (floor 24, ceiling 56), x 480..512, y
               336..400: from pen 3 over the stall's east ledge (sight and
               shots pass above the ledge); its lever on the passage's north
               wall. NOW open.
The checks are src/zscript/kenneltest.zs (MODE=1..7 tools/smoke.sh).
"""
import ajarmap
from ajarthen import Times, NOW, THEN, CO, LA, AR, FC, FA, FR, KC, KA, heights
from udmf import Map

m = Map()
import gfx_institute
m.align |= gfx_institute.ALIGNED            # MAP11's walls are laid by where they are
OFF = (0, -4096)                            # THEN is south of NOW (see the docstring)
t = Times(m, off=OFF, at=(384, 128))        # the AjarThen thing, in NOW's run

RUN = dict(wall=CO, ftex=FC, ctex=KC, ceil=160)
PEN = dict(wall=AR, ftex=FR, ctex=KA, ceil=128)
PASS = dict(wall=LA, ftex=FA, ctex=KA, ceil=128)
PENS = ((0, 240), (256, 496), (512, 752))
MID = tuple((a + b) // 2 for a, b in PENS)             # 120, 376, 632
GATE_CAUSE = (21, 22, 23)                              # THEN: each gate's shutter (0 shut, 1 open)
GATE_TAG = (61, 62, 63)                                # ... its sector THEN
SIDE_CAUSE, SIDE_TAG = 24, 64                          # THEN: the opening between pens 2 and 3
PEN_TAG = (81, 82, 83)                                 # NOW: the pens' floors, which the scales read
SHUTTER_TAG = 71                                       # NOW: pen 1's shutter, opened by its scales
SCALES_T = 20193                                       # AjarKennelScales (kennel.zs)
THRESHOLD = 400
HATCH_FLOOR, HATCH_CEIL = 24, 56
LEDGE, LEDGE_D = 48, 64
SIDE_Y = (336, 400)                                    # the opening between pens 2 and 3
STALL = (336, 416)                                     # pen 2, the stall, inside
STALL_Y = 528 - 192                                    # its mouth (its gate y 320..336, the lane y 256..320)


def hatch_sector(c, x1, y1, x2, y2, ceil=HATCH_CEIL, **k):
    return c.room((x1, y1, x2, y2), floor=HATCH_FLOOR, ceil=ceil, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF",
                  light=c.light, **k)


def place(c):
    # the run, the passage and its east leg
    c.room((0, 0, 768, 256), **RUN)
    c.room((0, 544, 896, 672), **PASS)
    c.room((784, 0, 896, 544), **PASS)
    # the turnstile: a gap 64 wide in the run's east wall, framed in striped steel; monsters never pass
    c.room((768, 96, 784, 160), floor=0, ceil=96, wall="SUPPORT3", ftex="FLAT23", ctex="FLAT23", light=c.light)
    c.line((768, 96), (768, 160), blockmonsters=True)
    c.line((784, 96), (784, 160), blockmonsters=True)
    for n, (x1, x2) in enumerate(PENS):
        mid = MID[n]
        tag = dict(id=PEN_TAG[n]) if c.now else {}
        if n == 1:                                     # the stall: ledges along both long sides, the lane to its gate
            sx1, sx2 = STALL
            c.room((sx1, STALL_Y, sx2, 528), **PEN, **tag)
            for a, b in ((sx1 - LEDGE_D, sx1), (sx2, sx2 + LEDGE_D)):
                c.room((a, STALL_Y, b, 528), **dict(PEN, floor=LEDGE, side="AJTRIM"), **tag)
            c.room((sx1, 256, sx2, STALL_Y - 16), **RUN)
            gate = (sx1, STALL_Y - 16, sx2, STALL_Y)
        else:
            c.room((x1, 272, x2, 528), **PEN, **tag)
            gate = (mid - 64, 256, mid + 64, 272)
        hatch_sector(c, mid - 32, 528, mid + 32, 544)
        # the gate onto the run: THEN a shutter on its lever, NOW gone
        gx1, gy1, gx2, gy2 = gate
        if c.then:
            c.room(gate, floor=0, ceil=128, wall="AJSHUT", ftex="AJTRIMF", ctex="AJTRIMF",
                   light=c.light, id=GATE_TAG[n], raw=heights(ceils=(0, 128), hold=True))
            for y in (gy1, gy2):
                c.line((gx1, y), (gx2, y), upper="AJSHUT", dontpegtop=True)
        else:
            c.room(gate, floor=0, ceil=128, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF", light=c.light)
    # between pens 2 and 3: THEN a shutter of the hatch's shape, NOW open
    if c.then:
        hatch_sector(c, STALL[1] + LEDGE_D, SIDE_Y[0], 512, SIDE_Y[1], ceil=HATCH_FLOOR, id=SIDE_TAG,
                     raw=heights(ceils=(HATCH_FLOOR, HATCH_CEIL), hold=True))
        for x in (STALL[1] + LEDGE_D, 512):
            c.line((x, SIDE_Y[0]), (x, SIDE_Y[1]), upper="AJSHUT", dontpegtop=True)
    else:
        hatch_sector(c, STALL[1] + LEDGE_D, SIDE_Y[0], 512, SIDE_Y[1])
    # NOW: pen 1's shutter in the passage's north wall, and the closet behind it
    if c.now:
        c.room((88, 672, 152, 688), floor=0, ceil=0, wall="AJSHUT", ftex="AJTRIMF", ctex="AJTRIMF", light=c.light,
               id=SHUTTER_TAG)
        for y in (672, 688):
            c.line((88, y), (152, y), upper="AJSHUT", dontpegtop=True)
        c.room((72, 688, 168, 752), **dict(PASS, ceil=112))


t.both(place)
t.frame((0, 96), (0, 160), (-1, 0), 101)
t.clocked(24, 56, 0)
m.thing(96, 128, 1, angle=0)
for x, y, kind in ((64, 216, 2001), (96, 216, 2049), (128, 216, 2002), (160, 216, 2048), (192, 216, 2048)):
    m.thing(x, y, kind)                                                  # a shotgun, shells, a chaingun, bullets
# the gates' levers THEN, east of each hatch on the passage's south wall (dead plates NOW)
for n, mid in enumerate(MID):
    t.lever((mid + 112, 544), (mid + 48, 544), GATE_CAUSE[n])
    t.cause(mid, 608, GATE_CAUSE[n], 2, tag=GATE_TAG[n], start=1)
t.lever((504, 672), (568, 672), SIDE_CAUSE)                               # the opening between 2 and 3, across
t.cause(536, 608, SIDE_CAUSE, 2, tag=SIDE_TAG, start=0)
# the scales NOW: a readout on the passage's south wall west of each hatch; pen 1's opens its shutter
for n, mid in enumerate(MID):
    shutter = (SHUTTER_TAG, 96) if n == 0 else (0, 0)
    t.now.thing(mid - 72, 546, SCALES_T, angle=90, height=40, args=(PEN_TAG[n], THRESHOLD) + shutter)
t.now.thing(120, 720, 2013)                                              # the soul sphere, behind pen 1's shutter
t.now.thing(STALL[0] - LEDGE_D // 2, 464, 83)                            # the megasphere, on the stall's west ledge
t.now.thing(STALL[1] + LEDGE_D // 2, 464, 2013)                          # a soul sphere, on its east ledge
# NOW, the run's east half, deaf and facing away
for x, y, kind in ((480, 72, 3002), (480, 184, 3002), (560, 128, 3001), (640, 72, 69), (640, 184, 3003)):
    t.now.thing(x, y, kind, angle=0, ambush=True, skill=1)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
