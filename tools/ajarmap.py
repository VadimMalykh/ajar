"""Shared pieces for Ajar maps: door colours, frame/far-side recesses, door things.

Line ids: 1xx = frames, 200 + colour = that door's far side; a fixed
doorway number n uses 150 + n and 250 + n.
"""
FRAME_T, DOOR_T = 20001, 20002
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
