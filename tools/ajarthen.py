"""Then and now: a place built twice (PLAN.md, "The then and now lab";
src/zscript/then.zs; the lab is tools/map_then.py).

Every room exists twice, NOW and THEN (forty years earlier): the same plan,
THEN shifted by a fixed offset (`Times(off=)`), so "the same spot at the
other time" is a point plus or minus the offset. NOW wears MAP11's look 3
(Post Box: flaking, dim), THEN look 2 (Thaw: white, bright).

    t = Times(m)                         # puts the AjarThen thing that names the offset
    t.room((x1, y1, x2, y2), wall=LA, ftex=FA, ctex=KA, then=dict(light=230))
    t.both(lambda c: c.room(...) if c.now else ...)   # any description, run once per copy
    t.frame(a, b, out, 101)             # frame 101 NOW, 101 + THEN_ID THEN: twins

A Copy (t.now, t.then) puts things in its own time: points are given in NOW's
coordinates and shifted; a texture given as a Part (LA, FA, ... below, or
Part("XX")) is MAP11's texture of that part in the copy's look; light is the
copy's unless given. Per-copy differences: `now=` and `then=` (dicts that
override the common properties, or False: not in that copy), or `only=NOW`.

The clocked door (colour CLOCKED): clocked() puts the door and its other leaf
(the shadow, never seen leaning: it hangs in the twin frame whenever the door
hangs). Long causes: cause() is a fixture THEN with 2 or 3 settings, worked
by lever() (live THEN, dead NOW) and target(); the NOW sectors it moves carry
their heights per setting (heights()); the THEN pieces that show it are
beam() and belt_run(). A frame with no twin (frame(only=)) does not take the
clocked door.

A colour door joins places, never times (2026-11-26): far() builds its far
side at both times (line id far_id NOW, + THEN_ID THEN), and the door opens
on the copy at the time of the frame it hangs in.

Three times (the three times lab, tools/map_before.py; PLAN.md, "The three
times lab"): Times(before=True) builds a third copy, BEFORE, ten years before
THEN, at NOW + 2 x the offset, in MAP11's look 1 (bright). A frame n NOW is
n + THEN_ID THEN and n + 2 x THEN_ID BEFORE; a colour door's far side the
same. `before=` beside `now=` and `then=`; `only=` one time or several
(only=(THEN, BEFORE)). The ten-year door (colour TENYEAR, ten_year()) joins a
frame THEN to its twin BEFORE as the clocked door joins NOW and THEN. A cause
BEFORE (cause(when=BEFORE), its lever() and target() BEFORE too) moves every
sector with its tag, THEN and NOW (and BEFORE: what shows it). check_ids()
says whether a map's frames and far sides keep clear of each other and of the
ids the engine reserves.
"""
import ajarmap
from udmf import rect

CLOCKED = 10        # the clocked door's colour (AjarDoor.CLOCKED)
TENYEAR = 11        # the ten-year door's (AjarDoor.TENYEAR): THEN to BEFORE
SHADOW = 3          # AjarDoor args[3] of its other leaf
NOW, THEN, BEFORE = 0, 1, 2
LOOK = {NOW: 3, THEN: 2, BEFORE: 1}         # MAP11's looks: 3 Post Box, 2 Thaw, 1 (the third time's, bright)
LIGHT = {NOW: 120, THEN: 216, BEFORE: 240}
THEN_ID = 20        # a THEN frame's line id: its NOW twin's + THEN_ID
OFF = (0, 4096)     # THEN is NOW shifted by this
THEN_T, CAUSE_T, TARGET_T, EMITTER_T, BELT_T, MUSIC_T = 20180, 20181, 20182, 20183, 20184, 20185
HIDDEN = 1000       # a thing with tid HIDDEN + a cause's tid is there only in its setting 0 (in a pit the heap covers)
LEVER = {NOW: "AJTHD3", THEN: "AJTHL2"}     # a cause's lever: dead NOW, live THEN (tools/gfx_then.py)
LIVE = {NOW: "AJTHL3", THEN: "AJTHL2", BEFORE: "AJTHL1"}     # a lever that works at every time (a gate's)
DEAD = {NOW: "AJTHD3", THEN: "AJTHD2"}      # where a cause's lever was, at a later time (tools/gfx_before.py)


class Part(str):
    """A texture named by its part in MAP11's looks (gfx_institute): each copy
    puts its own look's."""


LB, CO, LA, AR = Part("LB"), Part("CO"), Part("LA"), Part("AR")     # walls
FL, FC, FA, FR = Part("FL"), Part("FC"), Part("FA"), Part("FR")     # floors
KL, KC, KA = Part("KL"), Part("KC"), Part("KA")                     # ceilings


def heights(floors=None, ceils=None, hold=False, raised=None):
    """UDMF fields (a sector's raw=) for a NOW sector moved by a cause: its
    floor and/or ceiling in each setting (0, 1, 2). `hold`: its ceiling does
    not come down while anything stands in it, and the cause's openings wait
    for it (a hole). `raised`: the flat its floor shows while it stands
    higher than in setting 0 (a crate's lid on a heap that was never there)."""
    raw = {"user_raised": raised} if raised else {}
    if floors is not None:
        raw["user_floors"] = 1
        raw.update((f"user_f{i}", v) for i, v in enumerate(floors))
    if ceils is not None:
        raw["user_ceils"] = 1
        raw.update((f"user_c{i}", v) for i, v in enumerate(ceils))
    if hold:
        raw["user_hold"] = 1
    return raw


class Copy:
    def __init__(self, times, when):
        self.m, self.times, self.when = times.m, times, when
        self.now, self.then, self.before = when == NOW, when == THEN, when == BEFORE
        self.dx, self.dy = times.off[0] * when, times.off[1] * when
        self.look, self.light = LOOK[when], times.light[when]

    def P(self, p):
        return (p[0] + self.dx, p[1] + self.dy)

    def tex(self, v):
        return f"AJI{v}{self.look}" if isinstance(v, Part) else v

    def _dress(self, k, keys=("wall", "ftex", "ctex", "side", "mid", "upper", "lower")):
        return {key: self.tex(v) if key in keys else v for key, v in k.items()}

    def sector(self, poly, **k):
        k.setdefault("light", self.light)
        return self.m.sector([self.P(p) for p in poly], **self._dress(k))

    def room(self, box, **k):
        return self.sector(rect(*box), **k)

    def line(self, a, b, **k):
        self.m.line(self.P(a), self.P(b), **self._dress(k))

    def cut(self, *pts):
        self.m.cut(*(self.P(p) for p in pts))

    def thing(self, x, y, type, **k):
        x, y = self.P((x, y))
        self.m.thing(x, y, type, **k)

    def fid(self, n):
        """A frame's line id in this copy."""
        return n + THEN_ID * self.when

    def frame(self, a, b, out, n, floor=0, twin=True, target=None, **k):
        """Frame n (n + THEN_ID THEN, n + 2 x THEN_ID BEFORE); its portal is
        emptied at load, so any line id does as the dummy target: its twin's
        (`target`: another, for a frame that has no copy at that time). `twin`
        False: a frame in this copy alone, line id n whichever copy."""
        fid = self.fid(n) if twin else n
        self.times.used(fid, f"frame {n}")
        ajarmap.recess(self.m, self.P(a), self.P(b), out, floor, fid,
                       (target or (n if self.then else n + THEN_ID)) if twin else n, **k)

    def far(self, a, b, out, colour, floor=0, target=None, **k):
        """A plain door's far side, in this copy only (`target`: any frame's
        line id), line id far_id(colour) whichever copy. Against the rule
        since 2026-11-26 (PLAN.md, "Colour doors join places, never times"):
        a far side is built at both times, Times.far. No map uses it since
        MAP21 followed (2026-11-26)."""
        ajarmap.recess(self.m, self.P(a), self.P(b), out, floor, ajarmap.far_id(colour), target,
                       far_colour=colour, **k)

    def opening(self, a, b, out, floor=0, **k):
        ajarmap.opening(self.m, self.P(a), self.P(b), out, floor, **k)

    def far_line(self, colour):
        """The line id of a colour's far side in this copy (Times.far):
        far_id(colour) NOW, + THEN_ID THEN, + 2 x THEN_ID BEFORE (then.zs,
        AjarHandler.FarAt)."""
        return ajarmap.far_id(colour) + THEN_ID * self.when


class Times:
    def __init__(self, m, off=OFF, at=(0, 0), light=None, before=False):
        """`at`: a point of NOW (the AjarThen thing): a point is THEN if it
        lies more than half the offset from it, along the offset. `before`:
        a third copy, BEFORE, at twice the offset (args[2] of the AjarThen
        thing 3: a point past one and a half offsets is BEFORE)."""
        self.m, self.off = m, off
        self.light = dict(LIGHT, **(light or {}))
        self.now, self.then = Copy(self, NOW), Copy(self, THEN)
        self.before = Copy(self, BEFORE) if before else None
        self.copies = (self.now, self.then) + ((self.before,) if before else ())
        self.ids = {}                   # the frames' and far sides' line ids: what each is (check_ids)
        m.thing(at[0], at[1], THEN_T, args=off + ((3,) if before else ()))

    def used(self, line_id, what):
        """A frame's or far side's line id, kept for check_ids(); one used twice stops the build."""
        assert line_id not in self.ids, f"line id {line_id}: {self.ids[line_id]} and {what}"
        self.ids[line_id] = what

    def _each(self, now, then, before=None, only=None):
        """The copies a description is built in, each with its own differences:
        `only` one time (NOW, THEN, BEFORE) or several, and a copy's dict False
        leaves it out too."""
        for c in self.copies:
            extra = (now, then, before)[c.when]
            if extra is not False and (only is None or c.when in (only if isinstance(only, tuple) else (only,))):
                yield c, extra or {}

    def both(self, build):
        """Runs build(copy) for NOW, then for THEN (and BEFORE, if there is one)."""
        for c in self.copies:
            build(c)

    def sector(self, poly, *, now=None, then=None, before=None, only=None, **k):
        return [c.sector(poly, **dict(k, **extra)) for c, extra in self._each(now, then, before, only)]

    def room(self, box, *, now=None, then=None, before=None, only=None, **k):
        return self.sector(rect(*box), now=now, then=then, before=before, only=only, **k)

    def line(self, a, b, *, now=None, then=None, before=None, only=None, **k):
        for c, extra in self._each(now, then, before, only):
            c.line(a, b, **dict(k, **extra))

    def cut(self, *pts, only=None):
        for c, _ in self._each(None, None, None, only):
            c.cut(*pts)

    def frame(self, a, b, out, n, floor=0, *, only=None, now=None, then=None, before=None, **k):
        """A twinned frame: n NOW, n + THEN_ID THEN (and n + 2 x THEN_ID
        BEFORE). With `only` one time (NOW, THEN or BEFORE) a frame in that
        copy alone, line id n, with no twin: it does not take the clocked
        door. With `only` several times, a frame at each of those, twinned."""
        alone = only is not None and not isinstance(only, tuple)
        made = [c.when for c, _ in self._each(now, then, before, only)]
        for c, extra in self._each(now, then, before, only):
            other = [w for w in made if w != c.when]          # the dummy target: THEN's copy, or NOW's for THEN
            target = None if alone or not other else n + THEN_ID * (THEN if THEN in other else other[0])
            c.frame(a, b, out, n, floor, twin=not alone, target=target, **dict(k, **extra))

    def opening(self, a, b, out, floor=0, *, only=None, **k):
        for c, _ in self._each(None, None, None, only):
            c.opening(a, b, out, floor, **k)

    def far(self, a, b, out, colour, floor=0, target=None, *, now=None, then=None, before=None, **k):
        """A colour door's far side at every time, the same spot (Vadim,
        2026-11-26: a colour door joins places, never times). Line id
        far_id(colour) NOW, + THEN_ID THEN, + 2 x THEN_ID BEFORE
        (Copy.far_line). Hung in a frame NOW the door opens on the copy NOW,
        hung in a frame THEN (a twin's or one with no twin) on the copy THEN,
        BEFORE on BEFORE's; the other copies stay shut. `target`: any portal
        line id as the dummy target (default: the copy THEN's, or NOW's for
        THEN). `now=`, `then=`, `before=`: per-copy differences, as room()."""
        for c, extra in self._each(now, then, before):
            other = self.copies[0 if c.then else 1]
            self.used(c.far_line(colour), f"far side {colour}")
            ajarmap.recess(self.m, c.P(a), c.P(b), out, floor, c.far_line(colour),
                           target or other.far_line(colour), far_colour=colour, **dict(k, **extra))

    # --- the clocked door ------------------------------------------------------------------------
    def clocked(self, x, y, angle=0, *, frame=0, n=0, when=NOW):
        """The clocked door leaning at x, y (in the copy `when`), or hung in
        frame `frame` (that copy's line id); `n` numbers it if a map has
        more than one. Its shadow is the second AjarDoor, the same pair
        number (args[4] 100 + n)."""
        c = self.copies[when]
        c.thing(x, y, ajarmap.DOOR_T, angle=angle, args=(0, CLOCKED, frame, 0, 100 + n))
        c.thing(x, y, ajarmap.DOOR_T, angle=angle, args=(0, CLOCKED, 0, SHADOW, 100 + n))

    def ten_year(self, x, y, angle=0, *, frame=0, n=1, when=THEN):
        """The ten-year door, as clocked(): it joins a frame THEN to the same
        frame BEFORE (then.zs). Its pair number is 100 + n, n other than the
        clocked door's."""
        c = self.copies[when]
        c.thing(x, y, ajarmap.DOOR_T, angle=angle, args=(0, TENYEAR, frame, 0, 100 + n))
        c.thing(x, y, ajarmap.DOOR_T, angle=angle, args=(0, TENYEAR, 0, SHADOW, 100 + n))

    # --- long causes --------------------------------------------------------------------------------
    def cause(self, x, y, tid, settings=2, *, tag=0, basin=0, depth=0, start=0, when=THEN):
        """A fixture THEN at x, y (an invisible thing; its look is the
        caller's): `tid` is its number (its lever and targets name it),
        `settings` 2, 3 or 4 (MAP21's beam). In each setting n the NOW sectors tagged `tag`
        go to their heights() for n, and the basin `basin` (ajarwater)
        stands `depth` over its floor in setting 1 and over, dry in 0.
        Starts in `start`. `when` BEFORE: a fixture BEFORE, and the sectors
        with its tag THEN and NOW (and BEFORE) are those it moves."""
        self.copies[when].thing(x, y, CAUSE_T, id=tid, args=(settings, tag, basin, depth, start))

    def lever(self, a, b, cause, *, foot=True, tex=None, when=THEN):
        """The fixture's lever on the 64-long wall piece a-b: THEN, USE
        steps its setting on (Thing_Activate); NOW the same lever is dead.
        `tex`: its own pictures, {NOW: dead, THEN: live} (MAP21's, with a
        name plate over them), instead of the plain ones. `when` BEFORE: live
        BEFORE, dead THEN and NOW (DEAD)."""
        if when == BEFORE:
            tex = tex or dict(DEAD, **{BEFORE: LIVE[BEFORE]})
            self.cut(a, b)
            peg = dict(dontpegbottom=True) if foot else {}
            self.before.line(a, b, special=130, args=(cause,), playeruse=True, repeatspecial=True, mid=tex[BEFORE],
                             exact=True, **peg)
            for c in (self.then, self.now):
                c.line(a, b, mid=tex[c.when], exact=True, **peg)
            return
        tex = tex or LEVER
        self.cut(a, b)
        peg = dict(dontpegbottom=True) if foot else {}
        self.then.line(a, b, special=130, args=(cause,), playeruse=True, repeatspecial=True, mid=tex[THEN],
                       exact=True, **peg)
        self.now.line(a, b, mid=tex[NOW], exact=True, **peg)

    def target(self, x, y, cause, setting=None, z=28, when=THEN):
        """Something to shoot THEN, at x, y (12 clear of its wall), `z` up:
        a shot of the player's (from either time, through a hung door too)
        sets the cause to `setting`, or steps it on (None). `when`: the
        cause's time, if not THEN."""
        self.copies[when].thing(x, y, TARGET_T, height=z, args=(cause, 0 if setting is None else setting + 1))

    def beam(self, x, y, cause, angles):
        """THEN's emitter at x, y: in setting n (1, 2, 3) it shines along
        angles[n - 1] to the first wall."""
        self.then.thing(x, y, EMITTER_T, args=(cause,) + tuple(angles))

    def belt_run(self, x, y, cause, tag, speed):
        """THEN's belt `tag` (ajarmap.belt(scroll=False)) runs in setting 1
        at `speed` (x, y units a tic) and stands in 0."""
        self.then.thing(x, y, BELT_T, args=(cause, tag, 128 + speed[0], 128 + speed[1]))

    def hidden(self, x, y, type, cause, when=NOW):
        """An item at x, y that is there only in the cause's setting 0 (and
        once the floor under it is back): what lies in a pit a heap covers."""
        self.copies[when].thing(x, y, type, id=HIDDEN + cause)

    def music(self, a, b, at, tid, *, when=NOW):
        """A lever on the wall piece a-b that turns the music by time off and
        on; `at` is a spot in the room for the thing that stands for it."""
        c = self.copies[when]
        c.cut(a, b)
        c.line(a, b, special=130, args=(tid,), playeruse=True, repeatspecial=True, mid=LIVE[when], exact=True,
               dontpegbottom=True)
        c.thing(at[0], at[1], MUSIC_T, id=tid)

    # --- added for MAP21 (tools/map_longrun.py) ------------------------------------------------------
    def clock_frame(self, a, b, out, n, floor=0, *, when=(NOW, THEN), **k):
        """Frame n (n + THEN_ID THEN), which takes the clocked door only in
        the copies `when` (its trim says so, CLOCK_TRIM; then.zs refuses any
        other door there: "This frame takes only the clocked door.") and any
        door in the others. In a PUZZLE graph: only={n: the clocked door}, and
        for a twin that takes any door its own only={n + THEN_ID: every door}."""
        for c in self.copies:
            extra = dict(only=CLOCK_ONLY, trim=CLOCK_TRIM) if c.when in when else {}
            c.frame(a, b, out, n, floor, **dict(k, **extra))

    def locked(self, x, y, tid):
        """The thing that says "Locked for the night." for every line that
        does Thing_Activate(tid) (then's doors: locked_door())."""
        self.then.thing(x, y, LOCKED_T, id=tid)


CLOCK_ONLY = 6                          # AjarFrame args[4]: it takes the clocked door only (then.zs, ClockedRefuses)
CLOCK_TRIM = ("AJCKTR", "AJCKTF")       # ... and its trim (tools/gfx_then.py)
LOCKED_T = 20186                        # AjarThenLocked (then.zs)
AMBUSH_BOLTS, AMBUSH_CAUSE = 62, 63     # AjarAmbush causes (ajar.zs): a sector tag first open; a cause first set to a setting


def ambush(m, cause, arg, kind, *spots, angle=0, after=0, near=0):
    """As ajarmap.ambush (thinned the same way, counted with it), for the
    causes that need a number of their own (args[4]): AMBUSH_BOLTS, `arg` a
    sector tag, the monsters come when a sector with that tag first stands
    open (a bolted door's bolts drawn: ajarmap.bolted); AMBUSH_CAUSE, `arg`
    a cause's tid * 16 + a setting, they come when that cause is first set
    to that setting by a change (not at the start) and NOW has followed."""
    for x, y in spots:
        i = m.ambushers = getattr(m, "ambushers", -1) + 1
        m.thing(x, y, ajarmap.AMBUSH_T, angle=angle, args=(cause, kind, after, near, arg),
                skill=1 if i % 2 == 0 else 3 if i % 4 == 3 else 2)


RESERVED = set(range(270, 290)) | {190, 193, 500, 590, 591}     # line ids the engine keeps (ajar.zs: STRAY_ID.., HOME_MOUTH, ...)


def check_ids(m):
    """A map's frames and far sides keep clear of each other and of the ids
    the engine reserves: every portal line's id (frames, far sides; n,
    n + THEN_ID, n + 2 x THEN_ID) is on that line alone and is no reserved
    one, and no thing but its frame has a frame's tid (a lever's
    Thing_Activate names a cause by its tid). Returns the problems."""
    out = []
    portal = {}
    for edge, p in m.lineprops.items():
        if p.get("special") == 156:
            portal.setdefault(p.get("id"), []).append(edge)
    for i, edges in portal.items():
        if len(edges) > 1:
            out.append(f"line id {i}: {len(edges)} portal lines")
        if i in RESERVED:
            out.append(f"line id {i} is one the engine keeps")
    others = {p.get("id") for p in m.lineprops.values() if p.get("id") and p.get("special") != 156}
    out += [f"line id {i}: a portal line's and another line's" for i in sorted(set(portal) & others)]
    frames = [t.get("id") for t in m.things if t["type"] == ajarmap.FRAME_T]
    rest = [t.get("id") for t in m.things if t["type"] != ajarmap.FRAME_T and t.get("id")]
    out += [f"tid {i}: a frame's and another thing's" for i in sorted(set(frames) & set(rest))]
    out += [f"tid {i}: two frames" for i in sorted({i for i in frames if frames.count(i) > 1})]
    return out
