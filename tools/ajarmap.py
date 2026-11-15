"""Shared pieces for Ajar maps: door colours, frame/far-side recesses, door things.

Line ids: 1xx = frames, 200 + colour = that door's far side; a fixed
doorway number n uses 150 + n and 250 + n.
"""
FRAME_T, DOOR_T = 20001, 20002
KEY_T = {"1": 20011, "2": 20012, "3": 20013, "4": 20014}      # room keys, by number
LOCK = {"1": 41, "2": 42, "3": 43, "4": 44, "12": 45, "23": 46, "34": 47}   # src/lockdefs.txt
RED, BLUE, GREEN, YELLOW, VIOLET = 1, 2, 3, 4, 5
NAMES = {RED: "RED", BLUE: "BLUE", GREEN: "GREEN", YELLOW: "YELLOW", VIOLET: "VIOLET"}
DEPTH = 16          # recess depth
DOOR_H = 96
STUB = 32           # space behind each portal line (engine requirement)


def far_id(colour):
    return 200 + colour


def recess(m, m1, m2, out, floor, line_id, target, *, far_colour=None, color=None, arch=None):
    """A 64-wide door recess whose mouth is m1-m2 and which goes `out` of the room.

    Frames (far_colour None) get an AjarFrame thing and a usable mouth line.
    Far sides show the closed door of their colour until that door is hung.
    `target` is any valid portal line id; the script empties every portal at load.
    `arch` ("frame" or "far") makes it one end of a fixed doorway instead: see doorway().
    """
    b1 = (m1[0] + out[0] * DEPTH, m1[1] + out[1] * DEPTH)
    b2 = (m2[0] + out[0] * DEPTH, m2[1] + out[1] * DEPTH)
    if arch:
        wall, flat, mid = "AJARCH", "AJARCHF", "AJFRAME"
    elif far_colour:
        wall, flat, mid = f"AJTR{far_colour}", f"AJTF{far_colour}", f"AJDR{far_colour}"
    else:
        wall, flat, mid = "AJTRIM", "AJTRIMF", "AJFRAME"
    m.sector([m1, m2, b2, b1], floor=floor, ceil=floor + DOOR_H, light=176,
             wall=wall, ftex=flat, ctex=flat, color=color)
    # GZDoom only lets things walk through a portal line that has real space
    # behind it, so every portal line gets a small dark stub sector at its back.
    m.sector([b1, b2, (b2[0] + out[0] * STUB, b2[1] + out[1] * STUB),
              (b1[0] + out[0] * STUB, b1[1] + out[1] * STUB)],
             floor=floor, ceil=floor + DOOR_H, light=96, wall=wall, ftex=flat, ctex=flat)
    # Line_SetPortal: target id, this line, type 1 (teleporter), align to floor
    m.line(b1, b2, id=line_id, special=156, args=(target, 0, 1, 1), mid=mid)
    if arch == "frame" or not (arch or far_colour):
        m.line(m1, m2, special=130, args=(line_id,), playeruse=True, repeatspecial=True)
        m.thing((b1[0] + b2[0]) / 2 - out[0] * 8, (b1[1] + b2[1]) / 2 - out[1] * 8,
                FRAME_T, id=line_id, height=0, args=(line_id,))


def door(m, colour, x, y, *, angle=0, frame=0):
    """A door thing. With `frame` it starts hung there (x, y only pick the sector);
    otherwise it leans at x, y facing `angle`."""
    m.thing(x, y, DOOR_T, angle=angle, args=(far_id(colour), colour, frame))


def doorway(m, n, a1, a2, a_out, a_floor, b1, b2, b_out, b_floor, *, a_color=None, b_color=None):
    """Fixed doorway number n: a plain stone opening that joins two places for
    the whole level. Nobody can take it, and it has no colour: it is part of
    the building. In a PUZZLE graph it is two walk links, one each way.

    Underneath it is a door without a leaf, fixed in its frame (door thing
    args[3]), so monsters, shots and lodgers treat it like any hung door."""
    recess(m, a1, a2, a_out, a_floor, 150 + n, 250 + n, color=a_color, arch="frame")
    recess(m, b1, b2, b_out, b_floor, 250 + n, 150 + n, color=b_color, arch="far")
    m.thing((a1[0] + a2[0]) / 2 - a_out[0] * 24, (a1[1] + a2[1]) / 2 - a_out[1] * 24, DOOR_T,
            args=(250 + n, 0, 150 + n, 1))


def roomdoor(m, a, b, out, floor, *, thick=16, keys="", line_id=0):
    """An ordinary door, as in any Doom level: opened with USE, shuts by
    itself, and monsters can open it too. It fills the wall between two
    rooms that are `thick` apart; a-b is its 64-wide mouth on one side and
    `out` points to the other. It is plain wood and nobody can carry it.
    Declare both rooms first, so that the door is at the back of its lines.
    The rooms should be no more than 128 high where it stands (see gfx.py).

    With `keys` ("1", "23"...) it is locked and needs every one of those
    room keys (see key()); its lock plates show their numbers, and monsters
    cannot open it. In a PUZZLE graph that is a walk link with keys.
    `line_id` names the mouth line a-b, for tests."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor, ceil=floor, light=160, wall=f"AJHK{keys}" if keys else "AJHDOR",
             ftex="AJTRIMF", ctex="AJTRIMF")
    for p, q in ((a, b), (c, d)):
        if keys:
            m.line(p, q, special=13, args=(0, 24, 150, LOCK[keys]), playeruse=True, repeatspecial=True)
        else:
            m.line(p, q, special=12, args=(0, 24, 150), playeruse=True, monsteruse=True,
                   repeatspecial=True)
    if line_id:
        m.line(a, b, id=line_id)
    for p, q in ((a, c), (b, d)):
        m.line(p, q, mid="AJTRIM", dontpegbottom=True)


def key(m, number, x, y):
    """A numbered room key lying at x, y."""
    m.thing(x, y, KEY_T[str(number)])


def room(m, xs, ys, runner, *, ceil, light, **base):
    """A flat rectangular room cut into a grid by the lists xs and ys. Cells
    for which runner(i, j) is true (column i, row j) are a strip of carpet
    under a raised row of ceiling lights; use it to lead from door to door."""
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cell = [(xs[i], ys[j]), (xs[i], ys[j + 1]), (xs[i + 1], ys[j + 1]), (xs[i + 1], ys[j])]
            if runner(i, j):
                m.sector(cell, ceil=ceil + 16, light=min(255, light + 30),
                         **dict(base, ftex="AJRUG", ctex="AJLITE"))
            else:
                m.sector(cell, ceil=ceil, light=light, **base)


def picture(m, a, b, colour, height):
    """Hangs a framed picture of a door on the 64-long wall piece a-b.
    `height` is the wall's height there (336 or 176: see gfx.py)."""
    m.cut(a, b)
    m.line(a, b, mid=f"AJP{'A' if height == 336 else 'B'}{colour}", exact=True)
