"""Shared pieces for Ajar maps: door colours, frame/far-side recesses, door things.

Line ids: 1xx = frames, 200 + colour = that door's far side; a fixed
doorway number n uses 150 + n and 250 + n
(number 9 is every level's way out: way_out()). 270-289 are the places a
Stray door may open onto (stray_place). 190 is the frame of a way out the
player builds (way_home), 590 both of its mouths; 193 and 591 the same for
a secret way out the player builds (MAP15).
"""
FRAME_T, DOOR_T = 20001, 20002
KEY_T = {"1": 20011, "2": 20012, "3": 20013, "4": 20014}      # room keys, by number
LOCK = {"1": 41, "2": 42, "3": 43, "4": 44, "12": 45, "23": 46, "34": 47}   # src/lockdefs.txt
RED, BLUE, GREEN, YELLOW, VIOLET, PINK = 1, 2, 3, 4, 5, 6
STRAY = 7           # the Stray door: no far side of its own (see stray_place)
TEAL, ORANGE = 8, 9 # the colours of Pairs (see pair)
NAMES = {RED: "RED", BLUE: "BLUE", GREEN: "GREEN", YELLOW: "YELLOW", VIOLET: "VIOLET", PINK: "PINK"}
# A Pair's two leaves in a PUZZLE graph (solve.py): keys of their own, since
# both are one colour. doors={**ajarmap.leaves(TEAL, "hall", "hall"), ...}
LEAVES = {TEAL: (81, 82), ORANGE: (91, 92)}
NAMES.update({81: "a TEAL leaf", 82: "the other TEAL leaf", 91: "an ORANGE leaf", 92: "the other ORANGE leaf"})


def leaves(colour, *where):
    """The PUZZLE entries of a Pair's two leaves: each of `where` is the
    region a leaf leans in, or the line id of the frame it starts hung in."""
    a, b = LEAVES[colour]
    return {k: dict(pair=o, **({"lean": w} if isinstance(w, str) else {"frame": w}))
            for k, o, w in ((a, b, where[0]), (b, a, where[1]))}
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
           home=0, chain=None, only=False, tag=0):
    """A 64-wide door recess whose mouth is m1-m2 and which goes `out` of the room.

    Frames (far_colour None) get an AjarFrame thing and a usable mouth line.
    Far sides show the closed door of their colour until that door is hung.
    `target` is any valid portal line id; the script empties every portal at load.
    `arch` ("frame" or "far") makes it one end of a fixed doorway instead: see doorway().
    `trim` is (texture, flat) for the surround instead of the usual one.
    `home` (frames only) is the far-side line id of the door that makes this
    frame a way out: see way_home(). `chain` (frames only) is (the far-side
    line id of the pair's other door, the line id of the other brass frame):
    see brass_pair(). `only` (frames with `home`): no other door hangs in it;
    2: none but the two of `home` and `chain`, and it is no way out by itself
    (way_longer). `only=3` with `home` a Pair's colour (TEAL, ORANGE): the
    frame takes a leaf of that Pair and nothing else (MAP12's booth; in a
    PUZZLE graph `only={frame: the two leaves' keys}`). `only=4` with `home` a
    plain colour: the frame takes any door but that one, and its trim says so
    (MAP11's archive; in a PUZZLE graph `only={frame: every other door}`). `tag` is a sector tag for the recess and its stub: that of
    the lift car it is in, so that it rides with the car (see lift_button).
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
    elif only == 4:
        wall, flat = f"AJNO{home}", f"AJNF{home}"
    m.sector([m1, m2, b2, b1], floor=floor, ceil=floor + DOOR_H, light=176,
             wall=wall, ftex=flat, ctex=flat, color=color, id=tag)
    # GZDoom only lets things walk through a portal line that has real space
    # behind it, so every portal line gets a small dark stub sector at its back.
    m.sector([b1, b2, (b2[0] + out[0] * STUB, b2[1] + out[1] * STUB),
              (b1[0] + out[0] * STUB, b1[1] + out[1] * STUB)],
             floor=floor, ceil=floor + DOOR_H, light=96, wall=wall, ftex=flat, ctex=flat, id=tag)
    # Line_SetPortal: target id, this line, type 1 (teleporter), align to floor
    m.line(b1, b2, id=line_id, special=156, args=(target, 0, 1, 1), mid=mid)
    if arch == "frame" or not (arch or far_colour):
        m.line(m1, m2, special=130, args=(line_id,), playeruse=True, repeatspecial=True)
        m.thing((b1[0] + b2[0]) / 2 - out[0] * 8, (b1[1] + b2[1]) / 2 - out[1] * 8,
                FRAME_T, id=line_id, height=0, args=(line_id, home) + tuple(chain or (0, 0)) + (int(only),))


LIFT = 700          # sector tag of a level's lift car, and of the recesses in it
LIFT_T = 20050      # AjarLiftButton


def lift_button(m, a, b, z, tid, at, *, tag=LIFT, tex="AJEXIT", foot=False):
    """A button on the wall a-b that sends the lift car (every sector with
    `tag`: the car, and the recesses in it, made with recess(tag=)) to the
    floor height z. The car's floor and ceiling move together, so a landing
    is a sector beside it whose floor is at a stop's height and whose
    ceiling is lower than the car's floor at the next stop up: at any other
    stop it is a wall. `tid` is a thing id of its own for each button, `at` any
    spot in the room for the thing that stands for it. `foot`: `tex` is
    laid from the floor up (a plate at hand height on a strip of its own).
    A frame or a far side in the car rides with it (src/zscript/lift.zs)."""
    m.cut(a, b)
    m.line(a, b, special=130, args=(tid,), playeruse=True, repeatspecial=True, mid=tex, exact=True,
           **(dict(dontpegbottom=True) if foot else {}))
    m.thing(at[0], at[1], LIFT_T, id=tid, args=(tag, z))


TARGET_T, EMITTER_T, WATCH_T = 20060, 20061, 20062     # AjarTarget, AjarEmitter, AjarWatch (src/zscript/optics.zs)


def steel(m, a, b, out, floor, tag, *, thick=16):
    """A steel door with no handle on either side, between two rooms `thick`
    apart: a-b is its 64-wide mouth, `out` points to the other room. It opens
    for good when the target() with its `tag` is set off. In a PUZZLE graph:
    a walk link each way that needs a key (a letter) listed in `sights`."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor, ceil=floor, light=160, wall="AJBOLT", ftex="AJTRIMF", ctex="AJTRIMF", id=tag)
    for p, q in ((a, b), (c, d)):
        m.line(p, q, exact=True)
    for p, q in ((a, c), (b, d)):
        m.line(p, q, mid="AJTRIM", dontpegbottom=True)


def target(m, x, y, tag, *, beam=False, z=32, unseen=False):
    """Something to shoot, `z` above the floor at x, y (stand it 12 clear of
    its wall): set off, it opens every steel() door with `tag`. A plain one
    is set off by any shot of the player's, also through a hung door (the
    engine carries bullets through). With `beam` it is a sensor, and only an
    emitter()'s beam sets it off. In a PUZZLE graph: `sights`. `unseen`:
    until it is set off it is drawn only in mirrors."""
    m.thing(x, y, TARGET_T, height=z, args=(tag, int(beam), int(unseen)))


UNSEEN_T = 20093    # AjarUnseen


def unseen(m, box):
    """Every monster that stands in `box` (x1, y1, x2, y2) when the level
    begins is drawn only in mirrors (a Line_Mirror wall) while it is alive
    and in the box. So is one an ambush() brings into the box later
    (2026-11-19)."""
    x1, y1, x2, y2 = box
    m.thing((x1 + x2) / 2, (y1 + y2) / 2, UNSEEN_T, args=((x2 - x1) // 2, (y2 - y1) // 2))


def emitter(m, x, y, angle, tid, a, b, *, tex="AJEXIT", foot=False):
    """A fixed lamp at x, y that fires a beam along `angle` (40 above the
    floor) when the button on the wall piece a-b is pressed. The beam is a
    missile: it goes through a hung door and keeps its line, so it comes out
    square to whatever frame the door of the far side it flew into hangs in.
    `foot`: `tex` is laid from the floor up, as in lift_button()."""
    m.thing(x, y, EMITTER_T, angle=angle, id=tid)
    m.cut(a, b)
    m.line(a, b, special=130, args=(tid,), playeruse=True, repeatspecial=True, mid=tex, exact=True,
           **(dict(dontpegbottom=True) if foot else {}))


def watch(m, box, colour):
    """The room `box` (x1, y1, x2, y2) is the far side of the door `colour`,
    and what lives there fires through that door wherever it hangs: at the
    player before its frame, and at whatever is in another watched room
    whose door hangs in the frame facing it (AjarHandler.OpticsTick)."""
    x1, y1, x2, y2 = box
    m.thing((x1 + x2) / 2, (y1 + y2) / 2, WATCH_T, args=((x2 - x1) // 2, (y2 - y1) // 2, far_id(colour)))


def door(m, colour, x, y, *, angle=0, frame=0, unseen=False):
    """A door thing. With `frame` it starts hung there (x, y only pick the sector);
    otherwise it leans at x, y facing `angle`. `unseen`: until it is first
    taken it is drawn only in mirrors (and has no glow)."""
    m.thing(x, y, DOOR_T, angle=angle, args=(far_id(colour), colour, frame, 2 if unseen else 0))


def pair(m, colour, *leaves):
    """A Pair: two leaves of one colour (TEAL or ORANGE) that open onto each
    other and have no far side. Each of `leaves` is (x, y, angle) for one
    that leans there, or (x, y, angle, frame) for one that starts hung."""
    assert len(leaves) == 2 and colour in (TEAL, ORANGE)
    for x, y, angle, *frame in leaves:
        m.thing(x, y, DOOR_T, angle=angle, args=(0, colour, frame[0] if frame else 0, 0, colour))


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

    `colour` None (MAP17): no far side; the middle of the south wall is
    plain wall, and the caller makes the way in (a room touching it there
    opens onto it).

    It uses doorway number WAY_OUT (line ids 159 and 259)."""
    room(m, [x, x + 128, x + 192, x + 320], [y, y + 96, y + 160, y + 256],
         lambda i, j: j == 1 or (i == 1 and j == 0),
         ceil=160, light=150, wall="AJXW2", ftex="AJXG2", rug="AJXR2", ctex="AJXC2")
    if colour:
        recess(m, (x + 128, y), (x + 192, y), (0, -1), 0, far_id(colour), 150 + WAY_OUT, far_colour=colour)
    doorway(m, WAY_OUT, (x + 320, y + 96), (x + 320, y + 160), (1, 0), 0,
            (x, y + 96), (x, y + 160), (-1, 0), 0, trim=("AJXA", "AJXAF"))
    for xx in (x, x + 320):
        m.line((xx, y + 96), (xx, y + 160), special=243, args=(), playeruse=False, repeatspecial=False,
               playercross=True)
    for cx, cy in ((32, 48), (32, 208), (288, 48), (288, 208)):
        m.thing(x + cx, y + cy, 35)                               # candelabra


HOME, HOME_MOUTH = 190, 590
SECRET_HOME, SECRET_MOUTH = 193, 591    # a secret way out the player builds (way_home(frame=, mouth=))
SQUEEZE = 500       # line id of every squeeze (AjarHandler.Squeeze): see squeeze()


def way_home(m, x, y, colour, *, grille=False, only=False, floor=0, frame=HOME, mouth=HOME_MOUTH, rose=False):
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
    frame takes no door but `colour` (and its brass is inlaid with that
    colour, to be told by). Then no other door hung there makes a
    way in for it, and it comes in on foot or not at all. In a PUZZLE graph:
    `only={HOME: colour}`. `floor`: the room's floor, where it is not 0
    (MAP12's is on the top floor).

    A secret way out the player builds (MAP15 since 2026-11-19): `frame` and
    `mouth` are SECRET_HOME and SECRET_MOUTH instead, and `rose` gives it the
    look of PINK's places (ROSE, as way_longer()) and makes the carpet strip
    one secret sector. Hung there, the door turns its mouths into
    Exit_Secret, and the plain way out is not touched (ComeHome)."""
    tinted = dict(color=ROSE) if rose else {}
    room(m, [x, x + 160, x + 320] if grille else [x, x + 320], [y, y + 96, y + 160, y + 256],
         lambda i, j: j == 1, ceil=floor + 160, light=150, wall="AJXW2", ftex="AJXG2", rug="AJXR2", ctex="AJXC2",
         floor=floor, **tinted, **(dict(strip=dict(special=1024)) if rose else {}))
    if grille:
        m.cut((x + 160, y + 16), (x + 160, y + 64))
        for a, b in ((y, y + 16), (y + 64, y + 96), (y + 96, y + 160), (y + 160, y + 256)):
            m.line((x + 160, a), (x + 160, b), mid="AJGRIL", midboth=True, blocking=True, wrapmidtex=True)
        m.line((x + 160, y + 16), (x + 160, y + 64), id=SQUEEZE, blockmonsters=True)
    brass = ("AJXA", "AJXAF")
    # the far side keeps the surround of its colour, so that whoever gets here
    # by another way (a Stray door) can tell which door belongs in the frame
    recess(m, (x, y + 96), (x, y + 160), (-1, 0), floor, far_id(colour), frame, far_colour=colour, **tinted)
    # ... and a frame that takes that door only says so: its brass is inlaid
    # with the door's colour
    recess(m, (x + 320, y + 96), (x + 320, y + 160), (1, 0), floor, frame, far_id(colour),
           trim=(f"AJXA{colour}", f"AJXF{colour}") if only else brass, home=far_id(colour), only=only, **tinted)
    for xx in (x, x + 320):
        m.line((xx, y + 96), (xx, y + 160), id=mouth)
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


AMBUSH_T = 20030    # AjarAmbush: a monster that is not there yet


def ambush(m, cause, kind, *spots, angle=0, after=0, near=0):
    """Monsters of Doom editor number `kind` that come in a flash at `spots`
    when the player takes something: `cause` is a room key's number (1..4),
    or 10 plus the colour of a door, taken for the first time; or 20 plus the
    tag of a target() or sensor, once that is set off (MAP15, 2026-11-20); or
    40 plus the tag a checker opens, once its order is filled (MAP17, map17.zs).
    `near`: they hold back further until the player is within that distance
    of the spot and in sight of it: an ambush in a room the player comes back
    to, not one that walks out to meet him. Doom's oldest
    trick, and nothing the solver needs to know about. They are thinned on
    the easier difficulties as placed monsters are (udmf.Map._skills): of a
    level's ambushers, in the order given, every second one stays on 1 and
    three in four on 2. Keep the spots clear of walls and of each other;
    one whose place is taken waits until it is free. `after`: seconds they
    hold back once the thing is taken: a second wave, when the first looked
    like all of it."""
    for x, y in spots:
        i = m.ambushers = getattr(m, "ambushers", -1) + 1
        m.thing(x, y, AMBUSH_T, angle=angle, args=(cause, kind, after, near), skill=1 if i % 2 == 0 else 3 if i % 4 == 3 else 2)


LINE_T = 20006      # AjarLine: the middle of the room a chain runs through
HOME2 = 191         # the second brass frame of a chain


HOME3 = 192         # the third frame of a longer chain (way_longer)
ROSE = 0xFFC0DC     # the tint of PINK's places


def way_through(m, x, y, a, b, *, floor=0, longer=None):
    """The way out as a chain (Vadim, 2026-11-16; MAP09 on): this is the room
    at its far end. The night room, 320 by 256 with its south-west corner at
    x, y, and nothing in it but the far sides of two doors: `a` in its west
    end, `b` in its east end, each in its own colour's surround, facing each
    other down the room. Somewhere else brass_pair() puts two brass frames.
    With both doors hung in those, either way round, the two rooms open onto
    each other without end; the player walks through into this one, and
    leaving it again, by either door, ends the level (AjarHandler.ChainTick).
    Leaving it by the way out on foot (below) ends nothing.

    Nothing else leads here, so until then it is a dead end with two door
    backs in it; and with the two doors hung in any two frames it is a way
    between them, for whatever is carried. A Stray door may open onto either
    far side, so the room needs a way out on foot: the caller's job (its
    north and south walls are free; a drop, so that it stays a way out only;
    and not within 64 of the middle of an end wall, where ChainTick takes a
    leaving for one by a door).
    In a PUZZLE graph: both doors' home, and `home_chain`."""
    room(m, [x, x + 320], [y, y + 96, y + 160, y + 256], lambda i, j: j == 1, floor=floor,
         ceil=floor + 160, light=150, wall="AJXW2", ftex="AJXG2", rug="AJXR2", ctex="AJXC2")
    recess(m, (x, y + 96), (x, y + 160), (-1, 0), floor, far_id(a), HOME, far_colour=a)
    recess(m, (x + 320, y + 96), (x + 320, y + 160), (1, 0), floor, far_id(b), HOME, far_colour=b)
    m.thing(x + 160, y + 128, LINE_T, args=(160, 128) + ((HOME3, far_id(longer)) if longer else ()))
    for cx, cy in ((32, 48), (32, 208), (288, 48), (288, 208)):
        m.thing(x + cx, y + cy, 35)                               # candelabra


def way_longer(m, x, y, c, a, b, *, floor=0, **base):
    """The third room of a longer chain, and a secret way out (Vadim,
    2026-11-17; MAP10). A room 320 by 256 with its south-west corner at x, y:
    the far side of the door `c` in its west end, an empty brass frame (line
    id HOME3) in its east end, facing each other down the room. It is the
    room `c` has always opened onto: a secret (the sector is one), with
    whatever the caller puts in it. Nothing else leads here.

    The plain way out is way_through()'s loop of two rooms. Hang `c` in one
    of the brass_pair() frames instead, one of the pair's own doors in the
    other, and the pair's second door in this room's frame: now three rooms
    open onto each other without end, this one between the other two.
    Closing that loop is a secret of its own, and leaving the line by it is
    the secret way out (AjarHandler.LoopLen). A door comes in here only
    through `c`, hung somewhere else at the time.

    The frame takes any door (Vadim, 2026-11-18; AjarFrame args[4] = 2 only
    marks it as the third frame). What makes that safe: no Stray door opens
    onto `c`'s far side (AjarHandler.StrayPool, and the solver), so whoever
    hangs a door here came through `c`, which hangs somewhere they can walk
    to, and the door can be fetched again. (With a Stray door bringing them
    here with anything in hand, the solver found levels lost.) Only `c`
    itself does not hang here: the room would open onto itself, and left by
    its way out on foot it would be shut for good.

    The room wants a way out on foot all the same, as in way_through(): the
    caller's job. In a PUZZLE graph: `c`'s home, frame HOME3, and
    home_chain's `secret`."""
    look = dict(dict(ceil=floor + 160, light=160, wall="AJXW2", ftex="AJXG2", ctex="AJXC2", color=ROSE), **base)
    for y1, y2, strip in ((y, y + 96, {}), (y + 160, y + 256, {}),
                          (y + 96, y + 160, dict(ftex="AJXR2", special=1024))):   # one secret: the carpet you arrive on
        m.sector(rect4(x, y1, x + 320, y2), floor=floor, **dict(look, **strip))
    recess(m, (x, y + 96), (x, y + 160), (-1, 0), floor, far_id(c), HOME, far_colour=c, color=ROSE)
    recess(m, (x + 320, y + 96), (x + 320, y + 160), (1, 0), floor, HOME3, far_id(c), trim=("AJXA", "AJXAF"),
           color=ROSE, home=far_id(a), chain=(far_id(b), 0), only=2)


def brass_pair(m, w1, w2, e1, e2, floor, a, b, *, outs=((-1, 0), (1, 0))):
    """The two brass frames of a chain (see way_through), line ids HOME and
    HOME2: w1-w2 is the mouth of the one in a west wall, e1-e2 of the one in
    an east wall, facing each other across the caller's room (`outs`: the
    two walls' directions, if they are others). The doors `a` and `b` belong
    in them, either way round; they are frames like any other, and whatever
    hangs in them can be taken down again.

    One of the two may be in a lift car instead (MAP14: two recess() calls
    with `chain=`, the car's with `tag=`), across a landing from the other:
    the loop is then closed only while the car stands at that floor
    (AjarHandler.BrassLevel; `home_chain=dict(level=n)` in a PUZZLE graph)."""
    brass = ("AJXA", "AJXAF")
    recess(m, w1, w2, outs[0], floor, HOME, far_id(a), trim=brass, home=far_id(a), chain=(far_id(b), HOME2))
    recess(m, e1, e2, outs[1], floor, HOME2, far_id(a), trim=brass, home=far_id(a), chain=(far_id(b), HOME))


BUS_H = 144         # how tall the bus stands


def bus(m, x, y, *, face=1, floor=0, first=1, slots=range(6), deep=48, free=False, livery="B", **ground):
    """One face of the bus (Vadim's idea, 2026-11-16; MAP10): the flat red
    outline of a bus standing at its stop, 800 long, with room for six
    openings: one in each of `slots` (0..5, west to east), numbered from
    `first`. x, y is the west end of the face,
    which looks south (face=1) or north (-1). Returns the doors' mouths,
    [(m1, m2), ...]: the caller makes a recess() of each, going into the bus
    (0, face): a frame, a far side, an end of a doorway(). The bus is 64 deep
    behind a face, so two faces back to back want 144 between them.

    The bus is not a room and has no roof to stand on: it is a block
    BUS_H high, with the sky over it. In front of the
    face is a strip of pavement `deep` wide whose sky is BUS_H up too (that
    is what keeps the wall over each door from being drawn, and anything
    from flying over). `ground` is the strip's floor (ftex=, light=...).

    `livery` is the letter of another bus's textures (gfx_bus.LIVERIES).

    `free` (Vadim, 2026-11-17: a bus you can walk round, as in the film):
    the strip's ends are open, the caller's ground goes on past them and
    round the bus, and bus_ends() gives the bus its front and its back.
    The engine draws sky over a solid block as far up as the sky goes, so
    nothing that can be seen behind a free bus may stand taller than it:
    the walls of the place it stands in are BUS_H high (sky at BUS_H)."""
    y2 = y - face * deep
    m.sector(rect4(x, min(y, y2), x + 800, max(y, y2)), floor=floor, ceil=floor + BUS_H,
             **dict(dict(light=170, wall=f"AJ{livery}US", ctex="F_SKY1"), **ground))
    mouths, slots = [], list(slots)
    for k in range(11):                    # eleven pieces of 64 between the two ends: a door's place and a panel by turns
        a = (x + 48 + 64 * k, y)
        b = (a[0] + 64, y)
        m.cut(a, b)
        if k % 2 == 0 and k // 2 in slots:
            m.line(a, b, upper=f"AJ{livery}N{first + slots.index(k // 2)}")
        else:                              # no two panels alike side by side (gfx_bus: AJ?US, AJ?US1..4)
            v = (k * 3 + (2 if face < 0 else 0) + first) % 5
            m.line(a, b, mid=f"AJ{livery}US{v or ''}")
    for k in slots:
        mouths.append(((x + 48 + 128 * k, y), (x + 112 + 128 * k, y)))
    # an end's texture has the bus's corner on its left (Z) or its right (Y), as it is looked at
    ends = [((x, y), (x + 48, y), "Z" if face > 0 else "Y"), ((x + 752, y), (x + 800, y), "Y" if face > 0 else "Z")]
    for a, b, end in ends:
        m.line(a, b, mid=f"AJ{livery}US{end}")
    if not free:
        for a, b in (((x, y), (x, y2)), ((x + 800, y), (x + 800, y2))):
            m.line(a, b, mid=f"AJ{livery}USZ")
    return mouths


def bus_ends(m, x, y, livery="B"):
    """The front (west) and the back (east) of a free-standing bus whose two
    faces are bus(x, y, face=1) and bus(x, y + BUS_H, face=-1): 144 wide."""
    for xx, tex in ((x, f"AJ{livery}USF"), (x + 800, f"AJ{livery}USR")):
        m.cut((xx, y), (xx, y + 144))
        m.line((xx, y), (xx, y + 144), mid=tex)


def rect4(x1, y1, x2, y2):
    return [(x1, y1), (x1, y2), (x2, y2), (x2, y1)]


def route_board(m, a, lamps, *, step=(0, 16)):
    """The route board of a bus stop (MAP10): a row of lamps on a wall, one
    for each door of the bus, starting at `a` and going on by `step` (16
    along the wall) for each. A lamp is (number, what): what is a frame's
    line id (the lamp shows the colour of the door that hangs there), a
    colour whose far side is that door of the bus (lit while that door
    hangs somewhere), or None for a line that always runs. The wall must be
    128 high there (a porch). AjarHandler.BoardTick lights them."""
    for i, (n, what) in enumerate(lamps):
        p = (a[0] + step[0] * i, a[1] + step[1] * i)
        q = (p[0] + step[0], p[1] + step[1])
        m.cut(p, q)
        if what is None:
            m.line(p, q, mid=f"AJR{n}7")
        else:
            m.line(p, q, mid=f"AJR{n}0", id=600 + what if what >= 100 else 800 + what)


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


def roomdoor(m, a, b, out, floor, *, thick=16, keys="", line_id=0, look="", skin="", free_inside=False):
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
    door texture, to which the keys of a locked door are added.
    `free_inside`: a locked door needs no key from the side `out` points to
    (MAP09's east wing, which can be come into another way: nobody is locked
    in). In a PUZZLE graph the walk link out of there has no key."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor, ceil=floor, light=160, wall=skin + keys if skin else (f"AJ2K{look}{keys}" if keys else f"AJ2D{look}") if look else f"AJHK{keys}" if keys else "AJHDOR",
             ftex="AJTRIMF", ctex="AJTRIMF")
    for p, q in ((a, b), (c, d)):
        if keys and not (free_inside and p == c):
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


def room(m, xs, ys, runner, *, ceil, light, rug="AJRUG", lite="AJLITE", lift=16, strip=None, **base):
    """A flat rectangular room cut into a grid by the lists xs and ys. Cells
    for which runner(i, j) is true (column i, row j) are a strip of carpet
    under a raised row of ceiling lights; use it to lead from door to door.
    `rug` is the carpet's flat; `strip`, more sector properties for the
    carpet's cells only (a secret: special=1024)."""
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cell = [(xs[i], ys[j]), (xs[i], ys[j + 1]), (xs[i + 1], ys[j + 1]), (xs[i + 1], ys[j])]
            if runner(i, j):
                m.sector(cell, ceil=ceil + lift, lift=lift, light=min(255, light + 30),
                         **dict(base, ftex=rug, ctex=lite, **(strip or {})))
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


BELT_W, CURB_W, CURB_H = 64, 16, 16     # a belt is a door wide; its curbs
BELT_SPEED = 8      # Scroll_Floor's speed in units a tic (what rides it goes a little slower: PLAN.md, "The belt lab")
BELT_TAG = 900      # 900 + n: the sectors of one belt (one direction), see belt()


def belt(m, a, b, tag, *, floor=0, speed=BELT_SPEED, scroll=True, curbs=(True, True), light=200, color=None):
    """A straight run of conveyor belt (a scrolling floor that carries what
    stands on it) from a to b, the middles of its two ends; a-b runs along x
    or y and the belt carries from a towards b. It is BELT_W wide, with a
    curb CURB_W wide and CURB_H high on either side (`curbs`: left, right,
    looking from a to b) that a carried crate cannot climb and the player
    steps over. Every sector with `tag` carries the same way: give the
    recesses at its ends the tag too (recess(tag=)), so that the belt runs
    right up to a portal line and starts right at one. `scroll`: this call
    puts the Scroll_Floor line for the tag (one per tag, or it carries twice
    as fast); further runs in the same direction pass scroll=False."""
    d = ((b[0] > a[0]) - (b[0] < a[0]), (b[1] > a[1]) - (b[1] < a[1]))
    assert abs(d[0]) + abs(d[1]) == 1, "a belt runs along x or y"
    n = (-d[1], d[0])                                          # to the left
    def at(p, s):
        return (p[0] + n[0] * s, p[1] + n[1] * s)
    h = BELT_W // 2
    m.sector([at(a, h), at(b, h), at(b, -h), at(a, -h)], floor=floor, ftex="FLAT20", light=light, color=color, id=tag)
    for side, s in ((0, 1), (1, -1)):
        if curbs[side]:
            m.sector([at(a, s * h), at(b, s * h), at(b, s * (h + CURB_W)), at(a, s * (h + CURB_W))],
                     floor=floor + CURB_H, ftex="STEP1", side="METAL", light=light, color=color)
    if scroll:
        # Scroll_Floor(tag, no control sector, the texture and what stands on it, x, y): speeds are 128 + 32 a unit
        p, q = at(a, h), at((a[0] + d[0] * 8, a[1] + d[1] * 8), h)
        m.cut(p, q)
        m.line(p, q, special=223, args=(tag, 0, 2, 128 + 32 * speed * d[0], 128 + 32 * speed * d[1]), exact=True)


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


def lever(m, a, b, seconds, *, line_id=0, tex="AJLEVR"):
    """The lever of the level's shutter(), on the 64-long wall piece a-b:
    USE sends the shutter up for `seconds`."""
    m.cut(a, b)
    m.line(a, b, special=12, args=(SHUTTER, 64, seconds * 35), playeruse=True, repeatspecial=True,
           mid=tex, exact=True, id=line_id)


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


def _on(key, a, b):
    """Whether the edge a-b lies on the line `key` (a frozenset of two points)."""
    p1, p2 = tuple(key)
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    for v in (a, b):
        px, py = v[0] - p1[0], v[1] - p1[1]
        if dx * py - dy * px != 0 or not 0 <= (px * dx + py * dy) / (dx * dx + dy * dy) <= 1:
            return False
    return True


BOARDED = {}        # a door's face -> the same nailed up (gfx.boarded), wherever an excerpt() ends at a door
SCENERY_T = {34, 35, 2028, 85, 86, 44, 45, 46, 55, 56, 57, 48, 70} | set(range(20021, 20030))   # what only stands there
SCENERY_T |= {20098}  # MAP17's checker lamps (map17.zs)


def boarded(face):
    """The name of the door texture `face` with boards nailed across it."""
    return BOARDED.setdefault(face, "AJNB%02d" % len(BOARDED))


def excerpt(m, src, at, dx, dy, *, things=True, small=100000, without=()):
    """A piece of another level, as it stands there (Vadim, 2026-11-17: the
    places MAP10's bus goes to are the earlier levels, and should read so):
    everything of the Map `src` that can be walked to and back from the
    point `at` without a door that is carried, moved by dx, dy (multiples
    of 64: wall textures are laid by where they are), with its furniture,
    its windows, its ordinary doors, its monsters and what lies about.

    What is left behind: every frame and far side (their recesses are plain
    wall again), locked and bolted doors, exits, keys, Ajar's own monsters,
    secrets, and whatever is only dropped into or come to through a door.
    What comes along as scenery (Vadim, 2026-11-17: the pieces are to look
    as they do in their levels): whatever is seen from there and stands
    higher than anybody climbs (a balcony, a gallery, a stage, a bridge),
    and on from it for as long as the floor does not go down (and one
    small piece further where it does: a trap in a stage), with the lamps
    and such that stand on it. Nobody gets there: every step from
    the ground to a piece of scenery is more than 24. `without` is boxes
    (x1, y1, x2, y2) of the new map that the caller builds in: scenery
    that reaches into one stays behind.

    Where the excerpt ends at a door that does not come along (locked,
    bolted), the wall shows that door nailed up (boarded()); where it ends
    at anything else, the room's own wall.

    Returns the places where a recess was, [(m1, m2, out, floor), ...] in
    the new map, in the order `src` made them: the caller may make recesses
    of its own in them (the far end of a doorway(), a stray_place())."""
    polys, S = src._split(), src.sectors

    def props(a, b):
        p = src.lineprops.get(frozenset((a, b)))
        if p is None:
            p = next((v for k, v in src.lineprops.items() if _on(k, a, b)), {})
        return p

    def area(p):
        return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(p, p[1:] + p[:1]))) / 2

    def inside(x, y, p):
        hit = False
        for a, b in zip(p, p[1:] + p[:1]):
            if (a[1] > y) != (b[1] > y) and x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
                hit = not hit
        return hit

    edge = {(a, b): si for si, p in enumerate(polys) for a, b in zip(p, p[1:] + p[:1])}
    portal, doors, order = set(), set(), []
    for (a, b), si in edge.items():
        special = props(a, b).get("special")
        if special == 156 and si not in portal:
            order.append(si)
        if special == 156:
            portal |= {si, edge.get((b, a), si)}
        if special == 12 and S[si]["floor"] == S[si]["ceil"]:
            doors.add(si)
    walk = {i: set() for i in range(len(S))}       # both ways on foot
    near = {i: set() for i in range(len(S))}       # sharing a line
    see = {i: set() for i in range(len(S))}        # sharing a line with a gap over it
    for (a, b), si in edge.items():
        sj = edge.get((b, a))
        if sj is None or si in portal or sj in portal:
            continue
        near[si].add(sj)
        s, o = S[si], S[sj]
        if min(s["ceil"], o["ceil"]) > max(s["floor"], o["floor"]):
            see[si].add(sj)
        top = lambda x, i: x["floor"] + DOOR_H if i in doors else x["ceil"]
        if (not props(a, b).get("blocking") and abs(o["floor"] - s["floor"]) <= 24
                and min(top(s, si), top(o, sj)) - max(s["floor"], o["floor"]) >= 56):
            walk[si].add(sj)

    def spread(start, links, ok=lambda i: True):
        seen, todo = set(start), list(start)
        while todo:
            for j in links[todo.pop()]:
                if j not in seen and ok(j):
                    seen.add(j)
                    todo.append(j)
        return seen

    first = next(i for i, p in enumerate(polys) if i not in portal and inside(at[0], at[1], p))
    ground = spread([first], walk)
    # furniture, sills, what is seen through a window: whatever touches the
    # ground and is not somewhere to fall into, or a room of its own
    size = {}
    def fits(j):
        if j in portal or (S[j]["floor"] == S[j]["ceil"] and j not in doors):
            return False
        if j not in size:
            whole = spread([j], walk)
            size.update((k, sum(area(polys[k]) for k in whole)) for k in whole)
        low = min(S[k]["floor"] for k in near[j] if k in keep) if any(k in keep for k in near[j]) else S[j]["floor"]
        return size[j] < small and (S[j]["floor"] >= low or S[j]["ceil"] - S[j]["floor"] < 56)
    keep = set(ground)
    keep = spread(list(keep), near, fits)

    move = lambda v: (v[0] + dx, v[1] + dy)

    def clear(j):                                  # of the caller's own building
        xs, ys = [v[0] + dx for v in polys[j]], [v[1] + dy for v in polys[j]]
        return not any(min(xs) < x2 and max(xs) > x1 and min(ys) < y2 and max(ys) > y1 for x1, y1, x2, y2 in without)

    # scenery: seen from the ground and out of reach. A rectangle of it that
    # reaches into a `without` box comes along with that box cut out of it.
    scenery, part, todo = set(), set(), list(keep)
    while todo:
        i = todo.pop()
        for j in see[i]:
            if j in keep or j in scenery or j in portal:
                continue
            if not clear(j) and (len(src.polys[j]) != 4 or len({v[0] for v in src.polys[j]}) != 2):
                continue
            if S[j]["floor"] > S[i]["floor"] + 24 if i in keep else S[j]["floor"] >= S[i]["floor"]:
                scenery.add(j)
                todo.append(j)
            elif i not in keep and area(polys[j]) < small:     # a hole in it (a trap in a stage): no further
                scenery.add(j)
    while True:                                    # ... and nowhere a step or a drop away from it
        low = {j for j in scenery if any(g in ground and S[j]["floor"] <= S[g]["floor"] + 24 for g in near[j])}
        if not low:
            break
        scenery -= low
    part = {j for j in scenery if not clear(j)}
    scenery -= part
    keep |= scenery

    for i in sorted(keep):
        m.polys.append([move(v) for v in polys[i]])
        m.sectors.append(dict(S[i], id=0, special=0))
    for j in sorted(part):
        xs, ys = [v[0] + dx for v in src.polys[j]], [v[1] + dy for v in src.polys[j]]
        rects = [(min(xs), min(ys), max(xs), max(ys))]
        for x1, y1, x2, y2 in without:
            cut = []
            for a1, b1, a2, b2 in rects:
                if not (a1 < x2 and a2 > x1 and b1 < y2 and b2 > y1):
                    cut.append((a1, b1, a2, b2))
                    continue
                lo, hi = max(b1, y1), min(b2, y2)
                cut += [(a1, b1, a2, lo), (a1, hi, a2, b2), (a1, lo, max(a1, x1), hi), (min(a2, x2), lo, a2, hi)]
            rects = [r for r in cut if r[0] < r[2] and r[1] < r[3]]
        for r in rects:
            m.polys.append(rect4(*r))
            m.sectors.append(dict(S[j], id=0, special=0))
    for key, val in src.lineprops.items():
        p = dict(val)
        p.pop("id", None)
        if p.get("special") not in (None, 9, 12):
            p = {k: p[k] for k in ("blocking", "mid", "midboth") if p.get("blocking") and k in p}
        if "fit" in p:
            p["fit"] = (move(p["fit"][0]), p["fit"][1])
        if p:
            m.lineprops[frozenset(move(v) for v in key)] = p
    m.cuts |= {move(v) for v in src.cuts}
    m.align |= src.align
    # Where the excerpt ends. A door that stays behind is seen shut: nailed up
    # where anybody can come to it, as it is where nobody can. Anywhere else
    # the room's own wall, not what hung on the line (a railing).
    shut = set()
    for sj, P in enumerate(src.polys):
        if sj in keep or sj in part or sj in portal or S[sj]["floor"] != S[sj]["ceil"]:
            continue
        for A, B in zip(P, P[1:] + P[:1]):
            pieces = [(a, b) for a, b in zip(polys[sj], polys[sj][1:] + polys[sj][:1]) if _on(frozenset((A, B)), a, b)]
            rooms = {edge.get((b, a)) for a, b in pieces}
            if abs(A[0] - B[0]) + abs(A[1] - B[1]) != 64 or not rooms <= keep or any(S[k]["floor"] != S[sj]["floor"] for k in rooms):
                continue
            face = props(A, B).get("upper") or S[sj]["wall"]
            m.cut(move(A), move(B))
            m.lineprops[frozenset((move(A), move(B)))] = dict(mid=boarded(face) if rooms & ground else face,
                                                              dontpegbottom=True, exact=True)
            shut |= {(b, a) for a, b in pieces}
    for i in sorted(keep):
        for a, b in zip(polys[i], polys[i][1:] + polys[i][:1]):
            sj = edge.get((b, a))
            if sj is None or sj in keep or sj in part or (a, b) in shut:
                continue
            m.cut(move(a), move(b))
            m.lineprops[frozenset((move(a), move(b)))] = {}
    if things:
        for t in src.things:
            if t["type"] in (1, 2, 3, 4, 11) or 20001 <= t["type"] <= 20014 or t["type"] == AMBUSH_T:
                continue
            if any(inside(t["x"], t["y"], polys[i]) for i in ground) or (
                    t["type"] in SCENERY_T and any(inside(t["x"], t["y"], polys[i]) for i in keep - ground)):
                m.things.append(dict(t, x=t["x"] + dx, y=t["y"] + dy))
    places = []
    for si in order:                               # a recess: the sector on the room's side of a portal line
        for a, b in zip(polys[si], polys[si][1:] + polys[si][:1]):
            sj = edge.get((b, a))
            if sj in ground:
                mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
                cx = sum(v[0] for v in polys[si]) / len(polys[si])
                cy = sum(v[1] for v in polys[si]) / len(polys[si])
                out = ((cx > mx) - (cx < mx), (cy > my) - (cy < my))
                places.append((move(a), move(b), out, S[si]["floor"]))
    return places
