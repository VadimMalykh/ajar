"""Water for Ajar maps (PLAN.md, "The water lab"; src/zscript/water.zs).

Water stands level on both sides of a hung door, measured from the door's
sill. A room that can hold water is a *basin*: every sector of it carries
the basin's tag (give the frames and far sides in it `tag=` too, so that
the water runs into their recesses), and basin() puts the thing that names
it and the hidden sector whose ceiling is its water surface. The surface is
a swimmable 3D floor (Sector_Set3DFloor type 2: translucent, drawn from
above and below, its sides where it meets a sector without it), moved each
tic by the script.

    basin(m, tag, area, brim, kind=NORMAL, depth=0)
        tag     the sector tag of the basin's sectors
        area    its plan area in square units (the script takes it as the
                same at every height)
        brim    the highest its water stands (absolute)
        kind    NORMAL, RESERVOIR (always full: its surface `depth` over its
                floor, which is the sill of the far side in it), OUTFALL
                (always empty) or FOLLOW (its surface is kept at that of the
                basin tagged `depth`, every tic: MAP20's left-handed bath; it
                has no links of its own and its area and brim are not used)
        depth   NORMAL: the water it starts with, over its floor
    weir(m, x, y, upper, lower, crest, chute, lamp, shutter)
        a fixed overflow from basin `upper` into basin `lower` over a crest
        at height `crest`, with a paddle wheel at x, y (in the spillway).
        `chute` is the tag of the spillway's sectors (they look wet and
        scroll while water goes down them: give them no basin tag), `lamp`
        the tag of a sector that is lit while the wheel turns, `shutter` the
        tag of a door sector it holds open while it turns. Its fountain, if
        it has one: the sectors tagged FOUNTAIN + `chute` are dry at rest and
        show water, with a jet in their middle, while the wheel turns. In a
        level (with rate()) the wheel is drawn as large as the chute lets
        it be, up to 160 across, and every NORMAL basin that no FOLLOW
        basin follows gets a buoy at its thing's spot (water.zs).
    gauge(m, a, b)
        the painted staff gauge (AJGAUGE: depth marks every 32, from the
        floor) on the 64-long wall piece a-b
    raft(m, x, y)
        a raft: it floats on the surface, is carried towards the door the
        most water leaves by, and can be stood on
    bulkhead(m, a, b, out, floor, tag)
        an ordinary door (Door_Raise) a-b, `out` into the basin with `tag`:
        from the dry side it will not open while the basin holds water

For a level (MAP20, tools/map_highwater.py):
    rate(m, x, y, k, free, flags, wheel)
        the level's own rate of flow (K, and how many times that water falls
        out onto a dry sill) and its rules: FLOAT (the player floats up when
        idle under water), OVERFLOW (a basin at its brim spills what comes
        in to the outfall, so no flow is held back by a full basin). A map
        without it keeps the lab's (K 2048, 8, no flags).
    pressure_door(m, a, b, out, sill, tag, sides, lamp)
        a door that water holds: it opens by USE only while the water at its
        sill is under HOLD on both sides, says so when it refuses, and shuts
        itself (never on anyone) when the water comes to HOLD. A lamp over
        it on each side, red while water holds it. `auto`: it opens by itself
        the first time the basin sides[0] is dry (a cell in a tank's floor).
    float_gate(m, x, y, basin, mark, gate)
        a float in `basin`: once the water has stood at `mark` or over for
        2 s it raises the gate (sector tag `gate`) for good
    water_ambush(m, over, tag, height, kind, *spots, ...)
        ajarmap.ambush's monsters, brought by water: they come when basin
        `tag` first stands at or over (`over`) or at or under `height`
"""
BASIN_T, WEIR_T, RAFT_T = 20140, 20141, 20142      # AjarBasin, AjarWeir, AjarRaft (src/zscript/water.zs)
NORMAL, RESERVOIR, OUTFALL, FOLLOW = 0, 1, 2, 3
CTL = 6000                              # the control sector of basin tag t has the tag CTL + t
BULKHEAD = 9000                         # the dry side of a bulkhead into basin tag t: line id BULKHEAD + t
FOUNTAIN = 7000                         # a weir's fountain: the sectors tagged FOUNTAIN + its chute's tag
SURFACE, SIDE = "FWATER1", "FWATER1"     # the water's top (Doom II's own, animated) and its sides (a flat, on a wall)
ALPHA = 144                             # how opaque the water is (of 255)
UNDER_LIGHT, UNDER_COLOR = 150, 0x70B8D8    # the light under the surface, and its tint
DRY = 32                                # a dry basin's surface stands this far under its floor
VOID = (-6000, -6000)                   # where the hidden control sectors go, 64 apart along x


def basin(m, tag, area, brim, *, floor, kind=NORMAL, depth=0, at=None):
    """`floor` is the basin's lowest floor; `at` is any spot in it (for the
    thing; it only names the basin)."""
    n = getattr(m, "_basins", 0)
    m._basins = n + 1
    x, y = VOID[0] + 128 * n, VOID[1]
    level = {NORMAL: floor + depth if depth else floor - DRY, RESERVOIR: floor + depth, OUTFALL: floor - DRY,
             FOLLOW: floor - DRY}[kind]
    # The control sector, and beside it a second one, so that the line with
    # the special is two-sided: its front side then has an upper texture
    # (a 3D floor whose line has none is drawn with alpha 0).
    m.sector([(x, y), (x, y + 32), (x + 32, y + 32), (x + 32, y)], floor=floor - 2 * DRY, ceil=level,
             light=UNDER_LIGHT, wall=SIDE, ftex=SURFACE, ctex=SURFACE, id=CTL + tag,
             raw=dict(lightcolor=UNDER_COLOR))
    m.sector([(x + 32, y), (x + 32, y + 32), (x + 64, y + 32), (x + 64, y)], floor=floor - 2 * DRY,
             ceil=floor + 512, light=UNDER_LIGHT, wall=SIDE, ftex=SURFACE, ctex=SURFACE)
    # Sector_Set3DFloor(tag, type 2 swimmable, no flags, alpha); the middle texture is the water's side
    m.line((x + 32, y), (x + 32, y + 32), special=160, args=(tag, 2, 0, ALPHA), mid=SIDE)
    if at:
        m.thing(at[0], at[1], BASIN_T, args=(tag, area, brim, kind, depth))


def weir(m, x, y, upper, lower, crest, chute, lamp, shutter):
    m.thing(x, y, WEIR_T, args=(upper, lower, crest, chute, lamp * 65536 + shutter))


def raft(m, x, y):
    m.thing(x, y, RAFT_T)


def gauge(m, a, b):
    m.cut(a, b)
    m.line(a, b, mid="AJGAUGE", dontpegbottom=True, exact=True)


RATE_T, PDOOR_T, FLOAT_T = 20143, 20144, 20145      # AjarWaterRate, AjarPressureDoor, AjarFloatGate (water.zs)
FLOAT, OVERFLOW = 1, 2                  # rate() flags
HOLD = 16                               # a pressure door is held by this much water at its sill, on either side
LAMP_TEX = "TLITE6_6"                   # a pressure door's lamp (Doom II's own flat)
AMBUSH_OVER, AMBUSH_UNDER = 60, 61      # AjarAmbush causes (ajar.zs): a basin first at or over / at or under a height


def rate(m, x, y, k, free, flags, wheel=0):
    """`wheel`: tics the spill must stay over 2 units' flow for a wheel to count as turning (0: the lab's)."""
    m.thing(x, y, RATE_T, args=(k, free, flags, wheel))


def pressure_door(m, a, b, out, sill, tag, sides, lamp, *, thick=32, auto=False, look=None, strip=None):
    """a-b is its 64-wide mouth on one side, `out` the way through; `tag` the
    door's sector tag, `sides` the basin tags on the two sides (0: dry
    ground), `lamp` the tag of its two lamp strips. Declare the rooms on
    both sides first. `look`: the leaf's sector textures (wall: its face);
    `strip`: the lamp strips' wall and floor (the wall over the mouth)."""
    look = look or dict(wall="BIGDOOR2", ftex="FLAT20", ctex="FLAT20")
    strip = strip or dict(wall="AJTRIM", ftex="AJTRIMF")
    lt = (thick - 16) // 2
    p = lambda q, d: (q[0] + out[0] * d, q[1] + out[1] * d)
    a1, b1, a2, b2, a3, b3 = p(a, lt), p(b, lt), p(a, lt + 16), p(b, lt + 16), p(a, thick), p(b, thick)
    # Each lamp strip on a basin's side carries that basin's tag too (moreids), so that the water's 3D floor
    # is in it as in the rest of the basin: without it the surface stopped short of the door (a notch).
    for side, (s0, s1, t0, t1) in zip(sides, ((a, b, a1, b1), (a2, b2, a3, b3))):
        m.sector([s0, s1, t1, t0], floor=sill, ceil=sill + 96, light=160, wall=strip["wall"], ftex=strip["ftex"],
                 ctex=LAMP_TEX, id=lamp, raw=dict(moreids=str(side)) if side else None)
    m.sector([a1, b1, b2, a2], floor=sill, ceil=sill, light=160, id=tag, **look)
    for s, t in ((a1, b1), (a2, b2)):
        m.line(s, t, special=11, args=(0, 16), playeruse=True, repeatspecial=True)
    for s, t in ((a, a3), (b, b3)):
        m.line(s, t, mid="DOORTRAK", dontpegbottom=True)
    c = ((a1[0] + b2[0]) / 2, (a1[1] + b2[1]) / 2)
    m.thing(c[0], c[1], PDOOR_T, args=(tag, sides[0], sides[1], lamp, 1 if auto else 0))


def float_gate(m, x, y, basin_tag, mark, gate, seconds=2):
    m.thing(x, y, FLOAT_T, args=(basin_tag, mark, gate, seconds))


def water_ambush(m, over, tag, height, kind, *spots, angle=0, after=0, near=0):
    """As ajarmap.ambush (thinned the same way, counted with it), but brought
    by water: basin `tag` first at or over (`over`) or at or under `height`."""
    import ajarmap
    for x, y in spots:
        i = m.ambushers = getattr(m, "ambushers", -1) + 1
        m.thing(x, y, ajarmap.AMBUSH_T, angle=angle,
                args=(AMBUSH_OVER if over else AMBUSH_UNDER, kind, after, near, tag * 1024 + height + 512),
                skill=1 if i % 2 == 0 else 3 if i % 4 == 3 else 2)


def bulkhead(m, a, b, out, floor, tag, *, thick=16):
    """a-b is the door's face on the dry side, `out` the way into the basin.
    Declare the rooms on both sides first."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor, ceil=floor, light=160, wall="BIGDOOR2", ftex="FLAT20", ctex="FLAT20")
    m.line(a, b, special=12, args=(0, 32, 105), playeruse=True, repeatspecial=True, id=BULKHEAD + tag)
    m.line(c, d, special=12, args=(0, 32, 105), playeruse=True, repeatspecial=True)
    for p, q in ((a, c), (b, d)):
        m.line(p, q, mid="DOORTRAK", dontpegbottom=True)
