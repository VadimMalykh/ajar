"""Shared pieces for Ajar maps: door colours, frame/far-side recesses, door things.

Line ids: 1xx = frames, 200 + colour = that door's far side; a fixed
doorway number n uses 150 + n and 250 + n
(number 9 is every level's way out: way_out()). 270-289 are the places a
Stray door may open onto (stray_place). 190 is the frame of a way out the
player builds (way_home), 590 both of its mouths.
"""
FRAME_T, DOOR_T = 20001, 20002
KEY_T = {"1": 20011, "2": 20012, "3": 20013, "4": 20014}      # room keys, by number
LOCK = {"1": 41, "2": 42, "3": 43, "4": 44, "12": 45, "23": 46, "34": 47}   # src/lockdefs.txt
RED, BLUE, GREEN, YELLOW, VIOLET, PINK = 1, 2, 3, 4, 5, 6
STRAY = 7           # the Stray door: no far side of its own (see stray_place)
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


def recess(m, m1, m2, out, floor, line_id, target, *, far_colour=None, color=None, arch=None, trim=None,
           home=0, chain=None, only=False):
    """A 64-wide door recess whose mouth is m1-m2 and which goes `out` of the room.

    Frames (far_colour None) get an AjarFrame thing and a usable mouth line.
    Far sides show the closed door of their colour until that door is hung.
    `target` is any valid portal line id; the script empties every portal at load.
    `arch` ("frame" or "far") makes it one end of a fixed doorway instead: see doorway().
    `trim` is (texture, flat) for the surround instead of the usual one.
    `home` (frames only) is the far-side line id of the door that makes this
    frame a way out: see way_home(). `chain` (frames only) is (the far-side
    line id of the pair's other door, the line id of the other brass frame):
    see brass_pair(). `only` (frames with `home`): no other door hangs in it.
    """
    b1 = (m1[0] + out[0] * DEPTH, m1[1] + out[1] * DEPTH)
    b2 = (m2[0] + out[0] * DEPTH, m2[1] + out[1] * DEPTH)
    if arch:
        wall, flat, mid = (trim or ("AJARCH", "AJARCHF")) + ("AJFRAME",)
    elif far_colour:
        wall, flat, mid = f"AJTR{far_colour}", f"AJTF{far_colour}", f"AJDR{far_colour}"
    else:
        wall, flat, mid = "AJTRIM", "AJTRIMF", "AJFRAME"
    if trim:
        wall, flat = trim
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
                FRAME_T, id=line_id, height=0, args=(line_id, home) + tuple(chain or (0, 0)) + (int(only),))


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


WAY_OUT = 9         # the doorway number of every level's way out


def way_out(m, x, y, colour):
    """The way out, the same in every level: far sides have a colour, the
    way out has none. A night room (ink walls and ceiling with gold stars,
    dark floor with brass inlay, gold runner), 320 by 256 with its south-west
    corner at x, y on floor 0. The far side of the door `colour` is in the
    middle of its south wall. A brass doorway joins its west and east ends,
    which face each other down the room, so through either you see the room
    again and your own back in it; walking into either ends the level.
    Candelabra stand at both ends and repeat in the doorway. Put company
    in it with things; in a PUZZLE graph it is the goal.

    It uses doorway number WAY_OUT (line ids 159 and 259)."""
    room(m, [x, x + 128, x + 192, x + 320], [y, y + 96, y + 160, y + 256],
         lambda i, j: j == 1 or (i == 1 and j == 0),
         ceil=160, light=150, wall="AJXW2", ftex="AJXG2", rug="AJXR2", ctex="AJXC2")
    recess(m, (x + 128, y), (x + 192, y), (0, -1), 0, far_id(colour), 150 + WAY_OUT, far_colour=colour)
    doorway(m, WAY_OUT, (x + 320, y + 96), (x + 320, y + 160), (1, 0), 0,
            (x, y + 96), (x, y + 160), (-1, 0), 0, trim=("AJXA", "AJXAF"))
    for xx in (x, x + 320):
        m.line((xx, y + 96), (xx, y + 160), special=243, args=(), playeruse=False, repeatspecial=False,
               playercross=True)
    for cx, cy in ((32, 48), (32, 208), (288, 48), (288, 208)):
        m.thing(x + cx, y + cy, 35)                               # candelabra


HOME, HOME_MOUTH = 190, 590
SQUEEZE = 500       # line id of every squeeze (AjarHandler.Squeeze): see squeeze()


def way_home(m, x, y, colour, *, grille=False, only=False):
    """A way out the player has to build (MAP05 on). The same night room as
    way_out(), 320 by 256 with its south-west corner at x, y on floor 0, but
    its two ends are not joined yet: the far side of the door `colour` is in
    the west end (in its own colour's surround) and an empty brass frame
    (line id HOME) in the east end,
    facing each other down the room. Hang that door in that frame and the
    room opens onto itself: the door becomes the doorway of way_out(), for
    good, and walking into either end ends the level (AjarHandler.ComeHome).

    Going through the door from wherever it hangs brings you here without
    it, so the room needs another way in, by which the door can be carried:
    the caller's job (its north and south walls are free). In a PUZZLE graph:
    the door's home and the frame HOME are in the same region, and
    `home_frame=HOME` makes hanging it there the goal.

    With `grille` (MAP08) a brass grille stands across the middle of the
    room, with a gap by the south wall that only empty hands pass (a
    squeeze). Coming through the door from wherever it hangs then brings
    you to the west half and no further with anything in hand: the frame's
    half needs a way in of its own. In a PUZZLE graph the halves are two
    regions and `home_door` names the door.

    With `only` (MAP08 since 2026-11-16, instead of the grille) the brass
    frame takes no door but `colour`. Then no other door hung there makes a
    way in for it, and it comes in on foot or not at all. In a PUZZLE graph:
    `only={HOME: colour}`."""
    room(m, [x, x + 160, x + 320] if grille else [x, x + 320], [y, y + 96, y + 160, y + 256],
         lambda i, j: j == 1, ceil=160, light=150, wall="AJXW2", ftex="AJXG2", rug="AJXR2", ctex="AJXC2")
    if grille:
        m.cut((x + 160, y + 16), (x + 160, y + 64))
        for a, b in ((y, y + 16), (y + 64, y + 96), (y + 96, y + 160), (y + 160, y + 256)):
            m.line((x + 160, a), (x + 160, b), mid="AJGRIL", midboth=True, blocking=True, wrapmidtex=True)
        m.line((x + 160, y + 16), (x + 160, y + 64), id=SQUEEZE, blockmonsters=True)
    brass = ("AJXA", "AJXAF")
    # the far side keeps the surround of its colour, so that whoever gets here
    # by another way (a Stray door) can tell which door belongs in the frame
    recess(m, (x, y + 96), (x, y + 160), (-1, 0), 0, far_id(colour), HOME, far_colour=colour)
    recess(m, (x + 320, y + 96), (x + 320, y + 160), (1, 0), 0, HOME, far_id(colour), trim=brass,
           home=far_id(colour), only=only)
    for xx in (x, x + 320):
        m.line((xx, y + 96), (xx, y + 160), id=HOME_MOUTH)
    for cx, cy in ((32, 48), (32, 208), (288, 48), (288, 208)):
        m.thing(x + cx, y + cy, 35)                               # candelabra


def way_round(m, x, y, colour, *, frame=HOME, n=WAY_OUT, floor=0):
    """A way out the player builds, the other way round (Vadim, 2026-11-16).
    The night room again, 320 by 256 with its south-west corner at x, y, but
    nothing in it faces anything. In its west wall two brass openings stand
    side by side and are one fixed doorway (number n): walk into either and
    you come out of the other, back into the room. In its east wall, the
    same way, the far side of the door `colour` and beside it an empty brass
    frame (line id `frame`). Hang that door in that frame and the east wall
    turns you round as well: through any of the four openings the room now
    repeats, and you stand in every second one, seen from behind. Then
    walking into any of them ends the level.

    Until then one turn alone never shows you yourself: the room seen
    through an opening is the room turned half round about the pier between
    the two, and the pier hides the spot where you would be.

    Everything else as way_home(): the door needs another way in (the north
    and south walls are free), and in a PUZZLE graph `home_frame=frame` is
    the goal."""
    lo, hi = (y + 32, y + 96), (y + 160, y + 224)
    room(m, [x, x + 320], [y, lo[0], lo[1], hi[0], hi[1], y + 256], lambda i, j: j in (1, 3),
         floor=floor, ceil=floor + 160, light=150, wall="AJXW2", ftex="AJXG2", rug="AJXR2", ctex="AJXC2")
    brass = ("AJXA", "AJXAF")
    doorway(m, n, (x, lo[0]), (x, lo[1]), (-1, 0), floor, (x, hi[0]), (x, hi[1]), (-1, 0), floor, trim=brass)
    recess(m, (x + 320, lo[0]), (x + 320, lo[1]), (1, 0), floor, far_id(colour), frame, far_colour=colour)
    recess(m, (x + 320, hi[0]), (x + 320, hi[1]), (1, 0), floor, frame, far_id(colour), trim=brass,
           home=far_id(colour))
    for xx in (x, x + 320):
        for a, b in (lo, hi):
            m.line((xx, a), (xx, b), id=HOME_MOUTH)
    for cx in (32, 288):
        m.thing(x + cx, y + 128, 35)                              # candelabra, on the piers


LINE_T = 20006      # AjarLine: the middle of the room a chain runs through
HOME2 = 191         # the second brass frame of a chain


def way_through(m, x, y, a, b, *, floor=0):
    """The way out as a chain (Vadim, 2026-11-16; MAP09 on): this is the room
    at its far end. The night room, 320 by 256 with its south-west corner at
    x, y, and nothing in it but the far sides of two doors: `a` in its west
    end, `b` in its east end, each in its own colour's surround, facing each
    other down the room. Somewhere else brass_pair() puts two brass frames.
    With both doors hung in those, either way round, the two rooms open onto
    each other without end; the player walks through into this one, and
    leaving it again, by either door, ends the level (AjarHandler.ChainTick).

    Nothing else leads here, so until then it is a dead end with two door
    backs in it; and with the two doors hung in any two frames it is a way
    between them, for whatever is carried. A Stray door may open onto either
    far side, so the room needs a way out on foot: the caller's job (its
    north and south walls are free; a drop, so that it stays a way out only).
    In a PUZZLE graph: both doors' home, and `home_chain`."""
    room(m, [x, x + 320], [y, y + 96, y + 160, y + 256], lambda i, j: j == 1, floor=floor,
         ceil=floor + 160, light=150, wall="AJXW2", ftex="AJXG2", rug="AJXR2", ctex="AJXC2")
    recess(m, (x, y + 96), (x, y + 160), (-1, 0), floor, far_id(a), HOME, far_colour=a)
    recess(m, (x + 320, y + 96), (x + 320, y + 160), (1, 0), floor, far_id(b), HOME, far_colour=b)
    m.thing(x + 160, y + 128, LINE_T, args=(160, 128))
    for cx, cy in ((32, 48), (32, 208), (288, 48), (288, 208)):
        m.thing(x + cx, y + cy, 35)                               # candelabra


def brass_pair(m, w1, w2, e1, e2, floor, a, b):
    """The two brass frames of a chain (see way_through), line ids HOME and
    HOME2: w1-w2 is the mouth of the one in a west wall, e1-e2 of the one in
    an east wall, facing each other across the caller's room. The doors `a`
    and `b` belong in them, either way round. Until both hang there each can
    be taken down again like any door."""
    brass = ("AJXA", "AJXAF")
    recess(m, w1, w2, (-1, 0), floor, HOME, far_id(a), trim=brass, home=far_id(a), chain=(far_id(b), HOME2))
    recess(m, e1, e2, (1, 0), floor, HOME2, far_id(a), trim=brass, home=far_id(a), chain=(far_id(b), HOME))


STRAY_ID = 270      # line ids 270..289: the places Stray doors may open onto


def stray_place(m, k, m1, m2, out, floor, *, color=None, target=101):
    """Place number k (0..19) of the level's pool for Stray doors: a recess
    like a far side, with mouth m1-m2, showing a shut Stray door until one
    opens onto it. Which place a Stray door opens onto is drawn from the
    pool when it is hung; it stays open for a few seconds and is then gone.
    The far side of every coloured door that hangs nowhere at that moment
    is in the pool too, by itself: a stray place is for somewhere no
    coloured door leads (a secret, a nasty spot).
    Rules (PLAN.md, "Stray door"): every place needs a way out on foot, and
    a secret one also an ordinary way in. In a PUZZLE graph: `pool`.
    `target` is any frame's line id in the level (see recess)."""
    recess(m, m1, m2, out, floor, STRAY_ID + k, target, far_colour=STRAY, color=color)


def stray(m, x, y, *, angle=0):
    """A Stray door leaning at x, y. A level can have several."""
    m.thing(x, y, DOOR_T, angle=angle, args=(far_id(STRAY), STRAY, 0))


def roomdoor(m, a, b, out, floor, *, thick=16, keys="", line_id=0, look="", skin=""):
    """An ordinary door, as in any Doom level: opened with USE, shuts by
    itself, and monsters can open it too. It fills the wall between two
    rooms that are `thick` apart; a-b is its 64-wide mouth on one side and
    `out` points to the other. It is plain wood and nobody can carry it.
    Declare both rooms first, so that the door is at the back of its lines.
    The rooms should be no more than 256 high where it stands (see gfx.py).

    With `keys` ("1", "23"...) it is locked and needs every one of those
    room keys (see key()); its lock plates show their numbers, and monsters
    cannot open it. In a PUZZLE graph that is a walk link with keys.
    `line_id` names the mouth line a-b, for tests. `look` picks one of
    MAP02's candidate doors (gfx_hotel.py); `skin` is the name of another
    door texture, to which the keys of a locked door are added."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor, ceil=floor, light=160, wall=skin + keys if skin else (f"AJ2K{look}{keys}" if keys else f"AJ2D{look}") if look else f"AJHK{keys}" if keys else "AJHDOR",
             ftex="AJTRIMF", ctex="AJTRIMF")
    for p, q in ((a, b), (c, d)):
        if keys:
            m.line(p, q, special=13, args=(0, 24, 150, LOCK[keys]), playeruse=True, repeatspecial=True,
                   exact=True)
        else:
            m.line(p, q, special=12, args=(0, 24, 150), playeruse=True, monsteruse=True,
                   repeatspecial=True, exact=True)             # one leaf, even where the room's floor cuts its line
    if line_id:
        m.line(a, b, id=line_id)
    for p, q in ((a, c), (b, d)):
        m.line(p, q, mid="AJTRIM", dontpegbottom=True)


def key(m, number, x, y):
    """A numbered room key lying at x, y."""
    m.thing(x, y, KEY_T[str(number)])


def room(m, xs, ys, runner, *, ceil, light, rug="AJRUG", lite="AJLITE", lift=16, **base):
    """A flat rectangular room cut into a grid by the lists xs and ys. Cells
    for which runner(i, j) is true (column i, row j) are a strip of carpet
    under a raised row of ceiling lights; use it to lead from door to door.
    `rug` is the carpet's flat."""
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cell = [(xs[i], ys[j]), (xs[i], ys[j + 1]), (xs[i + 1], ys[j + 1]), (xs[i + 1], ys[j])]
            if runner(i, j):
                m.sector(cell, ceil=ceil + lift, lift=lift, light=min(255, light + 30),
                         **dict(base, ftex=rug, ctex=lite))
            else:
                m.sector(cell, ceil=ceil, light=light, **base)


def picture(m, a, b, colour, height, tex=None):
    """Hangs a framed picture of a door on the 64-long wall piece a-b.
    `height` is the wall's height there (336 or 176: see gfx.py); `tex` is
    the picture on another wall than the plain one."""
    m.cut(a, b)
    m.line(a, b, mid=tex or f"AJP{'A' if height == 336 else 'B'}{colour}", exact=True)


RUNNER = dict(runner=True)      # for fitted(): carpet under a raised row of lights


def fitted(m, box, features, rug="AJRUG", lite="AJLITE", lift=16, **base):
    """A flat rectangular room (x1, y1, x2, y2) with furniture. `features` is
    a list of ((x1, y1, x2, y2), changes): each rectangle inside the room gets
    those sector properties instead of the room's (later ones win), or, for
    RUNNER, the carpet and lights of room(). The room is cut into a grid
    along every rectangle's edges, so a wall piece that needs its own texture
    must not have such an edge crossing it. `rug` is the carpet's flat, `lite`
    the ceiling over it and `lift` how far that ceiling is raised."""
    xs = sorted({box[0], box[2]} | {v for r, _ in features for v in (r[0], r[2])})
    ys = sorted({box[1], box[3]} | {v for r, _ in features for v in (r[1], r[3])})
    for x1, x2 in zip(xs, xs[1:]):
        for y1, y2 in zip(ys, ys[1:]):
            props = dict(base)
            for (a, b, c, d), change in features:
                if a <= x1 and x2 <= c and b <= y1 and y2 <= d:
                    if change.get("runner"):
                        props.update(ceil=base["ceil"] + lift, light=min(255, base["light"] + 30),
                                     ftex=rug, ctex=lite, lift=lift)
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
    m.line(c, d, special=11, args=(tag, 32), playeruse=True, id=line_id, exact=True)
    m.line(a, b, exact=True)                  # one leaf, even where the room's floor cuts its line
    for p, q in ((a, c), (b, d)):
        m.line(p, q, mid="AJTRIM", dontpegbottom=True)


def unbolt(m, a, b, tag, special=11):
    """Crossing the two-sided line a-b draws the bolt of door `tag`."""
    m.line(a, b, special=special, args=(tag, 32), playercross=True)


SHUTTER = 600       # sector tag of a level's timed shutter (AjarHandler.ShutterTick)


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


def shutter(m, a, b, out, floor, *, thick=16, line_id=0):
    """A rolling shutter that a lever() somewhere else sends up, and that
    comes down again by itself a few seconds later (Vadim's idea,
    2026-11-15): a-b is its mouth on the side the lever serves, `out`
    points to the other. From that other side it can be pushed up with USE,
    but only for a moment: enough to walk out, not to fetch anything.
    Declare the rooms on both sides first. One to a level (sector tag
    SHUTTER); the time left is on the HUD while it is up. Keep monsters
    from standing under it: a shutter that meets something goes up again.
    In a PUZZLE graph: `dash`, and a walk link from the far side back."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor, ceil=floor, light=160, wall="AJSHUT",
             ftex="AJTRIMF", ctex="AJTRIMF", id=SHUTTER)
    m.line(c, d, special=12, args=(SHUTTER, 64, 35), playeruse=True, repeatspecial=True)
    if line_id:
        m.line(a, b, id=line_id)
    for p, q in ((a, c), (b, d)):
        m.line(p, q, mid="AJTRIM", dontpegbottom=True)


def lever(m, a, b, seconds, *, line_id=0):
    """The lever of the level's shutter(), on the 64-long wall piece a-b:
    USE sends the shutter up for `seconds`."""
    m.cut(a, b)
    m.line(a, b, special=12, args=(SHUTTER, 64, seconds * 35), playeruse=True, repeatspecial=True,
           mid="AJLEVR", exact=True, id=line_id)


# --- rooms that are not rectangles ---------------------------------------------
def octagon(x1, y1, x2, y2, c):
    """The rectangle with its corners cut off c along each wall."""
    return [(x1 + c, y1), (x2 - c, y1), (x2, y1 + c), (x2, y2 - c), (x2 - c, y2), (x1 + c, y2), (x1, y2 - c),
            (x1, y1 + c)]


def _inside(p, shape):
    if len(shape) == 4 and not isinstance(shape[0], (tuple, list)):
        return shape[0] < p[0] < shape[2] and shape[1] < p[1] < shape[3]
    signs = [(b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
             for a, b in zip(shape, list(shape[1:]) + [shape[0]])]
    return all(s > 0 for s in signs) or all(s < 0 for s in signs)


def _halves(poly, a, b):
    """The convex polygon `poly` cut along the line through a and b."""
    from fractions import Fraction
    def s(p):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    left, right = [], []
    for p, q in zip(poly, poly[1:] + poly[:1]):
        sp, sq = s(p), s(q)
        if sp >= 0:
            left.append(p)
        if sp <= 0:
            right.append(p)
        if sp * sq < 0:
            t = Fraction(sp, sp - sq)
            x = (p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]))
            left.append(x)
            right.append(x)
    return [h for h in (left, right) if len(h) > 2 and any(s(p) != 0 for p in h)]


def shaped(m, box, features, outline=None, **base):
    """fitted() for rooms with slanting walls and many small changes. `outline`
    is the room, a convex polygon inside `box` (default: the box). A feature's
    place is a rectangle (x1, y1, x2, y2) or a convex polygon; later ones win.
    Rectangles reaching past the box are cut off at it. No RUNNER. Pieces
    alike are joined, so that a room with a pool of light at every lamp does
    not become a thousand sectors."""
    def is_rect(s):
        return len(s) == 4 and not isinstance(s[0], (tuple, list))

    feats = []
    for shape, change in features:
        if is_rect(shape):
            shape = (max(shape[0], box[0]), max(shape[1], box[1]), min(shape[2], box[2]), min(shape[3], box[3]))
            if shape[0] >= shape[2] or shape[1] >= shape[3]:
                continue
        feats.append((shape, change))
    polys = [s for s, _ in feats if not is_rect(s)] + ([outline] if outline else [])
    slants = [(a, b) for poly in polys for a, b in zip(poly, list(poly[1:]) + [poly[0]]) if a[0] != b[0] and a[1] != b[1]]
    xs = sorted({box[0], box[2]} | {v for s, _ in feats if is_rect(s) for v in (s[0], s[2])} | {p[0] for poly in polys for p in poly})
    ys = sorted({box[1], box[3]} | {v for s, _ in feats if is_rect(s) for v in (s[1], s[3])} | {p[1] for poly in polys for p in poly})

    def props_at(piece):
        c = (sum(p[0] for p in piece) / len(piece), sum(p[1] for p in piece) / len(piece))
        if outline and not _inside(c, outline):
            return None
        props = dict(base)
        for shape, change in feats:
            if _inside(c, shape):
                props.update(change)
        return props

    def num(v):
        return int(v) if v == int(v) else float(v)

    whole = {}                                                       # (i, j) -> props of an uncut cell
    for i, (x1, x2) in enumerate(zip(xs, xs[1:])):
        for j, (y1, y2) in enumerate(zip(ys, ys[1:])):
            pieces = [[(x1, y1), (x1, y2), (x2, y2), (x2, y1)]]
            for a, b in slants:
                if min(a[0], b[0]) <= x1 and x2 <= max(a[0], b[0]) and min(a[1], b[1]) <= y1 and y2 <= max(a[1], b[1]):
                    pieces = [h for piece in pieces for h in _halves(piece, a, b)]
            if len(pieces) == 1:
                whole[i, j] = props_at(pieces[0])
                continue
            for piece in pieces:
                props = props_at(piece)
                if props is not None:
                    m.sector([(num(x), num(y)) for x, y in piece], **props)
    # join uncut cells that are alike: along x, then rows of the same run along y
    runs = {}                                                        # (i1, i2, key) -> [j1, j2, props]
    for j in range(len(ys) - 1):
        i, row = 0, []
        while i < len(xs) - 1:
            props = whole.get((i, j))
            if props is None:
                i += 1
                continue
            k = i
            while whole.get((k + 1, j)) == props:
                k += 1
            row.append((i, k + 1, props))
            i = k + 1
        for i1, i2, props in row:
            key = (i1, i2, repr(sorted(props.items(), key=repr)))
            if key in runs and runs[key][-1][1] == j:
                runs[key][-1][1] = j + 1
            else:
                runs.setdefault(key, []).append([j, j + 1, props])
    for (i1, i2, _), spans in runs.items():
        for j1, j2, props in spans:
            m.sector([(xs[i1], ys[j1]), (xs[i1], ys[j2]), (xs[i2], ys[j2]), (xs[i2], ys[j1])], **props)


def beyond(m, path, steps, *, start=None, end=None):
    """Strips of ground along the outside of a place's edge. `path` is the
    edge, a list of points with the outside on the right hand, turning only
    by right angles; `steps` is [(distance out, sector properties), ...], each
    strip reaching from the one before (or the edge) to its distance. At the
    path's two ends the strips are cut square, or, given the direction
    (dx, dy) the edge would go on in (`end`) or came from (`start`), mitred
    as at a corner. Returns (ends, lines): the strips' end edges, [[(a, b),
    ...] at the start, the same at the end], one per strip; and each strip's
    far edge, piece by piece."""
    def right(a, b):
        dx, dy = (b[0] > a[0]) - (b[0] < a[0]), (b[1] > a[1]) - (b[1] < a[1])
        return (dy, -dx)

    n = len(path)
    norms = [right(path[i], path[i + 1]) for i in range(n - 1)]
    first = right((0, 0), start) if start else norms[0]
    last = right((0, 0), end) if end else norms[-1]
    pairs = [(first, norms[0])] + [(norms[i - 1], norms[i]) for i in range(1, n - 1)] + [(norms[-1], last)]

    def off(i, d):
        (ax, ay), (bx, by) = pairs[i]
        nx, ny = (ax, ay) if (ax, ay) == (bx, by) else (ax + bx, ay + by)
        return (path[i][0] + nx * d, path[i][1] + ny * d)

    caps, lines, d0 = [[], []], [], 0
    for d1, props in steps:
        for i in range(n - 1):
            m.sector([off(i, d0), off(i + 1, d0), off(i + 1, d1), off(i, d1)], **props)
        caps[0].append((off(0, d0), off(0, d1)))
        caps[1].append((off(n - 1, d0), off(n - 1, d1)))
        lines.append([(off(i, d1), off(i + 1, d1)) for i in range(n - 1)])
        d0 = d1
    return caps, lines
