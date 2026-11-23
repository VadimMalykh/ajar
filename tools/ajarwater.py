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
                floor, which is the sill of the far side in it) or OUTFALL
                (always empty)
        depth   NORMAL: the water it starts with, over its floor
    weir(m, x, y, upper, lower, crest, chute, lamp, shutter)
        a fixed overflow from basin `upper` into basin `lower` over a crest
        at height `crest`, with a paddle wheel at x, y (in the spillway).
        `chute` is the tag of the spillway's sectors (they look wet and
        scroll while water goes down them: give them no basin tag), `lamp`
        the tag of a sector that is lit while the wheel turns, `shutter` the
        tag of a door sector it holds open while it turns.
    gauge(m, a, b)
        the painted staff gauge (AJGAUGE: depth marks every 32, from the
        floor) on the 64-long wall piece a-b
    raft(m, x, y)
        a raft: it floats on the surface, is carried towards the door the
        most water leaves by, and can be stood on
    bulkhead(m, a, b, out, floor, tag)
        an ordinary door (Door_Raise) a-b, `out` into the basin with `tag`:
        from the dry side it will not open while the basin holds water
"""
BASIN_T, WEIR_T, RAFT_T = 20140, 20141, 20142      # AjarBasin, AjarWeir, AjarRaft (src/zscript/water.zs)
NORMAL, RESERVOIR, OUTFALL = 0, 1, 2
CTL = 6000                              # the control sector of basin tag t has the tag CTL + t
BULKHEAD = 9000                         # the dry side of a bulkhead into basin tag t: line id BULKHEAD + t
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
    level = {NORMAL: floor + depth if depth else floor - DRY, RESERVOIR: floor + depth, OUTFALL: floor - DRY}[kind]
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
