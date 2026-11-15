"""Shared pieces for Ajar maps: door colours, frame/far-side recesses, door things.

Line ids: 1xx = frames, 200 + colour = that door's far side; a fixed
doorway number n uses 150 + n and 250 + n.
"""
FRAME_T, DOOR_T = 20001, 20002
KEY_T = {"1": 20011, "2": 20012, "3": 20013, "4": 20014}      # room keys, by number
LOCK = {"1": 41, "2": 42, "3": 43, "4": 44, "12": 45, "23": 46, "34": 47}   # src/lockdefs.txt
RED, BLUE, GREEN, YELLOW, VIOLET, PINK = 1, 2, 3, 4, 5, 6
NAMES = {RED: "RED", BLUE: "BLUE", GREEN: "GREEN", YELLOW: "YELLOW", VIOLET: "VIOLET", PINK: "PINK"}
DEPTH = 16          # recess depth
DOOR_H = 96
# Space behind each portal line (engine requirement). A thing crosses when its
# centre does, and its whole box must then still fit in front of the stub's
# back wall: the stub has to be deeper than the thing's radius plus one step
# of its walk. 32 let zombies through but not a demon (radius 30, step 10).
STUB = 48


def far_id(colour):
    return 200 + colour


def recess(m, m1, m2, out, floor, line_id, target, *, far_colour=None, color=None, arch=None, trim=None):
    """A 64-wide door recess whose mouth is m1-m2 and which goes `out` of the room.

    Frames (far_colour None) get an AjarFrame thing and a usable mouth line.
    Far sides show the closed door of their colour until that door is hung.
    `target` is any valid portal line id; the script empties every portal at load.
    `arch` ("frame" or "far") makes it one end of a fixed doorway instead: see doorway().
    `trim` is (texture, flat) for a doorway's surround instead of pale stone.
    """
    b1 = (m1[0] + out[0] * DEPTH, m1[1] + out[1] * DEPTH)
    b2 = (m2[0] + out[0] * DEPTH, m2[1] + out[1] * DEPTH)
    if arch:
        wall, flat, mid = (trim or ("AJARCH", "AJARCHF")) + ("AJFRAME",)
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


def doorway(m, n, a1, a2, a_out, a_floor, b1, b2, b_out, b_floor, *, a_color=None, b_color=None, trim=None):
    """Fixed doorway number n: a plain stone opening that joins two places for
    the whole level. Nobody can take it, and it has no colour: it is part of
    the building. In a PUZZLE graph it is two walk links, one each way.

    Underneath it is a door without a leaf, fixed in its frame (door thing
    args[3]), so monsters, shots and lodgers treat it like any hung door."""
    recess(m, a1, a2, a_out, a_floor, 150 + n, 250 + n, color=a_color, arch="frame", trim=trim)
    recess(m, b1, b2, b_out, b_floor, 250 + n, 150 + n, color=b_color, arch="far", trim=trim)
    m.thing((a1[0] + a2[0]) / 2 - a_out[0] * 24, (a1[1] + a2[1]) / 2 - a_out[1] * 24, DOOR_T,
            args=(250 + n, 0, 150 + n, 1))


def roomdoor(m, a, b, out, floor, *, thick=16, keys="", line_id=0):
    """An ordinary door, as in any Doom level: opened with USE, shuts by
    itself, and monsters can open it too. It fills the wall between two
    rooms that are `thick` apart; a-b is its 64-wide mouth on one side and
    `out` points to the other. It is plain wood and nobody can carry it.
    Declare both rooms first, so that the door is at the back of its lines.
    The rooms should be no more than 256 high where it stands (see gfx.py).

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


def room(m, xs, ys, runner, *, ceil, light, rug="AJRUG", **base):
    """A flat rectangular room cut into a grid by the lists xs and ys. Cells
    for which runner(i, j) is true (column i, row j) are a strip of carpet
    under a raised row of ceiling lights; use it to lead from door to door.
    `rug` is the carpet's flat."""
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cell = [(xs[i], ys[j]), (xs[i], ys[j + 1]), (xs[i + 1], ys[j + 1]), (xs[i + 1], ys[j])]
            if runner(i, j):
                m.sector(cell, ceil=ceil + 16, light=min(255, light + 30),
                         **dict(base, ftex=rug, ctex="AJLITE"))
            else:
                m.sector(cell, ceil=ceil, light=light, **base)


def picture(m, a, b, colour, height):
    """Hangs a framed picture of a door on the 64-long wall piece a-b.
    `height` is the wall's height there (336 or 176: see gfx.py)."""
    m.cut(a, b)
    m.line(a, b, mid=f"AJP{'A' if height == 336 else 'B'}{colour}", exact=True)


RUNNER = dict(runner=True)      # for fitted(): carpet under a raised row of lights


def fitted(m, box, features, **base):
    """A flat rectangular room (x1, y1, x2, y2) with furniture. `features` is
    a list of ((x1, y1, x2, y2), changes): each rectangle inside the room gets
    those sector properties instead of the room's (later ones win), or, for
    RUNNER, the carpet and lights of room(). The room is cut into a grid
    along every rectangle's edges, so a wall piece that needs its own texture
    must not have such an edge crossing it."""
    xs = sorted({box[0], box[2]} | {v for r, _ in features for v in (r[0], r[2])})
    ys = sorted({box[1], box[3]} | {v for r, _ in features for v in (r[1], r[3])})
    for x1, x2 in zip(xs, xs[1:]):
        for y1, y2 in zip(ys, ys[1:]):
            props = dict(base)
            for (a, b, c, d), change in features:
                if a <= x1 and x2 <= c and b <= y1 and y2 <= d:
                    if change.get("runner"):
                        props.update(ceil=base["ceil"] + 16, light=min(255, base["light"] + 30),
                                     ftex="AJRUG", ctex="AJLITE")
                    else:
                        props.update(change)
            m.sector([(x1, y1), (x1, y2), (x2, y2), (x2, y1)], **props)


def window(m, a, b, out, floor, *, sill=40, top=96, wall="AJWALL", color=None):
    """A window in the wall piece a-b (64 long), looking `out` at the sky:
    glazing bars nobody can pass, a sill, and beyond it a horizon line."""
    def off(p, d):
        return (p[0] + out[0] * d, p[1] + out[1] * d)
    m.sector([a, b, off(b, 8), off(a, 8)], floor=floor + sill, ceil=floor + top, light=255,
             wall=wall, ftex="AJTRIMF", ctex="AJTRIMF", color=color)
    m.sector([off(a, 8), off(b, 8), off(b, 12), off(a, 12)], floor=floor + sill, ceil=floor + top,
             light=255, wall=wall, ftex="F_SKY1", ctex="F_SKY1")
    m.line(off(a, 12), off(b, 12), special=9)                     # Line_Horizon
    m.line(a, b, mid="AJWIN", midboth=True, blocking=True)


def opening(m, a, b, out, floor, *, thick=16, color=None):
    """A plain open way through a wall `thick` deep, a-b its 64-wide mouth."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor, ceil=floor + DOOR_H, light=170, wall="AJTRIM",
             ftex="AJTRIMF", ctex="AJTRIMF", color=color)


def bolted(m, a, b, out, floor, tag, *, thick=16, line_id=0):
    """A steel door bolted on its far side: a-b is its mouth on the side it
    cannot be opened from, `out` points to the side with the bolt. It opens
    for good when something crosses a line given to unbolt(tag), or with
    USE from the bolt side. In a PUZZLE graph: a walk link each way that
    needs a key (a letter) lying on the bolt side and listed in `auto`.
    Every way of arriving on the bolt side has to cross an unbolt() line."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor, ceil=floor, light=160, wall="AJBOLT",
             ftex="AJTRIMF", ctex="AJTRIMF", id=tag)
    m.line(c, d, special=11, args=(tag, 32), playeruse=True, id=line_id)
    for p, q in ((a, c), (b, d)):
        m.line(p, q, mid="AJTRIM", dontpegbottom=True)


def unbolt(m, a, b, tag, special=11):
    """Crossing the two-sided line a-b draws the bolt of door `tag`."""
    m.line(a, b, special=special, args=(tag, 32), playercross=True)


SQUEEZE = 500       # line id of every squeeze (AjarHandler.Squeeze)


def squeeze(m, a, b, out, floor, *, thick=16, unbolt=None):
    """A hole through a wall, too small for a door: a-b is its mouth (48
    wide), `out` points to the other side. The player passes with empty
    hands only, and monsters not at all. In a PUZZLE graph: a walk link
    (from, to, "", "squeeze") each way, or one way if the far side is a drop.
    `unbolt` is the tag of a bolted door that coming out of it draws."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor, ceil=floor + 64, light=110, wall="AJTRIM",
             ftex="AJTRIMF", ctex="AJTRIMF")
    m.line(a, b, id=SQUEEZE, blockmonsters=True)
    if unbolt:
        m.line(c, d, special=11, args=(unbolt, 32), playercross=True)


def stairs(m, a, b, out, floor, rise, *, steps=8, depth=32, ceil=None, **k):
    """A flight of steps from the edge a-b at `floor`, going `out` and up by
    `rise` in all (negative: down)."""
    for i in range(steps):
        p1 = (a[0] + out[0] * depth * i, a[1] + out[1] * depth * i)
        p2 = (b[0] + out[0] * depth * i, b[1] + out[1] * depth * i)
        p3 = (b[0] + out[0] * depth * (i + 1), b[1] + out[1] * depth * (i + 1))
        p4 = (a[0] + out[0] * depth * (i + 1), a[1] + out[1] * depth * (i + 1))
        m.sector([p1, p2, p3, p4], floor=floor + rise * (i + 1) // steps,
                 ceil=ceil if ceil is not None else floor + 128, **k)
