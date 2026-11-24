"""Act 2, level 10: "High Water" (MAP20), the waterworks behind and under the
institute. PLAN.md, "MAP20 'High Water': the first version, as decided"; the
water is the water lab's (map WATER, tools/map_water.py, tools/ajarwater.py,
src/zscript/water.zs). It wears MAP19's look (AJAR_INSTITUTE) for now.

The rule (the lab's): water stands level on both sides of a hung door,
measured from the door's sill. BLUE's far side is in the reservoir (96 over
its sill), GREEN's in the outfall (always dry). Four doors only: BLUE, GREEN
and the two TEAL leaves.

Places (x east, y north; floor 0 is the baths' floor):
  the baths (stage 1, "see it"): the changing room (the start), the swimming
    bath off it (a room only in this version), the plunge hall P (101 at the
    floor, 102 on the gallery at 128, the ledge at 216 behind its coaming),
    the changing room's upper floor at 240 (from the ledge; the gallery's
    own door, bolted on its side, comes out in it)
  the pump corridor and the pump house (GREEN), the cooling hall C (stage 2,
    "drain it"; 111 on the walkway at 104, 112 on the landing at 0, 113 at
    the floor at -128; E2 and two cells in its floor, pressure doors)
  the passage from E2 and the boiler house with the feed tank T (stage 3,
    "the pipe"; 121 in T, the float that raises the yard gate)
  the lower yard (0) and the upper yard (192), the lock K between them
    (stage 4; 131, 135 at its floor, 133 on a shelf at 88), the wheel house
    (stage 5; L at -96 with 107 and 109, U at 128 with 108, the spillway and
    the wheel), the sluice, the tunnel and the machine hall (the way out)
  the reservoir (behind glass from the upper yard) and the outfall (from the
    lower yard): BLUE's and GREEN's far sides, not walked but through a door

No solver PUZZLE: water levels are numbers, not places. Instead the measure
(MEASURE, every build) runs the lab's rule of flow, written again here, to
rest for every hanging the plan names, and checks the four facts of "nothing
can be lost" on a graph of the places; the build fails on a broken rule.
"""
import math
import os as _os

import ajarmap
import ajarwater as W
import lefthand
import map_institute1 as I1
import map_clockdept as CD
from ajarmap import GREEN, BLUE, TEAL, far_id
from map_institute1 import dress, tint, over, LOOK
from map_institute1 import ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, CHAINGUNNER, KNIGHT, REVENANT, CACO
from map_institute1 import BARON, SOUL, MANCUBUS
from udmf import MONSTERS, Map, rect

ARACH, PAIN, VILE = 68, 71, 64

m = Map()
_theirs, I1.m = I1.m, m                     # MAP11's helpers draw on their module's map: this one while this file runs
_cd, CD.m = CD.m, m
if LOOK:
    import gfx_institute
    m.align |= gfx_institute.ALIGNED

# === the rate and the rules (water.zs reads them from the rate thing) =================================
K_FLOW = 1000           # volume a tic per unit of head difference through a hung door (the lab's is 2048)
FREE = 6                # ... this many times that onto a dry sill (the lab's)
K_WEIR = K_FLOW         # over the spillway's crest, per unit over it (as in the lab: the same as K)
WHEEL_FLOW = 2 * K_WEIR  # the wheel counts as turning over this (2 over the crest) ...
WHEEL_TICS = 192        # ... for this long (the lab's is 105: 3 s; here 5.5 s, so that the wait is not under 5 s)
HOLD = W.HOLD
REACH = 24              # the player climbs out from water no more than this under a ledge (the lab)
DIVE = 260              # the deepest dive "nothing can be lost" allows
WAIT = (5, 25)          # no wait the level asks for is shorter or longer (s)
FLOAT_MARK, FLOAT_SECONDS = 216, 2

# === tags ========================================================================================
TP, TC, TT, TK, TL, TU, TSB, TR, TO = 21, 22, 23, 24, 25, 26, 27, 28, 29     # basins
PD_P, PD_E2, PD_CA, PD_CB, PD_T, PD_K = 41, 42, 43, 44, 45, 46                # pressure doors (sector tags)
LAMP0 = 50              # + (pressure door tag - 40): its two lamps
GD_TAG, GW_TAG, LEDGE_TAG, YARD_TAG, SLUICE, WLAMP, CHUTE = 61, 62, 63, 64, 65, 66, 67
FOUNTAIN_TAG = W.FOUNTAIN + CHUTE        # the lower yard's fountain: dry at rest, plays while the wheel turns (water.zs)
MAPSPOT = 9001
NAMES = {TP: "P (the plunge hall)", TC: "C (the cooling hall)", TT: "T (the feed tank)", TK: "K (the lock)",
         TL: "L (the lower pool)", TU: "U (the upper pool)", TSB: "the swimming bath", TR: "the reservoir",
         TO: "the outfall"}
SHORT = {TP: "P", TC: "C", TT: "T", TK: "K", TL: "L", TU: "U", TSB: "SB", TR: "R", TO: "O"}

# === the look ======================================================================================
# "Municipal" (PLAN.md, "Look: MAP20, Municipal"): a town waterworks and public baths of 1900-1930, drawn
# by tools/gfx_highwater.py (names AJV...). It is what any AJAR_INSTITUTE but 0 builds; AJAR_INSTITUTE=0 is
# the plain level. A look changes textures and hangs pictures on walls: nothing moves. Walls are laid at
# absolute heights (see `hook`), so that courses, tide lines and plaques stand where the water can.
SKY = "F_SKY1"
# material -> (wall, floor, ceiling)
MATS = {
    "CR": ("AJVCR", "AJVFQ", "AJVKP"),          # the changing room: cream tile to 96, an oxblood capping, plaster
    "CU": ("AJVCU", "AJVFQ", "AJVKP"),          # ... its upper floor
    "PL": ("AJVPL", "AJVFP", "AJVKG"),          # the plunge hall: white tile, a black course every 64, oxblood at the brim
    "SB": ("AJVSB", "AJVFB", "AJVKG"),          # the swimming bath: the same family, all the build's own
    "EC": ("AJVEC", "AJVFC", "AJVKB"),          # the engine house: cream brick over a maroon dado, chequered floor
    "PH": ("AJVPH", "AJVFC", "AJVKB"),          # ... the pump house: riveted plate under the brick
    "PA": ("AJVPA", "AJVFC", "AJVKB"),          # ... the passage from E2
    "CH": ("AJVCH", "AJVFS", "AJVKB"),          # the cooling hall: iron plate, the tide line at 96; silt on its floor
    "CW": ("AJVCH", "AJVFW", "AJVKB"),          # ... its walkway: chequer plate
    "BH": ("AJVBH", "AJVFR", "AJVKB"),          # the boiler house: red brick, sooty above; brick paving
    "BS": ("AJVBH", "AJVFW", "AJVKB"),          # ... its stairs (and the gangway's): iron treads
    "TK": ("AJVTK", "AJVFT", "AJVKB"),          # the feed tank: riveted plate
    "CT": ("AJVTK", "AJVFW", "AJVKB"),          # ... its catwalk
    "LY": ("AJVYD", "AJVFG", SKY),              # the lower yard: brick on a stone plinth; setts
    "UY": ("AJVYU", "AJVFL", SKY),              # the upper yard: the same at 192; grass
    "KS": ("AJVKS", "AJVFK", SKY),              # the lock: buff stone, stained to its brim
    "BU": ("AJVBU", "AJVFK", SKY),              # buff stone, clean: the squeeze stair, the terrace
    "WL": ("AJVWL", "AJVFK", SKY),              # the wheel house: L, stained to -4
    "WU": ("AJVWU", "AJVFK", SKY),              # ... U, stained to 184
    "WT": ("AJVWT", "AJVFD", SKY),              # ... the spillway: timber
    "OV": ("AJVOV", "AJVFO", "AJVKO"),          # the outfall: a tide-stained brick vault
    "RS": ("AJVRS", "AJVFT", "AJVKR"),          # the reservoir: riveted plate
    "TN": ("AJVTN", "AJVFG", "AJVKO"),          # the tunnel, its first half: the yard's brick
    "TD": ("MARBGRAY", "FLOOR4_8", "TLITE6_1"),  # ... its second half: Doom's (the leak)
    "CL": ("MARBLE1", "DEM1_6", "FLOOR7_2"),    # the cells off C: Doom's stone
    "MH": ("MARBGRAY", "FLOOR4_8", "TLITE6_1"),  # the machine hall: a Doom room
}


def look(mat, light, ceil, color=None):
    d = dict(ceil=ceil, light=light, color=tint(color))
    if LOOK:
        d.update(zip(("wall", "ftex", "ctex"), MATS[mat]))
    return d


def sky(mat, light, ceil):
    d = look(mat, light, ceil)
    d["ctex"] = SKY
    return d


PALE, MINT, PAPER, DIM, RUST, COLD, STEEL = 0xDCE8DC, 0xC8E0C8, 0xF0E4C8, 0xB0B8C8, 0xE8C8B0, 0xA8C0D8, 0xC8D0E0
CHANGE = look("CR", 200, 192, PAPER)
BATH = look("PL", 210, 320, PALE)
PUMP = look("PH", 180, 352, COLD)
CORR = look("EC", 180, 344, MINT)
HALL = look("CH", 170, 400, COLD)
BOIL = look("BH", 176, 448, RUST)
YARD = sky("LY", 220, 512)
UPYARD = dict(sky("UY", 230, 640), **({} if LOOK else dict(ftex="GRASS1")))
MH_CEIL = 256
WORKS = look("MH", 190, MH_CEIL, STEEL)
# Doom's own elements (PLAN.md: "what looks like Doom behaves like Doom"): names in the player's doom2.wad
DOOR_FACE = "SPCDOOR1"          # a door opened by USE that stays where it is: the pressure doors and the ledge door
SURROUND = "SUPPORT2"           # ... the wall over a pressure door's mouth (its lamp strips')
SWITCH = "SW1BRIK"              # the gangway's bolt, from the boiler house (GZDoom turns it to SW2BRIK)
EXIT_FACE, EXIT_SIGN = "EXITDOOR", "EXITSIGN"


def pdoor_look():
    """The pressure doors' leaf and surround: Doom's in the look, the placeholder in the plain level."""
    if LOOK:
        return dict(look=dict(wall=DOOR_FACE, ftex="FLAT20", ctex="FLAT20"), strip=dict(wall=SURROUND, ftex="FLAT20"))
    return {}


# --- walls at absolute heights ------------------------------------------------------------------
# A wall texture of the look is H high and its row 0 stands at z0 (the rows go down from there): `hook` sets
# every side's vertical offset so, whatever the floor and ceiling of the sector it is on and however the line
# is pegged. Each is drawn by gfx_highwater (its `mat` and the heights given here, from the constants below);
# the build fails if a wall shows one where it has no rows.
WALLS = {}              # name -> dict(H, z0, mat, ...): the look's wall textures
PICS = {}               # name -> dict(H, z0, w, kind, base, shift, ...): pictures and plates (gfx_highwater)
OPENINGS = set()        # sector indices of open ways: the wall over and under them is the room's own
LOOK_PROBLEMS = []
DOOM = set()            # every Doom name the level uses (the report's list; checked against the IWAD by hand)


def wall_tex(name, H, z0, mat, **k):
    WALLS[name] = dict(H=H, z0=z0, mat=mat, **k)


def zpeg(name):
    if name in WALLS:
        return WALLS[name]["H"], WALLS[name]["z0"]
    if name in PICS:
        return PICS[name]["H"], PICS[name]["z0"]
    return ZDOOM.get(name)


ZDOOM = {SWITCH: (128, 240)}    # Doom textures laid at a height: the switch's plate from 168 down to 136


def make_hook(mm, openings):
    """udmf's line hook for the look: the wall over an open way is the room's own; every texture in
    WALLS, PICS or ZDOOM gets the vertical offset that puts its row 0 at its z0 (Doom's pegging rules:
    a one-sided wall from its ceiling, or its floor if lower-unpegged; an upper from the lower ceiling,
    or its own if upper-unpegged; a lower from the higher floor, or its own ceiling if lower-unpegged)."""
    secs = mm.sectors

    def hook(ld, sides, a, b, si, other, given):
        both = [(sides[ld["sidefront"]], si, other, a, b)]
        if other is not None:
            both.append((sides[ld["sideback"]], other, si, b, a))
        for sd, f, o, p, q in both:
            F, B = secs[f], (secs[o] if o is not None else None)
            if LOOK and B is not None and o in openings and f not in openings:
                if given["upper"] is None and sd.get("texturetop") == "AJTRIM":
                    sd["texturetop"] = F["wall"]
                if given["lower"] is None and sd.get("texturebottom") == "AJTRIM":
                    sd["texturebottom"] = F["side"]
            if B is not None and sd.get("texturetop") == DOOR_FACE and F["ceil"] > B["ceil"]:
                sd["scaley_top"] = round(128 / (F["ceil"] - B["ceil"]), 4)   # the whole Doom door in its mouth
            sw = SWITCH_AT.get((p, q))
            if sw is not None:
                sd["texturemiddle"] = SWITCH
                sd["offsetx_mid"] = float(sw)
            for part, key in (("top", "texturetop"), ("mid", "texturemiddle"), ("bottom", "texturebottom")):
                z = zpeg(sd.get(key))
                if z is None:
                    continue
                H, z0 = z
                if part == "mid":
                    if B is not None:
                        continue
                    anchor, lo, hi = (F["floor"] + H if ld.get("dontpegbottom") else F["ceil"]), F["floor"], F["ceil"]
                elif part == "top":
                    if B is None or F["ceil"] <= B["ceil"] or F["ctex"] == B["ctex"] == SKY:
                        continue                # (no upper is drawn between two skies)
                    anchor, lo, hi = (F["ceil"] if ld.get("dontpegtop") else B["ceil"] + H), B["ceil"], F["ceil"]
                else:
                    if B is None or F["floor"] >= B["floor"]:
                        continue
                    anchor, lo, hi = (F["ceil"] if ld.get("dontpegbottom") else B["floor"]), F["floor"], B["floor"]
                off = (z0 - anchor) % H
                if off:
                    sd["offsety_" + part] = float(off)
                else:
                    sd.pop("offsety_" + part, None)
                if sd[key] not in ZDOOM and (lo < z0 - H or hi > z0):
                    LOOK_PROBLEMS.append(f"{sd[key]} (rows {z0 - H}..{z0}) shown {lo}..{hi} at {p}-{q}")
    return hook


SWITCH_AT = {}          # (start, end) of a side -> the switch texture's column at its start
m.line_hook = make_hook(m, OPENINGS)
if LOOK:
    m.align |= {w for w, f, c in MATS.values() if w.startswith("AJV")}
GLASS = dict(mid="AJGLAS", midboth=True, blocking=True, blockhitscan=True, blockprojectiles=True)

BASINS = {}             # tag -> dict(name, floor, area, brim, kind, depth, at)
AREAS = {}              # name -> (box, floor): where monsters and things may stand
TAKEN = []              # (x, y, r): what stands where
AVOID = []              # (x, y): fronts of frames and doors: nothing placed near


def basin(tag, brim, kind=W.NORMAL, depth=0, at=None):
    BASINS[tag] = dict(name=NAMES[tag], floor=None, area=0, brim=brim, kind=kind, depth=depth, at=at)


def S(box, floor, lk, *, ceil=None, tag=0, area=None, mm=None, **k):
    """A rectangular sector `box` at `floor` in the look `lk`; `tag` a basin's
    (its plan area counts, unless `area` False) or any other sector tag.
    `mm`: into another Map than the level's (the left-handed bath's source)."""
    d = dict(lk)
    c = d.pop("ceil")
    d.update(k)
    i = (mm or m).sector(rect(*box), floor=floor, ceil=c if ceil is None else ceil, id=tag, **d)
    if tag in BASINS:
        b = BASINS[tag]
        b["floor"] = floor if b["floor"] is None else min(b["floor"], floor)
        if area is not False:
            b["area"] += (box[2] - box[0]) * (box[3] - box[1])
    return i


def stairs(a, b, out, floor, rise, steps, depth, lk, *, ceil=None, tag=0, mm=None):
    d = dict(lk)
    c = d.pop("ceil")
    ajarmap.stairs(mm or m, a, b, out, floor, rise, steps=steps, depth=depth, ceil=c if ceil is None else ceil, id=tag, **d)
    if tag in BASINS:
        bb = BASINS[tag]
        w = abs(a[0] - b[0]) + abs(a[1] - b[1])
        bb["area"] += w * depth * steps
        lowest = min(floor + rise * (i + 1) // steps for i in range(steps))
        bb["floor"] = lowest if bb["floor"] is None else min(bb["floor"], lowest)


def area(name, box, floor):
    AREAS[name] = (box, floor)


FRAMES = {}             # n -> dict(basin, sill, place, mouth, out)
FARS = {}               # colour -> dict(basin, sill)


def front(a, b, out, d=32):
    return ((a[0] + b[0]) / 2 - out[0] * d, (a[1] + b[1]) / 2 - out[1] * d)


def frame(a, b, out, n, sill, tag, place):
    ajarmap.recess(m, a, b, out, sill, n, far_id(BLUE), tag=tag)
    FRAMES[n] = dict(basin=tag, sill=sill, place=place, mouth=((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), out=out)
    AVOID.append(front(a, b, out))


def far(a, b, out, colour, sill, tag):
    ajarmap.recess(m, a, b, out, sill, far_id(colour), 101, far_colour=colour, tag=tag)
    FARS[colour] = dict(basin=tag, sill=sill, mouth=((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), out=out)


def gauge(a, b):
    W.gauge(m, a, b)


def opening(box, floor, lk=None, height=96):
    lk = lk or dict(light=170, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF", ceil=0)
    d = dict(lk)
    d.pop("ceil")
    OPENINGS.add(m.sector(rect(*box), floor=floor, ceil=floor + height, **d))
    AVOID.append(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2))


def squeeze(a, b, out, floor, *, thick=16):
    ajarmap.squeeze(m, a, b, out, floor, thick=thick)
    OPENINGS.add(len(m.sectors) - 1)


def pressure(a, b, out, sill, tag, sides, *, thick=32, auto=False):
    W.pressure_door(m, a, b, out, sill, tag, sides, LAMP0 + tag - 40, thick=thick, auto=auto, **pdoor_look())
    PDOORS[tag] = dict(sill=sill, sides=sides, auto=auto)
    AVOID.append(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))


PDOORS = {}
_PICKEYS = {}


def hang(mm, a, b, out, kind, base, *, part="mid", H=None, z0=None, **k):
    """In the look: the wall piece a-b, seen looking `out`, shows a picture of `kind` (gfx_highwater) on
    the wall texture `base` (its H and z0 unless given): `part` "mid" on a wall, "upper" over a way,
    "lower" under one. The same picture asked for twice is one texture."""
    if not LOOK:
        return None
    w = abs(a[0] - b[0]) + abs(a[1] - b[1])
    spec = dict(kind=kind, w=w, H=H, z0=z0, base=base, shift=I1._shift(a, b, out), **k)     # (H, z0: the base's, at the end)
    key = repr(sorted(spec.items()))
    name = _PICKEYS.get(key)
    if name is None:
        name = _PICKEYS[key] = f"AJVP{len(_PICKEYS):02d}"
        PICS[name] = spec
    mm.cut(a, b)
    mm.line(a, b, exact=True, **{part: name})
    return name


def named(a, b, out, base, words, head):
    """A plate over the way a-b (seen looking `out`, through the wall `base`), whose head is at `head`:
    the words of what is beyond, one line each."""
    return hang(m, a, b, out, "sign", base, part="upper", words=words, head=head)

# =================================================================================================
# THE BATHS (stage 1, "see it")
# =================================================================================================
basin(TP, 232, at=(800, 256))
basin(TSB, 0, at=(-704, 256))
# --- the changing room: the start ----------------------------------------------------------------
CR0 = (0, 0, 448, 384)
S(CR0, 0, CHANGE)
area("cr0", CR0, 0)
m.thing(224, 64, 1, angle=90)
TAKEN.append((224, 64, 64))
# --- the swimming bath, off it: the pool (the pit at -160, the shallow end at -96, steps up to the poolside)
# and the secret way out (PLAN.md, "MAP20: the secret way out, as decided"): the fourth of the five panes in
# the pit's far wall is not a mirror but a fixed line portal onto the left-handed bath, the bath built a
# second time reflected in the panes' plane (tools/lefthand.py), whose water is kept at this one's (water.zs,
# a FOLLOW basin) and which has one thing more: a door in the north wall by the shallow end, a passage, a
# secret sector and the Exit_Secret line. AJAR_SBMIRROR=1 ./build.sh makes the fourth pane a mirror like the
# others (for the comparison of the two only).
SBL = look("SB", 215, 320, PALE)
SB_PIT = -160
wall_tex("AJVSB", SBL["ceil"] - SB_PIT, SBL["ceil"], "bath", rim=0)     # the pit's floor to the roof
TSBL = 30                       # the left-handed bath's sectors (a FOLLOW basin: TSB's level)
SB_GLASS = -848                 # the panes' glass, the plane the copy is reflected in
SB_PANES = (32, 128, 224, 320, 416)
SB_OPEN = 3                     # the fourth pane (y 320..384) is the opening
SB_OPENING, SB_FAR = 1440, 1441     # its portal line, and its image in the copy
SB_SHIFT = (32, -2048)          # the copy is reflected in x = -848, then moved by this: (x, y) -> (-1664 - x, y - 2048)
SB_MIRROR = bool(_os.environ.get("AJAR_SBMIRROR"))
SB_BOX = (-896, -64, 0, 640)    # the bath, its panes' stub and its frames' recesses (the build's checks)
SB_DOOR = (-480, -416)          # the copy's door in the north wall (y 640), by the shallow end
EXIT_SECRET = 244
TRIM = dict(wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")


def empty_recess(mm, a, b, out, sill, tag):
    """A frame's recess as ajarmap.recess makes it, empty for good: the blank frame on its back line
    (the look of an empty frame at load, AjarHandler.Link), no portal, no AjarFrame, no number."""
    q = lambda p, d: (p[0] + out[0] * d, p[1] + out[1] * d)
    b1, b2 = q(a, ajarmap.DEPTH), q(b, ajarmap.DEPTH)
    mm.sector([a, b, b2, b1], floor=sill, ceil=sill + ajarmap.DOOR_H, light=176, id=tag, **TRIM)
    mm.sector([b1, b2, q(b2, ajarmap.STUB), q(b1, ajarmap.STUB)], floor=sill, ceil=sill + ajarmap.DOOR_H, light=96,
              id=tag, **TRIM)
    mm.line(b1, b2, mid="AJFRAME", blocking=True, blockeverything=True, blocksound=True)


def swimming_bath(mm, tag, copy=False):
    """The swimming bath into the Map mm, its water's sectors tagged `tag`: the room (mm the level's map),
    or the source of the left-handed bath (`copy`: its frames empty recesses, its way in a door that does
    not open, and the one thing more: the door in the north wall and the way out behind it)."""
    S((-832, 0, -576, 384), -160, SBL, tag=tag, mm=mm)                         # the pit ...
    S((-832, 384, -672, 512), -160, SBL, tag=tag, mm=mm)
    stairs((-672, 384), (-672, 512), (1, 0), -160, 64, 4, 24, SBL, tag=tag, mm=mm)     # ... its steps up to the shallow end
    S((-576, 0, -416, 512), -96, SBL, tag=tag, mm=mm)                          # the shallow end
    stairs((-416, 0), (-416, 512), (1, 0), -96, 96, 4, 24, SBL, tag=tag, mm=mm)    # up to the poolside (the last step is 0)
    S((-320, 0, -32, 640), 0, SBL, mm=mm)                                      # the poolside
    S((-832, 512, -320, 640), 0, SBL, mm=mm)
    # the way in from the changing room: a door in a trim surround (so that nothing beyond it is seen in the
    # panes: the copy has no changing room); in the copy it does not open
    mm.sector(rect(-32, 128, -24, 192), floor=0, ceil=96, light=170, **TRIM)
    d = mm.sector(rect(-24, 128, -8, 192), floor=0, ceil=0, light=160, wall="AJHDOR", ftex="AJTRIMF", ctex="AJTRIMF")
    mm.sector(rect(-8, 128, 0, 192), floor=0, ceil=96, light=170, **TRIM)
    for x in (-24, -8):
        mm.line((x, 128), (x, 192), back=d, **({} if copy else dict(special=12, args=(0, 16, 150), playeruse=True,
                                                                         repeatspecial=True)))
    for y in (128, 192):
        mm.line((-24, y), (-8, y), mid="AJTRIM", dontpegbottom=True)
    # five tall panes in the pit's far wall: four mirrors and the opening
    for k, y in enumerate(SB_PANES):
        mm.sector(rect(SB_GLASS, y, -832, y + 64), floor=0, ceil=288, light=200, **TRIM)
        if k == SB_OPEN and not SB_MIRROR:
            mm.sector(rect(SB_GLASS - 48, y, SB_GLASS, y + 64), floor=0, ceil=288, light=96, **TRIM)   # the stub behind the portal
            ids = (SB_FAR, SB_OPENING) if copy else (SB_OPENING, SB_FAR)
            mm.line((SB_GLASS, y), (SB_GLASS, y + 64), id=ids[0], special=156, args=(ids[1], 0, 1, 1))  # Line_SetPortal
        else:
            mm.line((SB_GLASS, y), (SB_GLASS, y + 64), special=182)                # Line_Mirror
            mm.line((-832, y), (-832, y + 64), blocking=True, blockeverything=True)
    if copy:
        empty_recess(mm, (-768, 0), (-704, 0), (0, -1), -160, tag)
        empty_recess(mm, (-528, 0), (-464, 0), (0, -1), -96, tag)
    else:
        frame((-768, 0), (-704, 0), (0, -1), 141, -160, tag, "sb")
        frame((-528, 0), (-464, 0), (0, -1), 142, -96, tag, "sb")
    W.gauge(mm, (-640, 0), (-576, 0))
    # painted on the pool's north wall under its rim: read mirrored in the copy, as in a mirror
    hang(mm, (-832, 512), (-704, 512), (0, 1), "words", "AJVSB", part="lower", H=160, z0=0, words=("DEEP END",), at=-12)
    hang(mm, (-576, 512), (-448, 512), (0, 1), "words", "AJVSB", part="lower", H=96, z0=0, words=("SHALLOW END",), at=-12)
    if copy:
        # the one thing not as it was: a door in the north wall by the shallow end (an ordinary one, in a trim
        # surround), a short passage, the secret sector, and the line with Exit_Secret
        x1, x2 = SB_DOOR
        mm.sector(rect(x1, 640, x2, 648), floor=0, ceil=96, light=170, **TRIM)
        mm.line((x1, 640), (x2, 640), upper=SBL.get("wall", "AJWALL"))                           # the bath's own wall over it
        d = mm.sector(rect(x1, 648, x2, 664), floor=0, ceil=0, light=160, wall="AJHDOR", ftex="AJTRIMF", ctex="AJTRIMF")
        mm.sector(rect(x1 - 16, 664, x2 + 16, 792), floor=0, ceil=128, light=200, special=1024, **TRIM)   # secret
        mm.sector(rect(x1 - 16, 792, x2 + 16, 856), floor=0, ceil=128, light=200, **TRIM)
        for y in (648, 664):
            mm.line((x1, y), (x2, y), back=d, special=12, args=(0, 16, 150), playeruse=True, repeatspecial=True)
        for x in (x1, x2):
            mm.line((x, 648), (x, 664), mid="AJTRIM", dontpegbottom=True)
        mm.line((x1 - 16, 792), (x2 + 16, 792), special=EXIT_SECRET, playercross=True)


swimming_bath(m, TSB)
area("sb", (-320, 0, -32, 640), 0)
AVOID.append((-16, 160))
PANE_SILL = 0

# --- the plunge hall P ---------------------------------------------------------------------------------
P_BOX = (480, 0, 1120, 512)
GALLERY, LANDING, LEDGE, COAMING = 128, 240, 216, 232
S((480, 0, 544, 128), 0, BATH, tag=TP)
stairs((480, 128), (544, 128), (0, 1), 0, GALLERY, 8, 32, BATH, tag=TP)       # up to the gallery, under water
S((544, 0, 1040, 384), 0, BATH, tag=TP)
S((1040, 0, 1120, 128), 0, BATH, tag=TP)
S((1040, 320, 1120, 384), 0, BATH, tag=TP)
S((480, 384, 1120, 448), GALLERY, BATH, tag=TP)                                # the gallery
S((480, 448, 576, 512), GALLERY, BATH, tag=TP)
stairs((576, 448), (576, 512), (1, 0), GALLERY, LANDING - GALLERY, 7, 32, BATH, tag=TP)   # on up, to the gallery door
S((800, 448, 864, 512), LANDING, BATH)                                         # the landing, over the brim
S((864, 448, 1120, 512), GALLERY, BATH, tag=TP)
S((1040, 128, 1056, 320), COAMING, BATH)                                       # the ledge's coaming, round three sides ...
S((1056, 128, 1120, 144), COAMING, BATH)
S((1056, 304, 1120, 320), COAMING, BATH)
S((1056, 144, 1120, 304), LEDGE, BATH)                                         # ... and the ledge: no stair
area("p", (544, 0, 1040, 384), 0)
area("ledge", (1056, 144, 1120, 304), LEDGE)
pressure((448, 32), (448, 96), (1, 0), 0, PD_P, (0, TP))                       # P's own door from the changing room
ajarmap.bolted(m, (800, 512), (864, 512), (0, 1), LANDING, GD_TAG, thick=96)   # the gallery's door, bolted on its far side
frame((736, 0), (800, 0), (0, -1), 101, 0, TP, "p")
frame((960, 512), (1024, 512), (0, 1), 102, GALLERY, TP, "p_gal")
gauge((544, 0), (608, 0))
# the ledge door: opens by USE and stays open (a stage gate)
m.sector(rect(1120, 192, 1152, 256), floor=LEDGE, ceil=LEDGE, light=160, wall=DOOR_FACE if LOOK else "BIGDOOR2",
         ftex="FLAT20", ctex="FLAT20", id=LEDGE_TAG)
for x in (1120, 1152):
    m.line((x, 192), (x, 256), special=11, args=(LEDGE_TAG, 32), playeruse=True, repeatspecial=True)
for y in (192, 256):
    m.line((1120, y), (1152, y), mid="DOORTRAK", dontpegbottom=True)
AVOID.append((1136, 224))

# --- the changing room's upper floor (240): from the ledge by the pump corridor ---------------------------------
UPPER = look("CU", 196, 400, PAPER)
S((0, 608, 1056, 864), LANDING, UPPER)
S((1056, 608, 1120, 864), LANDING, UPPER)
area("cr1", (0, 608, 1056, 864), LANDING)

# =================================================================================================
# THE PUMP CORRIDOR, THE PUMP HOUSE, THE COOLING HALL (stage 2, "drain it")
# =================================================================================================
S((1152, 160, 1184, 288), LEDGE, CORR)
S((1184, 160, 1472, 288), LEDGE, CORR)
ajarmap.unbolt(m, (1184, 160), (1184, 288), GD_TAG)                            # the first steps from the ledge draw the gallery's bolt
S((1152, 288, 1216, 672), LEDGE, CORR)
opening((1120, 608, 1152, 672), LANDING)
area("pc", (1184, 160, 1472, 288), LEDGE)
area("pcn", (1152, 288, 1216, 672), LEDGE)
PH_Z = 104
stairs((1472, 160), (1472, 288), (1, 0), LEDGE, PH_Z - LEDGE, 8, 32, CORR)
opening((1728, 160, 1760, 288), PH_Z)
PH = (1760, 0, 2272, 768)
S(PH, PH_Z, PUMP, ceil=PH_Z + 288)
area("ph", PH, PH_Z)
opening((2272, 672, 2304, 736), PH_Z)

C_FLOOR, C_LAND, WALK, C_BRIM, C_FOUND = -128, 0, 104, 100, 96
basin(TC, C_BRIM, depth=C_FOUND - C_FLOOR, at=(2816, 384))
CH = dict(HALL)
CW = look("CW", 170, 400, COLD)
S((2304, 640, 3328, 768), WALK, CW)                                            # the walkway: north ...
S((2304, 256, 2368, 640), WALK, CW)                                            # ... west ...
S((3264, 256, 3328, 640), WALK, CW)                                            # ... and east
stairs((2304, 256), (2368, 256), (0, -1), WALK, C_LAND - WALK, 5, 32, CH, tag=TC)     # down to the landing
S((2304, 0, 2496, 96), C_LAND, CH, tag=TC)                                     # the landing
stairs((2496, 0), (2496, 96), (1, 0), C_LAND, C_FLOOR - C_LAND, 6, 32, CH, tag=TC)    # on down to the floor
S((2368, 96, 3264, 640), C_FLOOR, CH, tag=TC)
S((2688, 0, 3264, 96), C_FLOOR, CH, tag=TC)
S((3264, 0, 3328, 256), C_FLOOR, CH, tag=TC)
area("cwalk", (2304, 640, 3328, 768), WALK)
area("cwalkw", (2304, 256, 2368, 640), WALK)
area("cwalke", (3264, 256, 3328, 640), WALK)
area("cfloor", (2368, 96, 3264, 640), C_FLOOR)
frame((2944, 768), (3008, 768), (0, 1), 111, WALK, TC, "cwalk")
frame((2368, 0), (2432, 0), (0, -1), 112, C_LAND, TC, "c")
frame((2752, 0), (2816, 0), (0, -1), 113, C_FLOOR, TC, "c")
gauge((2880, 0), (2944, 0))
pressure((2944, 0), (3008, 0), (0, -1), C_FLOOR, PD_E2, (TC, 0))               # E2: to the passage and the boiler house
CELL_A, CELL_B = (3024, -400, 3200, -32), (3216, -400, 3424, -32)
CELL = look("CL", 120, C_FLOOR + 128, RUST)
S(CELL_A, C_FLOOR, CELL)
S(CELL_B, C_FLOOR, dict(CELL, **(dict(wall="MARBLE2") if LOOK else {})))
pressure((3104, 0), (3168, 0), (0, -1), C_FLOOR, PD_CA, (TC, 0), auto=True)    # the cells: open when C is first dry
pressure((3232, 0), (3296, 0), (0, -1), C_FLOOR, PD_CB, (TC, 0), auto=True)
# the passage from E2, and its stair up to the boiler house
PASS = look("PA", 150, C_FLOOR + 128, COLD)
S((2944, -480, 3008, -32), C_FLOOR, PASS)
S((3008, -480, 3712, -416), C_FLOOR, PASS)
stairs((3648, -416), (3712, -416), (0, 1), C_FLOOR, 0 - C_FLOOR, 8, 48, PASS, ceil=160)
opening((3648, -32, 3712, 0), 0)
area("pass", (3008, -480, 3712, -416), C_FLOOR)
# the gangway: from the east walkway down to the boiler house, bolted on its side
ajarmap.bolted(m, (3328, 384), (3328, 448), (1, 0), WALK, GW_TAG, thick=32)
stairs((3360, 384), (3360, 448), (1, 0), WALK, -WALK, 8, 28, look("BS", 180, 344, MINT), ceil=WALK + 160)
GANGWAY_STEP = 28
# the bolt's Doom switch (PLAN.md, "Look: MAP20"): on the gangway's north wall beside the door, the plate's
# lamp and lever (the columns SW1 and SW2 differ in: 22..40) on the top step's piece of wall, which alone
# has the special; the switch's texture runs on over the next step's
SWITCH_X0 = 3344                # the switch texture's column 0 is at this x (its plate's left edge at 3360)
m.cut((SWITCH_X0 + 64, 448))
for _x1, _x2 in ((3360, 3360 + GANGWAY_STEP), (3360 + GANGWAY_STEP, SWITCH_X0 + 64)):
    SWITCH_AT[((_x1, 448), (_x2, 448))] = _x1 - SWITCH_X0
m.line((3360, 448), (3360 + GANGWAY_STEP, 448), special=11, args=(GW_TAG, 32), playeruse=True)   # as the door's own line

# =================================================================================================
# THE BOILER HOUSE AND THE FEED TANK (stage 3, "the pipe")
# =================================================================================================
T_BRIM = 272
basin(TT, T_BRIM, at=(4200, 640))
BH = (3584, 0, 4352, 768)
S((3584, 0, 4352, 416), 0, BOIL)
S((3584, 416, 4064, 704), 0, BOIL)
S((3584, 704, 3712, 768), 0, BOIL)
TANK = look("TK", 176, 448, RUST)
stairs((3712, 704), (3712, 768), (1, 0), 0, T_BRIM, 16, 22, look("BS", 176, 448, RUST))   # the dry stair up to the rim
S((4064, 416, 4352, 480), T_BRIM, look("CT", 176, 448, RUST))                  # the catwalk
S((4064, 480, 4096, 528), T_BRIM, TANK)                                        # the tank's west wall, its rim at 272 ...
pressure((4064, 528), (4064, 592), (1, 0), 0, PD_T, (0, TT))                    # ... the manhole ...
S((4064, 592, 4096, 608), T_BRIM, TANK)
m.sector(rect(4064, 608, 4096, 624), floor=8, ceil=T_BRIM - 8, light=200, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF",
         id=TT)                                                                # ... the gauge glass (the water stands in it) ...
for x in (4064, 4096):
    m.line((x, 608), (x, 624), **GLASS)
S((4064, 624, 4096, 768), T_BRIM, TANK)
m.cut((4064, 624), (4064, 688))
m.line((4064, 624), (4064, 688), lower="AJFLOATM", dontpegbottom=False)       # ... and the float mark beside it
S((4096, 480, 4352, 512), T_BRIM, TANK)                                        # the south wall's rim
S((4096, 512, 4288, 768), 0, TANK, tag=TT)                                     # in the tank
stairs((4288, 768), (4352, 768), (0, -1), 0, T_BRIM, 16, 16, TANK, tag=TT)     # its stair up to the rim, under water
area("bh", (3584, 0, 4352, 416), 0)
area("bhw", (3584, 416, 4064, 704), 0)
area("catwalk", (4064, 416, 4352, 480), T_BRIM)
frame((4160, 768), (4224, 768), (0, 1), 121, 0, TT, "t")
gauge((4224, 768), (4288, 768))
W.float_gate(m, 4200, 704, TT, FLOAT_MARK, YARD_TAG, FLOAT_SECONDS)
# the yard gate, which the float raises
m.sector(rect(3616, 768, 3680, 864), floor=0, ceil=0, light=160, wall="AJSHUT", ftex="AJTRIMF", ctex="AJTRIMF", id=YARD_TAG)
for x in (3616, 3680):
    m.line((x, 768), (x, 864), mid="AJTRIM", dontpegbottom=True)
AVOID.append((3648, 816))

# =================================================================================================
# THE YARDS, THE LOCK, THE WHEEL HOUSE (stages 4 and 5)
# =================================================================================================
LY = (3584, 864, 5184, 1856)
UY_Z, K_SILL, K_SHELF, K_BRIM = 192, 192, 88, 200
L_FLOOR, L_BRIM, U_FLOOR, CREST, U_BRIM = -96, -4, 128, 160, 184
FOUNTAIN = (4352, 1216, 4864, 1536)
CD.fit(LY, [(FOUNTAIN, dict(floor=40, **(dict(side="AJVBU", ftex="AJVFK") if LOOK else {}))),   # a fountain's basin: its curb is 40 high
            ((4384, 1248, 4832, 1504), dict(floor=16, ftex="AJVFK" if LOOK else "FLAT5_4", id=FOUNTAIN_TAG)),   # dry at rest (water.zs)
            ((5168, 1280, 5184, 1344), dict(ceil=112, ctex="TLITE6_5", light=96, id=WLAMP))],   # the wheel's lamp
       floor=0, **YARD)
area("ly", LY, 0)
AREAS["ly"] = (LY, 0)
LY_OBST = [FOUNTAIN]
# the sluice, the tunnel, the machine hall (the way out)
m.sector(rect(5184, 1280, 5216, 1344), floor=0, ceil=0, light=160, wall="AJSHUT", ftex="AJTRIMF", ctex="AJTRIMF", id=SLUICE)
for y in (1280, 1344):
    m.line((5184, y), (5216, y), mid="AJTRIM", dontpegbottom=True)
AVOID.append((5160, 1312))
TUNNEL = (5216, 1248, 5600, 1376)
SEAM = 5408                     # the tunnel's brick gives way to Doom's here (the look)
if LOOK:
    S((TUNNEL[0], TUNNEL[1], SEAM, TUNNEL[3]), 0, look("TN", 140, 128, COLD))
    S((SEAM, TUNNEL[1], TUNNEL[2], TUNNEL[3]), 0, look("TD", 140, 128, COLD))
else:
    S(TUNNEL, 0, look("TN", 140, 128, COLD))
area("tunnel", TUNNEL, 0)
# the machine hall, and the way out: a Doom exit door in the middle of its east wall (a strip as high as the
# door before it, the door 16 thick, Door_Raise by USE), Doom's EXIT sign on a box hung from the hall's ceiling
# before the door (nothing stands or walks so high), and behind the door our own way out, the night room
# (ajarmap.way_out), turned a quarter so that the door opens straight into it (Vadim, 2026-11-24: "door can be
# marked this way, yes, but inside should be our portal exit")
MH = (5600, 1056, 6048, 1568)
EXIT_MOUTH, EXIT_H = (1280, 1344), 72               # EXITDOOR is 72 high
SIGNBOX = (5992, 1296, 6008, 1328)                  # (EXITSIGN's sign is its left 32)
CD.fit(MH, [(SIGNBOX, dict(ceil=MH_CEIL - 16, wall=EXIT_SIGN, ctex="CEIL5_1"))], floor=0, **WORKS)
for _y in (SIGNBOX[1], SIGNBOX[3]):
    m.line((SIGNBOX[0], _y), (SIGNBOX[2], _y), upper="METAL")
EX = MH[2]
m.sector(rect(EX, EXIT_MOUTH[0], EX + 8, EXIT_MOUTH[1]), floor=0, ceil=EXIT_H, light=190,
         wall=WORKS.get("wall", "AJWALL"), ftex="FLAT20", ctex="FLAT20")
m.line((EX, EXIT_MOUTH[0]), (EX, EXIT_MOUTH[1]), dontpegtop=True)                # the hall's wall over the door
_d = m.sector(rect(EX + 8, EXIT_MOUTH[0], EX + 24, EXIT_MOUTH[1]), floor=0, ceil=0, light=190, wall=EXIT_FACE,
              ftex="FLAT20", ctex="FLAT20")
for _x in (EX + 8, EX + 24):
    m.line((_x, EXIT_MOUTH[0]), (_x, EXIT_MOUTH[1]), back=_d, special=12, args=(0, 16, 150), playeruse=True,
           repeatspecial=True)
for _y in EXIT_MOUTH:
    m.line((EX, _y), (EX + 24, _y), mid="DOORTRAK", dontpegbottom=True)
# the night room's side of the door, as the hall's: a strip 8 deep as high as the door (its threshold: the night
# room's carpet under, its starry ceiling over, its wall on the two short sides, laid from the floor as the room's),
# so that from inside too the door's back is EXITDOOR, under the night room's wall
NIGHT_STRIP = (EX + 24, EXIT_MOUTH[0], EX + 32, EXIT_MOUTH[1])
m.sector(rect(*NIGHT_STRIP), floor=0, ceil=EXIT_H, light=180, wall="AJXW2", ftex="AJXR2", ctex="AJXC2",
         raw=dict(rotationfloor=90.0, rotationceiling=90.0))
for _y in EXIT_MOUTH:
    m.line((NIGHT_STRIP[0], _y), (NIGHT_STRIP[2], _y), dontpegbottom=True)
# the night room: 256 by 320, its west wall's middle the strip (its way in, y 1280..1344), the brass doorway
# joining its south and north ends (Exit_Normal at both mouths, x 6176..6240 at y 1152 and 1472)
NIGHT = (NIGHT_STRIP[2], EXIT_MOUTH[0] - 128)      # its south-west corner, (6080, 1152)
NIGHT_BOX = (NIGHT[0], NIGHT[1] - ajarmap.DEPTH - ajarmap.STUB, NIGHT[0] + 256, NIGHT[1] + 320 + ajarmap.DEPTH + ajarmap.STUB)
NIGHT_SECTORS = range(len(m.sectors), len(m.sectors) + 13)  # its 9 cells and its doorway's 2 recesses and 2 stubs
ajarmap.way_out(m, *NIGHT, None, turned=True)
assert len(m.sectors) == NIGHT_SECTORS.stop
# the wall over the strip, from inside, hung from the room's ceiling as the walls beside it (the stars run on)
m.line((NIGHT[0], EXIT_MOUTH[0]), (NIGHT[0], EXIT_MOUTH[1]), dontpegtop=True)
area("mh", MH, 0)
# the outfall (GREEN's far side), seen from the lower yard through glass
basin(TO, 256, kind=W.OUTFALL, at=(5408, 1664))
S((5248, 1504, 5568, 1824), 0, look("OV", 140, 256, COLD), tag=TO)
far((5568, 1632), (5568, 1696), (1, 0), GREEN, 0, TO)
m.sector(rect(5184, 1600, 5248, 1728), floor=24, ceil=168, light=200, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
for x in (5184, 5248):
    m.line((x, 1600), (x, 1728), **GLASS)

# --- the lock K ------------------------------------------------------------------------------------------
basin(TK, K_BRIM, at=(4032, 2080))
KL = sky("KS", 210, 512)
BU = sky("BU", 210, 512)
S((3904, 1920, 4160, 2240), 0, KL, tag=TK)
S((4160, 1920, 4224, 2112), 0, KL, tag=TK)
S((4160, 2112, 4224, 2240), K_SHELF, KL, tag=TK)                               # the shelf: only a swimmer reaches it
S((3968, 2240, 4096, 2304), K_SILL, KL)                                        # the open sill onto the upper yard
pressure((3968, 1856), (4032, 1856), (0, 1), 0, PD_K, (0, TK), thick=64)        # from the lower yard
frame((3904, 1984), (3904, 2048), (-1, 0), 131, 0, TK, "k")
frame((4224, 1984), (4224, 2048), (1, 0), 135, 0, TK, "k")
frame((4224, 2144), (4224, 2208), (1, 0), 133, K_SHELF, TK, "shelf")
gauge((3904, 2176), (3904, 2240))
# the lock's own way out at any level, empty handed: through a squeeze at its floor and up a stair behind
# its west wall to the upper yard (a door cannot go through the squeeze, so it is not a way up for one)
S((3840, 2080, 3888, 2144), 0, KL, tag=TK)
stairs((3840, 2144), (3888, 2144), (0, 1), 0, K_SILL, 8, 12, KL, tag=TK)
S((3840, 2240, 3888, 2304), K_SILL, KL, tag=TK)
squeeze((3904, 2096), (3904, 2144), (-1, 0), 0, thick=16)
area("k", (3904, 1920, 4160, 2240), 0)

# --- the squeeze stair (empty hands, both ways) and the terrace (a drop, any hands) between the yards ------
squeeze((3648, 1856), (3696, 1856), (0, 1), 0, thick=32)
S((3632, 1888, 3712, 1936), 0, BU)
stairs((3632, 1936), (3712, 1936), (0, 1), 0, UY_Z, 10, 32, BU)
S((3632, 2256, 3712, 2272), UY_Z, BU)
opening((3632, 2272, 3712, 2304), UY_Z, sky("BU", 200, UY_Z + 128))
S((3744, 1856, 3808, 2304), UY_Z, BU)                                          # the terrace: a drop into the lower yard

# --- the upper yard --------------------------------------------------------------------------------------
UY = (3584, 2304, 5184, 3264)
S(UY, UY_Z, UPYARD)
area("uy", UY, UY_Z)
# the reservoir (BLUE's far side) in the water tower, behind glass
basin(TR, 448, kind=W.RESERVOIR, depth=96, at=(5408, 2784))
S((5248, 2624, 5568, 2944), UY_Z, look("RS", 200, 448, STEEL), tag=TR)
far((5568, 2752), (5568, 2816), (1, 0), BLUE, UY_Z, TR)
m.sector(rect(5184, 2720, 5248, 2848), floor=UY_Z + 24, ceil=UY_Z + 168, light=200, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
for x in (5184, 5248):
    m.line((x, 2720), (x, 2848), **GLASS)

# --- the wheel house: L (the lower pool), U (the upper pool), the spillway and its wheel ------------------
basin(TL, L_BRIM, at=(4700, 2000))
basin(TU, U_BRIM, at=(4600, 2192))
WH, WHU, WHT = sky("WL", 200, 448), sky("WU", 200, 448), sky("WT", 200, 448)
stairs((4480, 1856), (4608, 1856), (0, 1), 0, L_FLOOR, 4, 16, WH, tag=TL)      # down into L from the lower yard
S((4416, 1920, 5120, 2080), L_FLOOR, WH, tag=TL)
stairs((4480, 2304), (4608, 2304), (0, -1), UY_Z, U_FLOOR - UY_Z, 4, 16, WHU, tag=TU)   # down into U from the upper yard
S((4416, 2144, 4800, 2240), U_FLOOR, WHU, tag=TU)
S((4800, 2144, 4832, 2240), CREST, WHU, tag=TU)                                # the crest
stairs((4832, 2240), (4960, 2240), (0, -1), CREST, L_FLOOR - CREST, 8, 20, WHT, tag=CHUTE)   # the spillway, down into L
frame((5120, 1984), (5120, 2048), (1, 0), 107, L_FLOOR, TL, "l")
frame((4416, 1952), (4416, 2016), (-1, 0), 109, L_FLOOR, TL, "l")
frame((4416, 2160), (4416, 2224), (-1, 0), 108, U_FLOOR, TU, "u")
gauge((4672, 1920), (4736, 1920))
gauge((4672, 2240), (4736, 2240))
W.weir(m, 4896, 2176, TU, TL, CREST, CHUTE, WLAMP, SLUICE)

# --- the basins' things, the rate -------------------------------------------------------------------------
for tag, b in BASINS.items():
    W.basin(m, tag, b["area"], b["brim"], floor=b["floor"], kind=b["kind"], depth=b["depth"], at=b["at"])
W.rate(m, 224, 192, K_FLOW, FREE, W.FLOAT | W.OVERFLOW, WHEEL_TICS)

# --- the left-handed bath: the swimming bath built again on its own (with its one thing more), reflected in
# the panes' plane and put far south, an island joined to the level only by the opening; off the automap until
# the player stands in it. Its water is not a basin of its own: it follows the swimming bath's every tic.
SB_SRC = Map()
SB_SRC.align = set(m.align)
SB_SRC.line_hook = make_hook(SB_SRC, set())
swimming_bath(SB_SRC, TSBL, copy=True)
SB_COPY_BOX = lefthand.left_handed(m, SB_SRC, "x", SB_GLASS, SB_SHIFT, hide=True)
W.basin(m, TSBL, BASINS[TSB]["area"], BASINS[TSB]["brim"], floor=BASINS[TSB]["floor"], kind=W.FOLLOW, depth=TSB,
        at=(-704, 320))                     # (the thing only names it: it stands by the swimming bath's own)

# =================================================================================================
# THE DOORS
# =================================================================================================
ajarmap.door(m, BLUE, 672, 160, angle=0)                                       # BLUE leans by the plunge
ajarmap.door(m, GREEN, 2208, 384, angle=180)                                   # GREEN in the pump house
ajarmap.pair(m, TEAL, (2624, 352, 90), (2944, 288, 90))                        # both TEAL leaves on C's floor
for x, y in ((672, 160), (2208, 384), (2624, 352), (2944, 288)):
    TAKEN.append((x, y, 40))


# =================================================================================================
# THE LOOK: the walls at their heights, the pictures and the plates (PLAN.md, "Look: MAP20, Municipal")
# =================================================================================================
wall_tex("AJVCR", CHANGE["ceil"], CHANGE["ceil"], "tiled", floor=0)
wall_tex("AJVCU", UPPER["ceil"] - LANDING, UPPER["ceil"], "tiled", floor=LANDING)
wall_tex("AJVPL", BATH["ceil"], BATH["ceil"], "plunge", brim=BASINS[TP]["brim"], step=64)
wall_tex("AJVEC", CORR["ceil"] - PH_Z, CORR["ceil"], "engine", dados=(LEDGE, PH_Z))
wall_tex("AJVPH", 288, PH_Z + 288, "pumps", floor=PH_Z)
wall_tex("AJVPA", 160 - C_FLOOR, 160, "engine", dados=(C_FLOOR,))
wall_tex("AJVCH", HALL["ceil"] - C_FLOOR, HALL["ceil"], "hall", tide=C_FOUND)
wall_tex("AJVBH", BOIL["ceil"], BOIL["ceil"], "boiler")
wall_tex("AJVTK", BOIL["ceil"], BOIL["ceil"], "tank", rim=T_BRIM)
wall_tex("AJVYD", YARD["ceil"] - L_FLOOR, YARD["ceil"], "yard", floor=0)              # (down to L's floor: the stair into L)
wall_tex("AJVYU", UPYARD["ceil"] - U_FLOOR, UPYARD["ceil"], "yard", floor=UY_Z)        # (down to U's floor: the stair into U)
wall_tex("AJVTW", UPYARD["ceil"] - UY_Z, UPYARD["ceil"], "tower", floor=UY_Z)
wall_tex("AJVTN", 128, 128, "yard", floor=0)
wall_tex("AJVOV", 256, 256, "vault", tide=64)
wall_tex("AJVRS", 448 - UY_Z, 448, "reservoir", water=BASINS[TR]["floor"] + BASINS[TR]["depth"])
wall_tex("AJVKS", KL["ceil"], KL["ceil"], "stone", stain=K_BRIM)
wall_tex("AJVBU", KL["ceil"], KL["ceil"], "stone", stain=None)
wall_tex("AJVWL", WH["ceil"] - L_FLOOR, WH["ceil"], "stone", stain=L_BRIM)
wall_tex("AJVWU", WH["ceil"] - L_FLOOR, WH["ceil"], "stone", stain=U_BRIM)           # (the crest's side, down the spillway)
wall_tex("AJVWT", WH["ceil"] - L_FLOOR, WH["ceil"], "timber", top=CREST + 32)


def pieces(a, b, spec):
    """In the look: the wall from a towards b in pieces (length, Doom texture); a texture None is the room's."""
    if not LOOK:
        return
    n = (abs(b[0] - a[0]) + abs(b[1] - a[1]))
    d = ((b[0] - a[0]) / n, (b[1] - a[1]) / n)
    p = a
    for ln, tex in spec:
        q = (p[0] + round(d[0] * ln), p[1] + round(d[1] * ln))
        m.cut(p, q)
        if tex:
            m.line(p, q, mid=tex)
            DOOM.add(tex)
        p = q
    assert p == b, (a, b, p)


# stage 1, the baths: the changing room's lockers, rules and clock; the plates; P's high water at 224
hang(m, (64, 0), (192, 0), (0, -1), "lockers", "AJVCR", first=1)
hang(m, (256, 0), (384, 0), (0, -1), "lockers", "AJVCR", first=9)
hang(m, (128, 384), (320, 384), (0, 1), "rules", "AJVCR")
hang(m, (320, 384), (384, 384), (0, 1), "clock", "AJVCR")
named((0, 128), (0, 192), (-1, 0), "AJVCR", ("SWIMMING", "BATH"), 96)
hang(m, (448, 96), (448, 160), (1, 0), "plate", "AJVCR", words=("PLUNGE",), at=100, arrow=1)
P_HIGH = "BLUE in 102"          # the measure's run whose level the plaque marks: P at 224 (BLUE's 96 over 102's sill)
hang(m, (1120, 32), (1120, 96), (1, 0), "plaque", "AJVPL", level=P_HIGH, year=1928)
named((1120, 608), (1120, 672), (1, 0), "AJVCU", ("PUMPS",), LANDING + 96)
# stage 2, the engine house
named((1728, 160), (1728, 288), (1, 0), "AJVEC", ("PUMPS",), PH_Z + 96)
named((1760, 160), (1760, 288), (-1, 0), "AJVPH", ("PLUNGE",), PH_Z + 96)
named((2272, 672), (2272, 736), (1, 0), "AJVPH", ("COOLING", "HALL"), PH_Z + 96)
named((2304, 672), (2304, 736), (-1, 0), "AJVCH", ("PUMPS",), PH_Z + 96)
C_HIGH = "GREEN in 111"         # C as found: at C_FOUND (96), its tide line
hang(m, (3008, 0), (3072, 0), (0, -1), "plaque", "AJVCH", level=C_HIGH, year=1936)
named((3648, -32), (3712, -32), (0, 1), "AJVPA", ("BOILERS",), 96)
# stage 3, the boiler house: the boilers' fronts, the section drawing (the hint for the pipe), the plates
named((3648, 0), (3712, 0), (0, -1), "AJVBH", ("COOLING", "HALL"), 96)
named((3584, 384), (3584, 448), (-1, 0), "AJVBH", ("COOLING", "HALL"), WALK + 160)
hang(m, (3776, 0), (4160, 0), (0, -1), "boilers", "AJVBH")
SECTION = (4352, 32), (4352, 352)
hang(m, *SECTION, (1, 0), "section", "AJVBH")
# stage 4, the yards and the lock
named((3648, 1856), (3696, 1856), (0, 1), "AJVYD", ("YARD",), 64)
named((3632, 2272), (3712, 2272), (0, 1), "AJVBU", ("YARD",), UY_Z + 128)
hang(m, (4032, 1856), (4096, 1856), (0, 1), "plate", "AJVYD", words=("LOCK",), at=100, arrow=-1)
K_HIGH = ("then BLUE in 133", "BLUE in 131 (alone)")    # K at 184 and at 96: the flood marks by the sill
hang(m, (4096, 1920), (4160, 1920), (0, -1), "flood", "AJVKS", levels=K_HIGH, years=(1947, 1911))
named((4480, 1856), (4608, 1856), (0, 1), "AJVYD", ("WHEEL HOUSE",), 448)
named((4480, 2304), (4608, 2304), (0, -1), "AJVYU", ("WHEEL HOUSE",), 448)
hang(m, (5184, 1216), (5184, 1280), (1, 0), "plate", "AJVYD", words=("MACHINE", "HALL"), at=100, arrow=-1)
# the outfall's glass as a culvert's mouth in the lower yard, the reservoir's in the water tower's foot
hang(m, (5184, 1600), (5184, 1728), (1, 0), "culvert", "AJVYD", part="upper", words=("OUTFALL",), head=168)
if LOOK:
    m.line((5184, 1600), (5184, 1728), lower="AJVYD")
    m.line((5184, UY[1]), (5184, 2720), mid="AJVTW")
    m.line((5184, 2848), (5184, UY[3]), mid="AJVTW")
    m.line((5184, 2720), (5184, 2848), lower="AJVTW")
hang(m, (5184, 2720), (5184, 2848), (1, 0), "tower", "AJVTW", part="upper", words=("RESERVOIR",), head=UY_Z + 168)
# stage 5, the wheel house: L's high water at -4, the patent office's answer
L_HIGH = "BLUE in 109"          # L at its brim, -4
hang(m, (4800, 1920), (4864, 1920), (0, -1), "plaque", "AJVWL", level=L_HIGH, year=1953)
hang(m, (4544, 2080), (4672, 2080), (0, 1), "patent", "AJVWL")
# stage 6: Doom leaks in. The tunnel's brick ends at the seam (a plate says so), then SUPPORT3 ribs and marble;
# the cells are Doom's stone with a demon's face; the machine hall is a Doom room; the exit door is Doom's (behind
# it, our night room)
hang(m, (SEAM - 64, TUNNEL[3]), (SEAM, TUNNEL[3]), (0, 1), "seam", "AJVTN")
for _y in (TUNNEL[1], TUNNEL[3]):
    pieces((SEAM, _y), (TUNNEL[2], _y), [(32, "SUPPORT3"), (64, None), (32, "SUPPORT3"), (64, None)])
pieces((CELL_B[0] + 40, CELL_B[1]), (CELL_B[0] + 168, CELL_B[1]), [(128, "MARBFACE")])
for _y in (MH[1], MH[3]):
    pieces((MH[0], _y), (MH[2], _y), [(64, "SUPPORT3"), (64, None), (64, None), (64, "SUPPORT3"), (64, None), (64, None),
                                      (64, "SUPPORT3")])
for _ya, _yb in ((MH[1], TUNNEL[1]), (MH[3], TUNNEL[3])):
    pieces((MH[0], _ya), (MH[0], _yb), [(64, None), (64, "SUPPORT3"), (64, None)])
for _ya, _yb in ((MH[1], EXIT_MOUTH[0]), (MH[3], EXIT_MOUTH[1])):
    pieces((MH[2], _ya), (MH[2], _yb), [(64, None), (64, "SUPPORT3"), (64, None), (32, "SUPPORT3")])


# =================================================================================================
# THE FIGHTS AND WHAT IS PICKED UP (MAP19's weapons in MAP19's order; what walks drowns)
# =================================================================================================
area("l", (4416, 1920, 5120, 2080), L_FLOOR)
area("u", (4416, 2144, 4800, 2240), U_FLOOR)
area("cella", CELL_A, C_FLOOR)
area("cellb", CELL_B, C_FLOOR)
OBST = {"ly": LY_OBST}
NOROOM = []


def halton(i, b):
    f, r = 1, 0
    while i:
        f /= b
        r += f * (i % b)
        i //= b
    return r


def spot(name, r=20):
    """A free place for a thing of radius r in area `name`: off its walls, clear of every other
    thing and of the fronts of frames and doors (a Halton sequence: the same every build)."""
    (x1, y1, x2, y2), _ = AREAS[name]
    obs = OBST.get(name, [])
    mx = min(16, (x2 - x1) / 2 - r - 1)
    my = min(16, (y2 - y1) / 2 - r - 1)
    for k in range(1, 4000):
        x = round((x1 + mx + r + halton(k, 2) * (x2 - x1 - 2 * mx - 2 * r)) / 8) * 8
        y = round((y1 + my + r + halton(k, 3) * (y2 - y1 - 2 * my - 2 * r)) / 8) * 8
        if not (x1 + r < x < x2 - r and y1 + r < y < y2 - r):
            continue
        if any(o[0] - r - 24 < x < o[2] + r + 24 and o[1] - r - 24 < y < o[3] + r + 24 for o in obs):
            continue
        if any(max(abs(x - tx), abs(y - ty)) < r + tr + 8 for tx, ty, tr in TAKEN):
            continue
        if any(math.hypot(x - ax, y - ay) < 80 for ax, ay in AVOID):
            continue
        TAKEN.append((x, y, r))
        return x, y
    NOROOM.append(name)
    return x1 + 64, y1 + 64


R = {CACO: 31, PAIN: 31, MANCUBUS: 48, ARACH: 64, BARON: 24, KNIGHT: 24, DEMON: 30, SPECTRE: 30}
COMPANY = {}            # place -> {kind: count} (the write-up)


def put(name, kind, n, angle=0, skill=None):
    for _ in range(n):
        x, y = spot(name, R.get(kind, 20))
        if skill:
            m.thing(x, y, kind, angle=angle, skill=skill)
        else:
            m.thing(x, y, kind, angle=angle)
    COMPANY.setdefault(name, {})
    COMPANY[name][kind] = COMPANY[name].get(kind, 0) + n


def wambush(name, over, tag, height, kind, n, angle=0, after=0, near=0):
    spots = [spot(name, R.get(kind, 20)) for _ in range(n)]
    W.water_ambush(m, over, tag, height, kind, *spots, angle=angle, after=after, near=near)
    key = f"{name} (water)"
    COMPANY.setdefault(key, {})
    COMPANY[key][kind] = COMPANY[key].get(kind, 0) + n


def ambush(name, cause, kind, n, angle=0, after=0, near=0):
    spots = [spot(name, R.get(kind, 20)) for _ in range(n)]
    ajarmap.ambush(m, cause, kind, *spots, angle=angle, after=after, near=near)
    key = f"{name} (ambush)"
    COMPANY.setdefault(key, {})
    COMPANY[key][kind] = COMPANY[key].get(kind, 0) + n


def item(kind, x, y):
    m.thing(x, y, kind)
    TAKEN.append((x, y, 16))


def items(name, kind, n):
    for _ in range(n):
        m.thing(*spot(name, 16), kind)


# what is picked up: the weapons where MAP19 has them in the order of the way (shotgun, chaingun,
# super shotgun, rocket launcher, plasma rifle)
item(2001, 320, 288)                                    # the shotgun: the changing room
item(2002, 1088, 224)                                   # the chaingun: on the ledge, the stage's prize
item(82, 1968, 160)                                     # the super shotgun: the pump house
item(2003, 4160, 448)                                   # the rocket launcher: the boiler house's catwalk
item(2004, 4960, 3008)                                  # the plasma rifle: the upper yard, by the reservoir's glass
item(2018, 640, 736)                                    # green armour: the changing room's upper floor
AMMO = [("cr0", 2008, 3), ("cr0", 2011, 2), ("cr0", 2008, 2), ("cr0", 2012, 1),    # (the bath's: nothing in it) ("p", 2008, 2), ("cr1", 2007, 3),
        ("cr1", 2049, 1), ("cr1", 2012, 1), ("pc", 2007, 1), ("pcn", 2011, 1), ("cr1", 2011, 1), ("ph", 2049, 2), ("ph", 2048, 1),
        ("ph", 2012, 2), ("cwalk", 2049, 2), ("cwalk", 2048, 1), ("cwalkw", 2011, 1), ("ph", 2011, 2), ("bh", 2049, 1),
        ("bh", 2046, 1), ("pass", 2012, 1), ("bh", 2046, 2), ("bh", 2049, 2), ("bh", 2048, 1), ("bh", 2012, 2),
        ("bhw", 2010, 4), ("bhw", 2011, 3), ("ly", 2046, 3), ("ly", 2049, 2), ("ly", 2048, 2), ("ly", 17, 1),
        ("ly", 2012, 3), ("ly", 2047, 3), ("uy", 17, 2), ("uy", 2046, 2), ("uy", 2049, 2), ("uy", 2012, 3),
        ("uy", 2047, 2), ("l", 2049, 1), ("l", 2012, 1), ("tunnel", 2046, 1), ("tunnel", 2012, 1),
        ("mh", 17, 1), ("mh", 2012, 2), ("mh", 2046, 1),
        ("cr1", 2049, 1), ("ph", 2049, 1), ("bh", 2049, 1), ("bhw", 2046, 1), ("ly", 2046, 1), ("ly", 17, 1),
        ("ly", 2048, 1), ("uy", 2048, 1), ("p", 2012, 1), ("pc", 2012, 1), ("bhw", 2012, 1), ("ly", 2012, 1),
        ("uy", 2012, 1), ("bhw", 2019, 1)]
AMMO.append(("ph", 8, 1))                              # a backpack: the pump house
for name, kind, n in AMMO:
    items(name, kind, n)

# the baths: a few to learn on; cacodemons over the water when P first stands over 200
put("cr0", ZOMBIE, 2, angle=270)
put("cr0", ZOMBIE, 3, angle=270)                       # the swimming bath's: nothing may stand in it (the left-handed bath)
put("cr0", SERGEANT, 1, angle=270)
put("p", IMP, 3, angle=180)
put("p", SERGEANT, 2, angle=180)
put("cr1", IMP, 4, angle=0)
put("cr1", CHAINGUNNER, 2, angle=0)
put("cr1", SERGEANT, 2, angle=0)
wambush("p", True, TP, 200, CACO, 3, angle=180)
# the pump corridor and the pump house: the fight for GREEN
put("pc", SERGEANT, 2, angle=180)
put("pcn", SERGEANT, 1, angle=270)
put("pcn", IMP, 2, angle=270)
put("ph", IMP, 6, angle=180)
put("ph", DEMON, 3, angle=180)
put("ph", SPECTRE, 2, angle=180)
put("ph", CHAINGUNNER, 2, angle=180)
put("ph", REVENANT, 1, angle=180)
ambush("ph", 10 + GREEN, IMP, 4, angle=180, after=2)
ambush("ph", 10 + GREEN, KNIGHT, 2, angle=180, after=4)
# the cooling hall: revenants and imps on the walkway while it is full; the cells
put("cwalk", REVENANT, 2, angle=270)
put("cwalke", REVENANT, 1, angle=180)
put("cwalk", IMP, 4, angle=270)
put("cwalkw", IMP, 3, angle=0)
put("cella", DEMON, 3, angle=90)
put("cella", KNIGHT, 2, angle=90)
put("cellb", DEMON, 3, angle=90)
put("cellb", KNIGHT, 2, angle=90)
put("cellb", BARON, 1, angle=90)
wambush("cwalke", False, TC, C_FLOOR + 8, IMP, 2, angle=180, after=3)
wambush("cwalk", False, TC, C_FLOOR + 8, IMP, 2, angle=270, after=3)          # when C is first dry: the walkway's second lot
# the passage and the boiler house: chaingunners on the catwalk, company when the float trips
put("pass", ZOMBIE, 4, angle=0)
put("pass", SPECTRE, 2, angle=180)
put("catwalk", CHAINGUNNER, 2, angle=180)
put("bhw", CHAINGUNNER, 2, angle=0)
put("bh", IMP, 4, angle=90)
put("bh", KNIGHT, 2, angle=90)
put("bhw", REVENANT, 2, angle=0)
wambush("bh", True, TT, FLOAT_MARK, CACO, 3, angle=90, after=1)
wambush("bhw", True, TT, FLOAT_MARK, IMP, 4, angle=0, after=2)
# the lower yard: the big open fight
put("ly", MANCUBUS, 2, angle=270)
put("ly", ARACH, 2, angle=270)
put("ly", CACO, 3, angle=270)
put("ly", PAIN, 1, angle=270)
put("ly", IMP, 6, angle=270)
put("ly", SERGEANT, 4, angle=270)
put("ly", CHAINGUNNER, 2, angle=270)
put("ly", REVENANT, 2, angle=270)
# the lock: lost souls and cacodemons at the sill when K first stands over 150
wambush("uy", True, TK, 150, SOUL, 6, angle=270)
wambush("uy", True, TK, 150, CACO, 2, angle=270, after=2)
# the upper yard: an arch-vile and its court
put("uy", VILE, 1, angle=270)
put("uy", KNIGHT, 3, angle=270)
put("uy", REVENANT, 2, angle=270)
put("uy", IMP, 4, angle=270)
put("uy", CHAINGUNNER, 2, angle=270)
put("uy", MANCUBUS, 1, angle=270)
# the wheel house
put("l", IMP, 3, angle=90)
put("u", SERGEANT, 2, angle=270)
# behind the sluice: what it lets out when the wheel first turns
put("tunnel", DEMON, 2, angle=180)
put("mh", DEMON, 1, angle=180)
put("tunnel", IMP, 1, angle=180)
put("mh", IMP, 2, angle=180)
put("mh", KNIGHT, 2, angle=180)
put("mh", BARON, 1, angle=180)
put("mh", REVENANT, 2, angle=180)
put("mh", CHAINGUNNER, 2, angle=180)

# where the tests stand the player (map20.zs: MapSpot tids)
TEST_SPOTS = {}


def test_spot(tid, x, y, angle):
    TEST_SPOTS[tid] = (x, y, angle)
    m.thing(x, y, MAPSPOT, id=tid, angle=angle)


for n, fr in FRAMES.items():                            # 1000 + n: before frame n, facing it
    (x, y), o = fr["mouth"], fr["out"]
    test_spot(1000 + n, x - o[0] * 40, y - o[1] * 40, round(math.degrees(math.atan2(o[1], o[0]))) % 360)
VIEWS = {2001: (520, 480, 315), 2002: (2336, 736, 315), 2003: (2976, 200, 270), 2004: (3900, 640, 0),
         2005: (4200, 448, 90), 2006: (3648, 900, 0), 2007: (4032, 2280, 270), 2008: (4544, 2288, 270),
         2009: (4900, 1312, 0), 2010: (-200, 300, 180), 2011: (1088, 224, 0), 2012: (832, 640, 270),
         2013: (5300, 1312, 0), 2014: (4032, 2340, 270), 2015: (4000, 1820, 90), 2016: (2000, 400, 0),
         2017: (3300, -448, 0), 2018: (3296, 416, 0), 2019: (3560, 416, 180), 2020: (416, 64, 0),
         2021: (2944, 64, 270), 2022: (4064, 704, 0),
         # the look's (PLAN.md, "Look: MAP20"): the plaques P, C, K, L; the section drawing; the cells' demon;
         # the tunnel's seam; the exit door
         2023: (700, 64, 0), 2024: (3040, 680, 270), 2025: (4100, 2150, 270), 2026: (4832, 2040, 270),
         2027: (3950, 192, 0), 2028: (3320, -230, 270), 2029: (5280, 1280, 30), 2030: (5850, 1312, 0)}
for tid, (x, y, a) in VIEWS.items():
    test_spot(tid, x, y, a)


# =================================================================================================
# THE MEASURE: the lab's rule of flow written again (water.zs, AjarWaterHandler: Links, Spills,
# Apply), run to rest for every hanging the plan names; the four facts of "nothing can be lost"
# =================================================================================================
TIC = 35


class Flow:
    """The water of the level, as water.zs keeps it, one tic at a time."""

    def __init__(self, levels=None, k=K_FLOW, overflow=True):
        self.k, self.overflow = k, overflow
        self.w = {}
        for tag, b in BASINS.items():
            if b["kind"] == W.OUTFALL:
                self.w[tag] = b["floor"] - 32
            else:
                self.w[tag] = min(max(b["floor"] + b["depth"], b["floor"]), b["brim"])
        self.w.update(levels or {})
        self.links = []             # (basin a, sill a, basin b, sill b)
        self.turning = 0            # tics the spill has stayed over WHEEL_FLOW
        self.spill = 0

    def fixed(self, t):
        return BASINS[t]["kind"] != W.NORMAL

    def hang(self, door, n, twin=None):
        f = FRAMES[n]
        if door == TEAL:
            g = FRAMES[twin]
            self.links.append((f["basin"], f["sill"], g["basin"], g["sill"]))
        else:
            g = FARS[door]
            self.links.append((f["basin"], f["sill"], g["basin"], g["sill"]))
        return self

    def take(self, n):
        s = FRAMES[n]["sill"], FRAMES[n]["basin"]
        self.links = [l for l in self.links if (l[1], l[0]) != s and (l[3], l[2]) != s]
        return self

    def q(self, a, sa, b, sb):
        w = self.w
        sign = 1
        ha, hb = w[a] - sa, w[b] - sb
        if ha < hb:
            a, b, sa, sb, ha, hb, sign = b, a, sb, sa, hb, ha, -1
        if ha <= 0:
            return 0
        q = (self.k * FREE if hb <= 0 else self.k) * (ha - max(hb, 0))
        ia = 0 if self.fixed(a) else 1 / BASINS[a]["area"]
        ib = 0 if self.fixed(b) else 1 / BASINS[b]["area"]
        if ia + ib > 0:
            q = min(q, (ha - hb) / (ia + ib))
        if not self.fixed(a):
            q = min(q, ha * BASINS[a]["area"])
        if not self.fixed(b) and not self.overflow:
            q = min(q, (BASINS[b]["brim"] - w[b]) * BASINS[b]["area"])
        return max(q, 0) * sign

    def move(self, a, b, q):
        for t, d in ((a, -q), (b, q)):
            if not self.fixed(t):
                bb = BASINS[t]
                self.w[t] = min(max(self.w[t] + d / bb["area"], bb["floor"]), bb["brim"])

    def tic(self):
        qs = [(a, b, self.q(a, sa, b, sb)) for a, sa, b, sb in self.links]
        over = self.w[TU] - CREST
        s = self.k * over if over > 0 else 0          # K_WEIR is the level's K
        s = min(s, max(over, 0) * BASINS[TU]["area"])
        if not self.overflow:
            s = min(s, (BASINS[TL]["brim"] - self.w[TL]) * BASINS[TL]["area"])
        self.spill = max(s, 0)
        for a, b, q in qs:
            self.move(a, b, q)
        self.move(TU, TL, self.spill)
        self.turning = self.turning + 1 if self.spill > 2 * self.k else 0

    def run(self, watch, ok, seconds=120, hold=0):
        """Runs `seconds`; returns (where `watch` rests, seconds until within 1 of it, seconds until
        ok(level) first held `hold` seconds on end and for good (None: never), seconds the wheel
        first counted as turning (None: never))."""
        trace, wheel = [], None
        for t in range(seconds * TIC):
            self.tic()
            trace.append(self.w[watch])
            if wheel is None and self.turning >= WHEEL_TICS:
                wheel = (t + 1) / TIC
        rest = trace[-1]
        settle = 0
        for i in range(len(trace) - 1, -1, -1):
            if abs(trace[i] - rest) > 1:
                settle = (i + 1) / TIC
                break
        at = None
        if ok(rest):
            i = len(trace)
            while i > 0 and ok(trace[i - 1]):
                i -= 1
            at = i / TIC + hold
        return rest, settle, at, wheel


def _found():
    return Flow()


# Each named hanging: (what it is, what is hung, the basin to read, what it is for and the height
# that must be reached for it (the water no more than REACH under it), meant: True an answer meant
# (must reach), False a wrong one named (must not), None a step (reported only), a wait the level asks for?)
def _runs():
    runs = []
    def add(name, flow, watch, what, need, meant, wait, mark=None, hold=0):
        runs.append(dict(name=name, flow=flow, watch=watch, what=what, need=need, meant=meant, wait=wait, mark=mark,
                         hold=hold))
    add("BLUE in 101", Flow().hang(BLUE, 101), TP, "the ledge (its coaming 232)", COAMING, False, False)
    add("BLUE in 102", Flow().hang(BLUE, 102), TP, "the ledge (its coaming 232)", COAMING, True, True)
    add("GREEN in 111", Flow().hang(GREEN, 111), TC, "E2 opens (under 16 at its sill)", None, None, False)
    add("GREEN in 112", Flow().hang(GREEN, 112), TC, "E2 opens (under 16 at its sill)", None, False, True)
    add("GREEN in 113", Flow().hang(GREEN, 113), TC, "E2 opens (under 16 at its sill)", None, True, True)
    add("BLUE in 121", Flow({TC: C_FLOOR}).hang(BLUE, 121), TT, "the float mark 216, 2 s", None, False, False,
        FLOAT_MARK, FLOAT_SECONDS)
    add("TEAL 113-121, BLUE in 111", Flow().hang(TEAL, 113, 121).hang(TEAL, 121, 113).hang(BLUE, 111), TT,
        "the float mark 216, 2 s", None, True, True, FLOAT_MARK, FLOAT_SECONDS)
    add("TEAL 101-121 from P 224, BLUE in 102", Flow({TP: 224}).hang(TEAL, 101, 121).hang(TEAL, 121, 101).hang(BLUE, 102), TT,
        "the float mark 216, 2 s", None, True, True, FLOAT_MARK, FLOAT_SECONDS)
    add("TEAL 101-121 from P 224, no BLUE", Flow({TP: 224}).hang(TEAL, 101, 121).hang(TEAL, 121, 101), TT,
        "the float mark 216, 2 s", None, False, False, FLOAT_MARK, FLOAT_SECONDS)
    add("BLUE in 131 (alone)", Flow().hang(BLUE, 131), TK, "the sill 192", K_SILL, False, False)
    add("  ... the shelf", Flow().hang(BLUE, 131), TK, "frame 133 on the shelf 88", K_SHELF, True, False)
    add("then BLUE in 133", Flow({TK: 96}).hang(BLUE, 133), TK, "the sill 192", K_SILL, True, True)
    add("BLUE in 141", Flow().hang(BLUE, 141), TSB, "the panes (sills 0)", PANE_SILL, False, False)
    add("BLUE in 142", Flow().hang(BLUE, 142), TSB, "the panes (sills 0)", PANE_SILL, True, True)
    add("BLUE in 109", Flow().hang(BLUE, 109), TL, "L at its brim -4", L_BRIM, True, True)
    add("circle, L full: TEAL 107-108", Flow({TL: L_BRIM}).hang(TEAL, 107, 108).hang(TEAL, 108, 107), TU,
        "the wheel turning", None, True, True)
    add("circle, L dry: TEAL 107-108", Flow().hang(TEAL, 107, 108).hang(TEAL, 108, 107), TU,
        "the wheel turning", None, False, False)
    return runs


def _pair_once(flow):
    """A Pair links once (water.zs: from the leaf in the lower-numbered frame): the runs above
    hang both leaves, so keep one of the two links."""
    seen, keep = set(), []
    for l in flow.links:
        key = frozenset(((l[0], l[1]), (l[2], l[3])))
        if key not in seen:
            seen.add(key)
            keep.append(l)
    flow.links = keep
    return flow


def _maxlevels():
    """The highest each basin can ever stand: through any door, from the reservoir down."""
    top = {t: (b["floor"] + b["depth"] if b["kind"] != W.OUTFALL else b["floor"]) for t, b in BASINS.items()}
    sills = [(f["basin"], f["sill"]) for f in FRAMES.values()] + [(f["basin"], f["sill"]) for f in FARS.values()]
    for _ in range(50):
        for t, b in BASINS.items():
            if b["kind"] != W.NORMAL:
                continue
            best = top[t]
            for a, sa in sills:
                if a != t:
                    continue
                for c, sc in sills:
                    if c != t and top[c] > sc:
                        best = max(best, top[c] - sc + sa)
            if t == TL:
                best = max(best, L_FLOOR)
            top[t] = min(best, b["brim"])
    top[TL] = L_BRIM
    return top


# the ways out of each basin with empty hands, and the levels they are good for (lo, hi): the
# pressure door while it is under HOLD at its sill; a stair that goes on under water out over the
# brim (any level); a ledge or sill while the water is no more than REACH under it
EXITS = {
    TP: [("its pressure door", 0, HOLD), ("the stair to the landing and the gallery's door", 0, 999),
         ("over the coaming to the ledge", COAMING - REACH, 999)],
    TC: [("the stair up to the walkway", C_FLOOR, 999), ("E2", C_FLOOR, C_FLOOR + HOLD)],
    TT: [("the manhole", 0, HOLD), ("its stair up to the rim", 0, 999)],
    TK: [("its pressure door", 0, HOLD), ("the squeeze and the stair behind it", 0, 999),
         ("over the sill", K_SILL - REACH, 999)],
    TL: [("the stair up to the lower yard", L_FLOOR, 999)],
    TU: [("the stair up to the upper yard", U_FLOOR, 999)],
    TSB: [("the steps up to the poolside", -160, 999)],
}

# Where a door can be carried (places, by name; FRAMES[n]["place"]); squeezes are not ways for it.
# A pressure door is: the basin behind it can always be emptied through a frame at its floor (GREEN).
# ("water", basin, level): only while the basin stands at least so high (a swim with the door).
CARRY = [
    ("cr0", "p", None), ("p", "cr0", None), ("p", "p_gal", None), ("p_gal", "p", None),
    ("p_gal", "cr1", None), ("cr1", "p_gal", None),                     # the gallery's door: bolt drawn from the ledge on
    ("p", "ledge", (TP, COAMING - REACH)), ("ledge", "p", None),
    ("ledge", "pc", None), ("pc", "ledge", None), ("cr1", "pc", None), ("pc", "cr1", None),
    ("pc", "ph", None), ("ph", "pc", None), ("ph", "cwalk", None), ("cwalk", "ph", None),
    ("cwalk", "c", None), ("c", "cwalk", None),
    ("c", "pass", None), ("pass", "c", None), ("pass", "bh", None), ("bh", "pass", None),
    ("cwalk", "bh", None), ("bh", "cwalk", None),                       # the gangway, once its bolt is drawn
    ("bh", "t", None), ("t", "bh", None), ("cr0", "sb", None), ("sb", "cr0", None),
    ("bh", "ly", None), ("ly", "bh", None),                             # the yard gate, once raised
    ("ly", "k", None), ("k", "ly", None), ("k", "uy", (TK, K_SILL - REACH)), ("uy", "k", None),
    ("k", "shelf", (TK, K_SHELF - REACH)), ("shelf", "k", None),
    ("uy", "ly", None),                                                 # the terrace: a drop
    ("ly", "l", None), ("l", "ly", None), ("uy", "u", None), ("u", "uy", None),
]
LOWER = {"cr0", "p", "p_gal", "ledge", "cr1", "pc", "ph", "cwalk", "c", "pass", "bh", "t", "sb", "ly", "k", "l"}
UPPER = {"uy", "u", "shelf"}


def _reach(start, levels):
    seen, todo = {start}, [start]
    while todo:
        a = todo.pop()
        for x, y, need in CARRY:
            if x == a and y not in seen and (need is None or levels[need[0]] >= need[1]):
                seen.add(y)
                todo.append(y)
    return seen


REST = {}               # each named hanging's level at rest (the measure)
# the ones map20.zs compares its own with: MapSpot 3100 + n, args[0] the level at rest x 100
EXPECT = ["BLUE in 102", "GREEN in 112", "GREEN in 113", "TEAL 113-121, BLUE in 111", "BLUE in 131 (alone)",
          "then BLUE in 133", "BLUE in 109", "circle, L full: TEAL 107-108", "BLUE in 101", "BLUE in 121",
          "TEAL 101-121 from P 224, no BLUE", "BLUE in 142", "BLUE in 141"]


def measure():
    lines, problems = [], []
    lines.append(f"MAP20 measure: K {K_FLOW} (the lab's 2048), FREE {FREE}, overflow to the outfall; "
                 f"waits the level asks for {WAIT[0]}..{WAIT[1]} s")
    lines.append(f"  {'hanging':36} {'basin':5} {'rests at':>9} {'after':>8} {'reached':>7}  for (the time it is reached)")
    for r in _runs():
        f = _pair_once(r["flow"])
        what, need = r["what"], r["need"]
        if r["mark"] is not None:
            ok = lambda v: v >= r["mark"]
        elif what.startswith("E2"):
            ok = lambda v: v < C_FLOOR + HOLD
        elif need == L_BRIM:
            ok = lambda v: v >= L_BRIM - 0.5
        elif need is None:
            ok = lambda v: True
        else:
            ok = lambda v: v >= need - REACH
        rest, settle, at, wheel = f.run(r["watch"], ok, hold=r["hold"])
        REST[r["name"]] = rest
        if what.startswith("the wheel"):
            at = wheel
        ok, t = at is not None, at
        tt = f"{t:.1f} s" if t is not None else "-"
        lines.append(f"  {r['name']:36} {SHORT[r['watch']]:5} {rest:9.1f} {settle:6.1f} s {tt:>7}  {what}: "
                     f"{'yes' if ok else 'no'}{'' if r['meant'] is None else ' (meant)' if r['meant'] else ' (not meant)'}")
        if r["meant"] is True and not ok:
            problems.append(f"{r['name']}: {what} not reached")
        if r["meant"] is False and ok:
            problems.append(f"{r['name']}: {what} reached, which it must not be")
        if r["wait"] and ok and not (WAIT[0] <= t <= WAIT[1]):
            problems.append(f"{r['name']}: the wait is {t:.1f} s")
    # the four facts
    top = _maxlevels()
    lines.append("  the highest each basin can stand: " + ", ".join(f"{SHORT[t]} {top[t]:.0f}" for t in top
                                                                   if BASINS[t]["kind"] == W.NORMAL))
    deep = []
    for n, f in sorted(FRAMES.items()):
        d = top[f["basin"]] - f["sill"]
        deep.append(f"{n} {max(d, 0):.0f}")
        if d > DIVE:
            problems.append(f"frame {n}: a dive of {d:.0f} at its deepest")
    lines.append(f"  1. every frame by a dive of at most {DIVE} (the deepest, by frame): " + ", ".join(deep)
                 + f"; frame 133 on the shelf ({K_SHELF}) needs K at {K_SHELF - REACH} or over, which BLUE in 131"
                 " or 135 gives (the one frame that is not come to on foot when its basin is dry)")
    for t, ways in EXITS.items():
        lo, hi = BASINS[t]["floor"], top[t]
        cover = sorted((max(a, lo), b) for _, a, b in ways)
        x = lo
        for a, b in cover:
            if a > x + 1e-6:
                break
            x = max(x, b)
        if x < hi:
            problems.append(f"{NAMES[t]}: no way out with empty hands from {x} up to {hi}")
    lines.append("  2. every basin can be left with empty hands at any level it can have: "
                 + "; ".join(f"{SHORT[t]} {', '.join(n for n, _, _ in w)}" for t, w in EXITS.items()))
    places = sorted({f["place"] for f in FRAMES.values()})
    worst = {t: (top[t] if BASINS[t]["kind"] == W.NORMAL else 0) for t in BASINS}
    bad = []
    for a in places:
        got = _reach(a, worst)
        for b in places:
            if b in got:
                continue
            if a in LOWER and b in UPPER:
                continue                                    # up from the lower yard: the lock's
            bad.append(f"{a}->{b}")
    if bad:
        problems.append("a door cannot be carried " + ", ".join(bad))
    lines.append(f"  3. every door can be carried from any frame to any other ({len(places)} places), up from the "
                 "lower side to the upper only by the lock: " + ("yes" if not bad else "no"))
    lines.append("  4. the stage gates stay open once opened (the ledge door and the gallery's and gangway's bolts:"
                 " Door_Open; the yard gate: the float raises it for good): by construction; MODE=3 tries them")
    return lines, problems


def bath_checks():
    """What "The left-handed room lab" asks of a room with an opening, checked on the swimming bath (the
    level's own records in SB_BOX) and on the left-handed bath's source: (1) no mirror the opening can see:
    every mirror is a pane, in the glass's own plane; (2) nothing in the bath moves by itself: no thing in it
    but the invisible markers, no light effect, no line special but the bath's own (mirrors, the opening,
    frames, doors, the way out); (3) every wall and flat is the game's own (made by tools/gfx*.py, so that
    lefthand.flip_all can flip it: it stops the build on any other). The water's surface is the one
    exception, and it is not in the copy: it is the control sector's (ajarwater.basin), FWATER1 unflipped."""
    problems = []
    x1, y1, x2, y2 = SB_BOX
    inside = lambda p: x1 <= p[0] <= x2 and y1 <= p[1] <= y2
    mirrors = 0
    for key, props in list(m.lineprops.items()) + list(SB_SRC.lineprops.items()):
        a, b = tuple(key)
        if not (inside(a) and inside(b)):
            continue
        sp = props.get("special", 0)
        if sp == 182:
            mirrors += 1
            if not a[0] == b[0] == SB_GLASS:
                problems.append(f"the swimming bath: a mirror at {a}-{b}, which the opening can see")
        elif sp not in (0, 156, 130, 12, EXIT_SECRET):
            problems.append(f"the swimming bath: line special {sp} at {a}-{b} (only mirrors, the opening, frames, doors)")
    still = {MAPSPOT, W.BASIN_T, ajarmap.FRAME_T}
    for t in m.things:
        if inside((t["x"], t["y"])) and t["type"] not in still:
            problems.append(f"the swimming bath: thing {t['type']} at ({t['x']}, {t['y']}): nothing may stand in it")
    if SB_SRC.things:
        problems.append(f"the left-handed bath's source has {len(SB_SRC.things)} things")
    walls, flats = set(), set()
    _, _, sides, sectors, _ = SB_SRC.parts()
    for sd in sides:
        walls |= {sd[k] for k in ("texturetop", "texturemiddle", "texturebottom") if sd.get(k) not in (None, "-", "")}
    for d in sectors:
        flats |= {d["texturefloor"], d["textureceiling"]}
        if d.get("special", 0) not in (0, 1024) or d.get("lightfloor") or d.get("lightceiling"):
            problems.append(f"the swimming bath: a sector with a light effect or special: {d}")
    for name in sorted(walls | flats):
        if not name.startswith("AJ"):
            problems.append(f"the swimming bath: {name} is not the game's own and cannot be flipped")
    line = (f"  the swimming bath's opening (pane {SB_OPEN + 1}{', a mirror: AJAR_SBMIRROR' if SB_MIRROR else ''}): "
            f"{mirrors} mirror lines in it and its copy, all in the glass's plane x {SB_GLASS}; nothing stands in it; "
            f"its copy at {SB_COPY_BOX}, {len(sectors)} sectors, {len(walls)} wall textures and {len(flats)} flats, "
            f"all the game's own (the water's surface, FWATER1, is the control sector's and not flipped)")
    return line, problems


I1.m, CD.m = _theirs, _cd                    # MAP11's and MAP18's helpers draw on their own maps again
MEASURE, PROBLEMS = measure()


def _level(run):
    """A level the water can be made to stand at, as the measure has it (the plaques mark these)."""
    v = REST[run]
    if abs(v - round(v)) > 0.05:
        PROBLEMS.append(f"the look: {run} rests at {v:.2f}, not a whole height for a plaque")
    return round(v)


def finish_look():
    """The pictures' heights from their walls, the plaques' levels from the measure, the section drawing's
    basins and frames from the generator's own records; then the walls are laid once (the hook's checks)."""
    for p in PICS.values():
        base = WALLS[p["base"]]
        p["H"] = base["H"] if p["H"] is None else p["H"]
        p["z0"] = base["z0"] if p["z0"] is None else p["z0"]
        p["basespec"] = base
        if p["kind"] == "plaque":
            p["at"] = _level(p["level"])
        if p["kind"] == "flood":
            p["ats"] = tuple(_level(r) for r in p["levels"])
        if p["kind"] == "section":
            p["basins"] = [(SHORT[t], BASINS[t]["floor"], BASINS[t]["brim"],
                            sorted((n, f["sill"]) for n, f in FRAMES.items() if f["basin"] == t))
                           for t in (TP, TC, TT, TK, TL, TU)]
            p["reservoir"] = BASINS[TR]["floor"] + BASINS[TR]["depth"]
    del LOOK_PROBLEMS[:]
    m.parts()
    PROBLEMS.extend("the look: " + s for s in LOOK_PROBLEMS)


if LOOK:
    finish_look()
_line, _problems = bath_checks()
MEASURE.append(_line)
PROBLEMS += _problems
for _n, _name in enumerate(EXPECT):
    m.thing(32 + 32 * _n, 352, MAPSPOT, id=3101 + _n, args=(round(REST[_name] * 100),))
if NOROOM:
    PROBLEMS.append("no room for things in " + ", ".join(sorted(set(NOROOM))))
# the night room's ground (NIGHT_BOX) is its own: nothing else of the level reaches into it
for _i, _p in enumerate(m.polys):
    if _i not in NIGHT_SECTORS and min(q[0] for q in _p) < NIGHT_BOX[2] and max(q[0] for q in _p) > NIGHT_BOX[0] \
            and min(q[1] for q in _p) < NIGHT_BOX[3] and max(q[1] for q in _p) > NIGHT_BOX[1]:
        PROBLEMS.append(f"sector {_i} reaches into the night room's ground {NIGHT_BOX}")
if PROBLEMS:
    raise SystemExit("MAP20: " + "; ".join(PROBLEMS) + "\n" + "\n".join(MEASURE))

if __name__ == "__main__":
    import sys
    if "-m" in sys.argv:
        print("\n".join(MEASURE))
    else:
        sys.stdout.write(m.textmap())
