"""Map helpers for stepping out of a fight (src/zscript/time.zs has the contract)."""
import ajarmap

ZONE_T = 20040
CUE_T = 20041
TIME = 10           # the time door's colour number: textures AJDR10, AJTR10, AJTF10


REEL_TAG = 3070     # the big screen's sector, and the tid of the seat before it


def hall_line(k, j):
    return 3000 + 100 * k + j


def box_line(k, n):
    return 3050 + 100 * k + n


def zone(m, k, n, x1, y1, x2, y2, *, grow=0, open=False, goes=False, mix=False):
    """Part of fight k: of its hall and the way into it (n 0), or of its box n.
    `grow` widens it, to take in recesses and the stubs behind doors. `open`
    (on a hall's zone): the fight is an open one (time.zs). `goes` (on a
    hall's zone): it is a room of goes (plate.zs), with one box, number 1.
    `mix` (on a hall's zone): an open fight that becomes a room of goes when
    it is won (goes.zs)."""
    m.thing((x1 + x2) / 2, (y1 + y2) / 2, ZONE_T,
            args=(k, n, (x2 - x1) // 2 + grow, (y2 - y1) // 2 + grow, 3 if mix else 2 if goes else int(open)))


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


def show_tag(k):
    """The tag of hall k's sectors, and the id of its screen's line: with
    them the hall has a show (time.zs)."""
    return 3080 + 100 * k


def cue(m, k, wave, when, kind, *spots, angle=0, always=False):
    """Monsters of Doom editor number `kind` that come into fight k at
    `spots`, as wave number `wave`, once no more than `when` are left. A
    hall with a show starts empty: its first monsters are wave 1, when 0.
    `always`: on every difficulty (what a fight is remembered by)."""
    for x, y in spots:
        i = m.cues = getattr(m, "cues", -1) + 1         # thinned on the easier difficulties, as ajarmap.ambush
        m.thing(x, y, CUE_T, angle=angle, args=(k, wave, when, kind),
                skill=1 if always or i % 2 == 0 else 3 if i % 4 == 3 else 2)


LOCKER_T = 20042


def locker(m, x, y, key, *what, angle=0):
    """A cupboard that room key `key` opens, facing `angle`; `what` is the
    Doom editor numbers of one or two things in it."""
    m.thing(x, y, LOCKER_T, angle=angle, args=(key,) + tuple(what))


WIND_T = 20043


def wind(m, x, y, angle, on, z=30):
    """A plate on a wall, facing `angle`, `z` above the floor: USE winds the
    fight half a minute back, or (`on`) on: an open fight that is being
    played (from its boxes, and its hall), or a fight that is being watched
    from the box the plate is in (time.zs, AjarTimeHandler.Wind)."""
    m.thing(x, y, WIND_T, angle=angle, height=float(z), args=(int(on),))


PLATE_T = 20044
ANEW_T = 20045


def plate(m, x, y, frame):
    """A plate on the floor at x, y that springs the frame `frame` (its line
    id): a door hung there is open only while the player or an earlier self
    stands on the plate (plate.zs, AjarPlate). Put it far enough from the
    frame's mouth (256 or more) that it cannot be stepped off and the door run."""
    m.thing(x, y, PLATE_T, args=(frame,))


PRESS_T = 20046
PRESS_SWITCH_T = 20047
TOGETHER_T = 20048


def press(m, x, y, tag):
    """A press over every sector with `tag` (give them a wall and ceiling of
    steel: what a ceiling that comes down shows). x, y anywhere in the area:
    its sounds are heard from there (goes.zs, AjarPress)."""
    m.thing(x, y, PRESS_T, args=(tag,))


def press_switch(m, x, y, angle, tag, z=40):
    """A switch on a wall, facing `angle`, `z` above the floor: USE sets off
    the press of `tag` (goes.zs, AjarPressSwitch). Stand it 2 off the wall."""
    m.thing(x, y, PRESS_SWITCH_T, angle=angle, height=float(z), args=(tag,))


def together(m, x, y, angle, frame, z=72):
    """A lamp on the wall beside frame `frame` (its line id), facing `angle`:
    a Pair joins through it only if both leaves were hung within two seconds
    of each other (goes.zs, AjarTogether)."""
    m.thing(x, y, TOGETHER_T, angle=angle, height=float(z), args=(frame,))


def anew(m, x, y, angle, z=30):
    """A plate on a wall of a room of goes' box, facing `angle`: USE forgets
    every go (plate.zs, AjarAnew)."""
    m.thing(x, y, ANEW_T, angle=angle, height=float(z))
