"""Map helpers for stepping out of a fight (src/zscript/time.zs has the contract)."""
import ajarmap

ZONE_T = 20040
CUE_T = 20041
TIME = 10           # the time door's colour number: textures AJDR10, AJTR10, AJTF10


def hall_line(k, j):
    return 3000 + 100 * k + j


def box_line(k, n):
    return 3050 + 100 * k + n


def zone(m, k, n, x1, y1, x2, y2, *, grow=0):
    """Part of fight k: of its hall and the way into it (n 0), or of its box n.
    `grow` widens it, to take in recesses and the stubs behind doors."""
    m.thing((x1 + x2) / 2, (y1 + y2) / 2, ZONE_T,
            args=(k, n, (x2 - x1) // 2 + grow, (y2 - y1) // 2 + grow))


def hall_door(m, k, j, a, b, out, floor, **look):
    """Time door j of hall k: a-b is its 64-wide mouth."""
    ajarmap.recess(m, a, b, out, floor, hall_line(k, j), box_line(k, 1), far_colour=TIME, **look)


def box_door(m, k, n, a, b, out, floor, **look):
    """The door of box n of fight k."""
    ajarmap.recess(m, a, b, out, floor, box_line(k, n), hall_line(k, 1), far_colour=TIME, **look)


def glass(m, a, b, out, floor, *, sill=8, top=120, thick=16, color=None, trim=("AJTRIM", "AJTRIMF")):
    """A box's window: a-b is its edge on the hall's wall, `out` points from
    the hall into the box, whose floor is `floor`. Nothing passes it: no
    walker, no shot, no monster's sight. `trim` is (texture, flat) for its
    sill, head and sides."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor + sill, ceil=floor + top, light=200, wall=trim[0],
             ftex=trim[1], ctex=trim[1], color=color)
    m.line(a, b, blocking=True, blockeverything=True, blocksight=True, blocksound=True)
    m.line(c, d, blocking=True, blocksound=True)


def cue(m, k, wave, when, kind, *spots, angle=0):
    """Monsters of Doom editor number `kind` that come into fight k at
    `spots`, as wave number `wave`, once no more than `when` are left."""
    for x, y in spots:
        i = m.cues = getattr(m, "cues", -1) + 1         # thinned on the easier difficulties, as ajarmap.ambush
        m.thing(x, y, CUE_T, angle=angle, args=(k, wave, when, kind), skill=1 if i % 2 == 0 else 3 if i % 4 == 3 else 2)


LOCKER_T = 20042


def locker(m, x, y, key, *what, angle=0):
    """A cupboard that room key `key` opens, facing `angle`; `what` is the
    Doom editor numbers of one or two things in it."""
    m.thing(x, y, LOCKER_T, angle=angle, args=(key,) + tuple(what))
