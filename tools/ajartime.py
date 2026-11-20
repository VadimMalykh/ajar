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
    if mix:
        m.mix_fights = getattr(m, "mix_fights", set()) | {k}         # for fight_anew_reached()


def hall_door(m, k, j, a, b, out, floor, *, out_only=False, **look):
    """Time door j of hall k: a-b is its 64-wide mouth. `out_only`: the
    player goes out by it as by any (and an earlier self that went out by it
    goes out by it again), but the next go's box opens onto the hall's time
    door 1, not onto this one (time.zs: args[4] 1 on the portal line)."""
    ajarmap.recess(m, a, b, out, floor, hall_line(k, j), box_line(k, 1), far_colour=TIME, **look)
    if out_only:
        d = ajarmap.DEPTH
        m.line((a[0] + out[0] * d, a[1] + out[1] * d), (b[0] + out[0] * d, b[1] + out[1] * d),
               args=(box_line(k, 1), 0, 1, 1, 1))


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


def cue(m, k, wave, when, kind, *spots, angle=0, always=False, calm=False):
    """Monsters of Doom editor number `kind` that come into fight k at
    `spots`, as wave number `wave`, once no more than `when` are left. A
    hall with a show starts empty: its first monsters are wave 1, when 0.
    `always`: on every difficulty (what a fight is remembered by). `calm`:
    they never fight each other (NOINFIGHTING; time.zs, Calm)."""
    for x, y in spots:
        i = m.cues = getattr(m, "cues", -1) + 1         # thinned on the easier difficulties, as ajarmap.ambush
        m.thing(x, y, CUE_T, angle=angle, args=(k, wave, when, kind, int(calm)),
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


GRAPHS = {}         # on_foot()'s rooms, by name: (regions, links)


def anew(m, x, y, angle, z=30):
    """A plate on a wall of a room of goes' box, facing `angle`: USE forgets
    every go (plate.zs, AjarAnew)."""
    m.thing(x, y, ANEW_T, angle=angle, height=float(z))


# --- the third goes lab (map SHUT, tools/map_shut.py; src/zscript/shut.zs) -------
SHUTTER_T = 20049
FIGURE_T = 20051
SHUT_HIGH = 96          # how high a shutter opens, over its floor


def shutter(m, a, b, out, floor, tag, *, high=SHUT_HIGH, thick=16, keep=False, behind=False, under=0,
            nomonsters=False, screen=False, color=None):
    """A shutter in a wall: a-b is its face on the side it is worked from
    (where whoever is in its way is put when it shuts), `out` points through
    it to the other side. It is a sector `thick` deep (tag `tag`) whose
    ceiling is at its floor while it is shut, and `high` over it while it is
    open: open only while a plate that names it is pressed (shutter_plate;
    shut.zs, AjarShutter). Declare the places on both sides first. `keep`:
    nothing walks between the shutter and the far side, open or shut (a pen:
    the line there is impassable to players and monsters, but shots and
    sight pass it, so what is penned fights through the open shutter).
    `behind`: the sector right behind it is a booth whose only way out it
    is: a player in the booth when it shuts is put out, as one in its way
    is (shut.zs, AjarShutter args[2]). `under`: a sector tag (a press's);
    the shutter is open also while the player or an earlier self is in a
    sector with that tag (AjarShutter args[3]; with no plate, only then).
    `nomonsters`: no monster walks or flies past its face a-b (players,
    shots and sight do). `screen`: the reverse, a SCREEN, shut while it is
    held and open otherwise (built open; AjarShutter args[4] 1). Returns its
    sector."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    si = m.sector([a, b, d, c], floor=floor, ceil=floor + high if screen else floor, light=170, wall="AJSHUT",
                  ftex="AJTRIMF", ctex="AJTRIMF", id=tag, color=color)
    if keep:
        m.line(c, d, blocking=True)
    for p, q in ((a, c), (b, d)):
        m.line(p, q, mid="AJTRIM", dontpegbottom=True)
    if nomonsters:
        m.line(a, b, blockmonsters=True)
    ang = {(0, 1): 270, (0, -1): 90, (1, 0): 180, (-1, 0): 0}[tuple(out)]
    m.thing((a[0] + d[0]) / 2, (a[1] + d[1]) / 2, SHUTTER_T, angle=ang, args=(tag, high, int(behind), under, int(screen)))
    return si


SHUT_LAMP_T = 20053


def shut_lamp(m, x, y, angle, tag, z=72):
    """A lamp on the wall beside the shutter of `tag`, facing `angle`, `z`
    over the floor: green while it is wholly worked (a shutter open, a
    screen shut), amber while an earlier self holds it or is about to, red
    otherwise (shut.zs, AjarShutLamp). Stand it 2 off the wall."""
    m.thing(x, y, SHUT_LAMP_T, angle=angle, height=float(z), args=(tag,))


PRESS_LAMP_T = 20054
SENTRY_T = 20055


def press_lamp(m, x, y, angle, tag, z=72):
    """A lamp on a wall for the press of `tag`, facing `angle`: red while the
    press is not up and ready, amber while an earlier self's pull of it is
    about to come, green otherwise (shut.zs, AjarPressLamp). Stand it 2 off
    the wall."""
    m.thing(x, y, PRESS_LAMP_T, angle=angle, height=float(z), args=(tag,))


def sentries(m, x, y, fight, pen_tag, trip_tag):
    """Fight `fight`'s monsters on the demo that stand in a sector of
    `pen_tag` wake while the player stands in a sector of `trip_tag` (time.zs,
    AjarSentry). x, y anywhere."""
    m.thing(x, y, SENTRY_T, args=(fight, pen_tag, trip_tag))


def seen(spaces, p, q):
    """Is the point q (x, y, z) seen from p, through `spaces`, a list of
    (x1, y1, x2, y2, floor, ceil) that tile the rooms between them? Sight in
    2.5D as the engine has it: every piece of the line lies in a space, and
    between its floor and its ceiling where it enters and leaves it."""
    xs = {v for s in spaces for v in (s[0], s[2])}
    ys = {v for s in spaces for v in (s[1], s[3])}
    ts = {0.0, 1.0}
    for vs, i in ((xs, 0), (ys, 1)):
        d = q[i] - p[i]
        if d:
            ts |= {(v - p[i]) / d for v in vs if 0 < (v - p[i]) / d < 1}
    ts = sorted(ts)
    at = lambda t: tuple(p[i] + (q[i] - p[i]) * t for i in range(3))
    for a, b in zip(ts, ts[1:]):
        mx, my, _ = at((a + b) / 2)
        sp = [s for s in spaces if s[0] <= mx <= s[2] and s[1] <= my <= s[3]]
        if not sp:
            return False
        f, c = sp[0][4], sp[0][5]
        if not all(f < at(t)[2] < c for t in (a, b)):
            return False
    return True


def shutter_plate(m, x, y, tag, say=0):
    """A plate on the floor at x, y that holds the shutter of `tag` open
    while the player or an earlier self stands on it (an AjarPlate whose
    args[1] is the shutter's tag). `say` n: the first time the player steps
    on it, message n (shut.zs, PlateText)."""
    m.thing(x, y, PLATE_T, args=(0, tag, say))


FIGURES = {"me": 1, "body": 2, "plate": 3, "hung": 4, "leaning": 5, "lamp": 6, "walking": 7, "go": 8, "frame": 9,
           "plaque": 10, "lever": 11, "standing": 12, "dial": 13}
GO_OVER = 34        # how high a go's number floats over the floor under a self of scale 0.5


def figure(m, x, y, what, *, kind=0, angle=0, scale=None, z=0):
    """A still figure for a model of a puzzle solved (shut.zs, AjarFigure):
    `what` is "me" (the player standing), "walking" (the player mid-stride),
    "body" (a dead monster of Doom editor number `kind`, as it lies at the
    end of its death), "plate" (a floor plate, pressed, with a warm light),
    "hung" (a door of colour `kind` standing open, as in a frame),
    "leaning" (that door leaning), "lamp" (a clock lamp, ajartime.together,
    lit green: joined in time), "go" (the number `kind`, 1 to 3, of the go a
    self is, floating over its head: put it where the self stands), "frame"
    (a door frame's face, brass inlaid with colour `kind`, 0 plain: stand it
    against a wall and the "hung" door 2 in front of it), "plaque" (the
    clock plaque over a case, which case() puts there), "lever" (the
    press's switch, set off, on a wall: stand it against the wall),
    "standing" (a live monster of Doom editor number `kind`, standing: the
    first picture of its Spawn state) or "dial" (MAP16's weighbridge dial,
    its needle at the red mark and its lamp green: stand it against a
    wall). `scale` its size (by
    default 0.5; a plate 0.75, the plaque 1). Nothing about it is alive: not
    solid, not shot, never counted, never recorded and no weight on a plate.
    `z` over the floor (a go's number: over that, GO_OVER more)."""
    if scale is None:
        scale = {"plate": 0.75, "plaque": 1.0}.get(what, 0.5)
    if what == "go":
        z += GO_OVER
    m.thing(x, y, FIGURE_T, angle=angle, height=float(z),
            args=(FIGURES[what], kind, int(round(scale * 100))))


def case(m, a, b, out, floor, *, deep=96, raised=16, top=112, light=240, color=None, wall="AJWALL",
         ftex="AJFLOOR", ctex="AJCEIL", ceil=192, plaque=True, trim=None):
    """A glass case in a wall: a-b is its glass on the room's side (16
    thick, framed in the time door's ivory), `out` points from the room into
    it. Its floor is `raised` over `floor`. Inside, it is a piece of the room:
    `wall`, `ftex`, `ctex` the room's own textures (`color` its tint), lit
    `light`. Over the glass, between its head and the room's ceiling (`ceil`
    over `floor`; no more than 24 over the head), the clock plaque that says
    "later" (a figure). In a level with no time doors (MAP16): `plaque`
    False leaves the plaque out, and `trim` (texture, flat) frames the glass
    in the level's own trim instead of the ivory. Returns the
    case's sector, for sealed(). Put figures in it."""
    glass(m, a, b, out, floor, sill=raised, top=top, color=color, trim=trim or (f"AJTR{TIME}", f"AJTF{TIME}"))
    c = (a[0] + out[0] * 16, a[1] + out[1] * 16)
    d = (b[0] + out[0] * 16, b[1] + out[1] * 16)
    e = (d[0] + out[0] * deep, d[1] + out[1] * deep)
    f = (c[0] + out[0] * deep, c[1] + out[1] * deep)
    ang = {(0, 1): 270, (0, -1): 90, (1, 0): 180, (-1, 0): 0}[tuple(out)]
    if plaque:
        assert ceil - top >= 40, "no room for the plaque over the glass"
        figure(m, (a[0] + b[0]) / 2 - out[0] * 2, (a[1] + b[1]) / 2 - out[1] * 2, "plaque", angle=ang,
               z=min((top + ceil) / 2 - 16, top + 24))
    return m.sector([c, d, e, f], floor=floor + raised, ceil=floor + top, light=light, wall=wall,
                    ftex=ftex, ctex=ctex, color=color)


def sealed(m, si):
    """Can nothing walk into sector `si` (or out of it)? Every way out of it
    over a two-sided line that does not block leads only into it again."""
    import re
    text = m.textmap()
    sides = [int(s) for s in re.findall(r"sidedef\{[^}]*?sector=(\d+);", text)]
    seen, todo = {si}, [si]
    lines = re.findall(r"linedef\{([^}]*)\}", text)
    while todo:
        s = todo.pop()
        for ld in lines:
            if "sideback" not in ld or "blocking=true" in ld:
                continue
            f = sides[int(re.search(r"sidefront=(\d+);", ld).group(1))]
            k = sides[int(re.search(r"sideback=(\d+);", ld).group(1))]
            for p, q in ((f, k), (k, f)):
                if p == s and q not in seen:
                    seen.add(q)
                    todo.append(q)
    return seen == {si}


# --- MAP32 rebuilt (tools/map_secret2.py): checks a generator makes ---------------
RADIUS = {3004: 20, 9: 20, 65: 20, 3001: 20, 3002: 30, 58: 30, 3005: 31, 69: 24, 3003: 24, 66: 20, 64: 20, 67: 48,
          68: 64, 71: 31, 16: 40, 7: 128}
HEALTH = {3004: 20, 9: 30, 65: 70, 3001: 60, 3002: 150, 58: 150, 3005: 400, 69: 500, 3003: 1000, 66: 300, 64: 700,
          67: 600, 68: 500, 71: 400, 16: 4000, 7: 3000}


HEIGHT = {3004: 56, 9: 56, 65: 56, 3001: 56, 3002: 56, 58: 56, 3005: 56, 69: 64, 3003: 64, 66: 56, 64: 56, 67: 64,
          68: 64, 71: 56, 16: 110, 7: 100}


class Crowd:
    """The monsters of fight k, all AjarCues (cue()), and where they may
    stand: `floor` is a list of rectangles (x1, y1, x2, y2) a monster stands
    wholly inside one of, `solid` of those it may not touch (pillars). A
    monster must also stand clear of the others of its wave: one that has no
    room never comes, and the fight is never won (as map_shift's
    Shop.room_for). `bad` lists what has no room; the generator asserts it
    empty. `kinds` is every monster placed, for toughness(). `calm`: they
    never fight each other (cue())."""

    def __init__(self, m, k, floor, solid=(), calm=False):
        self.m, self.k, self.floor, self.solid, self.calm = m, k, list(floor), list(solid), calm
        self.placed, self.bad, self.kinds = {}, [], []

    def cue(self, wave, when, kind, *spots, **look):
        r = RADIUS[kind] + 8
        for x, y in spots:
            if not any(a + r <= x <= c - r and b + r <= y <= d - r for a, b, c, d in self.floor):
                self.bad.append((self.k, wave, kind, x, y, "wall"))
            for a, b, c, d in self.solid:
                if a - r < x < c + r and b - r < y < d + r:
                    self.bad.append((self.k, wave, kind, x, y, "pillar"))
            for ox, oy, orr in self.placed.setdefault(wave, []):
                if max(abs(x - ox), abs(y - oy)) < r - 8 + orr:
                    self.bad.append((self.k, wave, kind, x, y, "another", ox, oy))
            self.placed[wave].append((x, y, RADIUS[kind]))
            self.kinds.append(kind)
        cue(self.m, self.k, wave, when, kind, *spots, calm=self.calm, **look)


def toughness(kinds):
    """How much health a fight's monsters have between them."""
    return sum(HEALTH[k] for k in kinds)


# What a pick-up holds (a weapon: what comes with it), and what one round is
# worth on average against a monster: a rocket's hit and some of its blast, a
# plasma bolt, a shotgun's seven pellets, a bullet.
AMMO = {2046: ("rocket", 5), 2010: ("rocket", 1), 2003: ("rocket", 2), 17: ("cell", 100), 2047: ("cell", 20),
        2004: ("cell", 40), 2006: ("cell", 40), 2049: ("shell", 20), 2008: ("shell", 4), 2001: ("shell", 8),
        82: ("shell", 8), 2048: ("bullet", 50), 2007: ("bullet", 10), 2002: ("bullet", 20)}
ROUND = {"rocket": 150, "cell": 22, "shell": 70, "bullet": 10}


def firepower(kinds):
    """The damage the ammunition in `kinds` (Doom editor numbers) can do, on average."""
    return sum(AMMO[k][1] * ROUND[AMMO[k][0]] for k in kinds if k in AMMO)


def walk(*ps):
    """The length of a walk through the points ps."""
    return sum(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5 for a, b in zip(ps, ps[1:]))


def on_foot(name, regions, links, doors):
    """No dead end in a room of goes or a fight: from every region a player can
    stand in, a time door of the room is reached on foot, without an earlier
    self. `regions` {name: (x1, y1, x2, y2)}; `links` [(a, b)] a way on foot
    from a to b (a drop: one way), or (a, b, True) both ways; leave out every
    way that needs an earlier self (a sprung frame, a Pair joined in time).
    `doors` {region: [(x, y), ...]}: a point in the mouth of each time door
    (or a box's door, which leads to one), asserted to be in its region.
    Returns the regions, for covers()."""
    for r, pts in doors.items():
        x1, y1, x2, y2 = regions[r]
        for x, y in pts:
            assert x1 <= x <= x2 and y1 <= y <= y2, f"{name}: the door at {x, y} is not in {r}"
    GRAPHS[name] = (regions, links)          # for fight_anew_reached()
    nxt = {r: set() for r in regions}
    for a, b, *both in links:
        nxt[a].add(b)
        if both and both[0]:
            nxt[b].add(a)
    for r in regions:
        seen, todo = {r}, [r]
        while todo:
            for q in nxt[todo.pop()] - seen:
                seen.add(q)
                todo.append(q)
        assert seen & set(doors), f"{name}: no time door on foot from {r}"
    return regions


def covers(m, name, first, regions, *, zone, small=4096, exempt=()):
    """Every sector made since index `first` that lies in the room's `zone`
    (x1, y1, x2, y2) and is bigger than `small` is in one of the declared
    `regions`, unless it is `exempt` (a case, a pen): so that no part of the
    room is left out of on_foot()."""
    for si in range(first, len(m.polys)):
        if si in exempt:
            continue
        p = m.polys[si]
        area = abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(p, p[1:] + p[:1]))) / 2
        cx, cy = sum(q[0] for q in p) / len(p), sum(q[1] for q in p) / len(p)
        if area <= small or not (zone[0] <= cx <= zone[2] and zone[1] <= cy <= zone[3]):
            continue
        assert any(x1 <= cx <= x2 and y1 <= cy <= y2 for x1, y1, x2, y2 in regions.values()), \
            f"{name}: the sector at {cx, cy} is in no region"


# --- begin anew in a fight (src/zscript/anew.zs; PLAN.md, "Begin anew in a fight") ---
FIGHT_ANEW_T = 20052


def fight_anew(m, k, x, y, angle, z=16):
    """A big bright plate on a wall of fight k's hall (in its zone, by the way
    in), facing `angle`, its foot `z` over the floor (it is 56 high): USE puts
    the fight back as it was when the player first came in, and death after
    its last box does the same (anew.zs, AjarFightAnew). Stand it 2 off the
    wall. Recorded for fight_anew_reached()."""
    m.thing(x, y, FIGHT_ANEW_T, angle=angle, height=float(z))
    m.fight_anews = getattr(m, "fight_anews", {})
    m.fight_anews.setdefault(k, []).append((x, y))


def fight_anew_reached(m, rooms):
    """No dead end when a fight of goes' boxes are spent: every fight of goes
    (zone(mix=True)) has a begin-anew plate (fight_anew), and from every
    region of its room (as declared to on_foot, by name: `rooms` {fight:
    name}) the region the plate is in is reached on foot, without an earlier
    self."""
    mix = getattr(m, "mix_fights", set())
    plates = getattr(m, "fight_anews", {})
    assert set(rooms) == mix, f"fights of goes {sorted(mix)}, rooms given for {sorted(rooms)}"
    for k, name in rooms.items():
        assert plates.get(k), f"{name}: a fight of goes with no plate that begins it anew"
        regions, links = GRAPHS[name]
        nxt = {r: set() for r in regions}
        for a, b, *both in links:
            nxt[a].add(b)
            if both and both[0]:
                nxt[b].add(a)
        for x, y in plates[k]:
            at = [r for r, (x1, y1, x2, y2) in regions.items() if x1 <= x <= x2 and y1 <= y <= y2]
            assert at, f"{name}: the begin-anew plate at {x, y} is in no region"
            for r in regions:
                seen, todo = {r}, [r]
                while todo:
                    for q in nxt[todo.pop()] - seen:
                        seen.add(q)
                        todo.append(q)
                assert seen & set(at), f"{name}: the begin-anew plate is not reached on foot from {r}"
