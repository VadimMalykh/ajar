"""Map helpers for a map played whole in three goes (MAP33; the lab is map
THIRD, tools/map_third.py). src/zscript/third.zs has the contract; PLAN.md,
"The three goes lab"."""
import re

import ajarmap
import ajartime

THIRD_T = 20160     # AjarThird: the map is played in goes (one to a map)
HALL_T = 20161      # AjarThirdHall: a window hall
POST_T = 20162      # AjarThirdPost: a monster of the future seen
WATCH_T = 20163     # AjarThirdWatch: where an earlier self must not come before a hall is won
WIN_T = 20164       # AjarThirdWin: a shutter a hall's win opens
WIND_T = 20165      # AjarThirdWind: a plate on a wall that winds the clock on
LAST_T = 20166      # AjarThirdLast: the last hall, where every go fights the same fight (one to a map)
GUARD_T = 20167     # AjarThirdGuard: a monster of the last hall, there from the alarm
LOCK_T = 20168      # AjarThirdLock: a window hall's lobby, two shutters that lock the player in with its fight
FALLEN_T = 20169    # AjarThirdFallen: a monster of a later part, seen dead before its go
FIGHT = 9           # the fight number of the AjarZone over the whole map (the paradox's room)


def time_door(k):
    """The line id of time door k (at the end of part k)."""
    return 3310 + k


def box_door(k):
    """The line id of box k's door (where time door k - 1 comes out)."""
    return 3320 + k


def box_tag(k):
    """The sector tag of box k: its room and its door's recess."""
    return 3330 + k


def third(m, x, y, exit_tag, out_tag, zone, *, seconds=10):
    """The map is played in goes (third.zs). `exit_tag`: the AjarShutter
    that is the exit door, open while every plate is stood on and `seconds`
    more; `out_tag`: the sector tag of the room behind it (through the door).
    `zone` (x1, y1, x2, y2): the whole map, for the paradox (an AjarZone of
    fight FIGHT)."""
    m.thing(x, y, THIRD_T, args=(exit_tag, out_tag, seconds))
    ajartime.zone(m, FIGHT, 0, *zone)


def time_door_at(m, k, a, b, out, floor, **look):
    """Time door k, in the end room of part k: a-b its 64-wide mouth, `out`
    pointing out of the room. Through it, the player is in box k + 1."""
    ajarmap.recess(m, a, b, out, floor, time_door(k), box_door(k + 1), far_colour=ajartime.TIME, **look)


def box_door_at(m, k, a, b, out, floor, **look):
    """Box k's door (in its wall, `out` pointing out of the box): where the
    player comes out of time door k - 1. Shut for good."""
    ajarmap.recess(m, a, b, out, floor, box_door(k), time_door(k - 1), far_colour=ajartime.TIME, tag=box_tag(k), **look)


def box(m, k, poly, **look):
    """Box k's room (its sectors carry box_tag(k))."""
    return m.sector(poly, id=box_tag(k), **look)


def hall(m, x, y, h, part, tag, tag2=0):
    """Window hall h: every sector with `tag` (and `tag2`). The go of `part`
    fights there and is recorded; every later go sees it played back."""
    m.thing(x, y, HALL_T, args=(h, part, tag, tag2))


def post(m, x, y, h, kind, angle=0):
    """A monster of Doom editor number `kind` that hall h's fight has at x, y:
    before that fight's go a body lies there (if it leaves one), in it the
    monster stands there idle. Put it where it cannot leave (a pedestal 64
    high, a pit) or give it a monster that leaves no body."""
    m.thing(x, y, POST_T, angle=angle, args=(h, kind))


def fallen(m, x, y, part, kind, angle=0, **kw):
    """An ordinary monster of Doom editor number `kind` in `part`, at x, y,
    facing `angle`, that an earlier go sees before its own go comes there
    (through glass): in every go before `part`'s a body lies there (if it
    leaves one), as that go will leave it; at the start of `part`'s go it
    stands there alive, with no target and not in ambush; later goes find what
    that go left. Nothing is enforced (no hall, no win, no watch). `kw` goes
    to Map.thing (`skill=`)."""
    m.thing(x, y, FALLEN_T, angle=angle, args=(part, kind), **kw)


def watch(m, x, y, tag, h, go=1):
    """The earlier self of `go` must not come into a sector with `tag` while
    hall h's fight is not won (the paradox)."""
    m.thing(x, y, WATCH_T, args=(tag, h, go))


def win(m, x, y, h, shutter_tag):
    """The AjarShutter of `shutter_tag` is opened by hall h's win: open in
    the goes before its fight's, shut in that go until the win, and in later
    goes as it was then."""
    m.thing(x, y, WIN_T, args=(h, shutter_tag))


def lock(m, x, y, h, outer, inner, lobby):
    """Window hall h's way in is a LOBBY (third.zs, AjarThirdLock): `lobby`
    the tag of its sectors (give it to the hall as its second tag, so that
    they are in the hall: recorded, and its monsters may come into them),
    `outer` the tag of the AjarShutter between it and the way the player
    comes, `inner` that of the one between it and the hall (counted in the
    hall too). In the hall's go: the outer one open and the inner one shut
    until the player stands in the lobby clear of the outer one; then the
    outer one shuts, and once it is shut the inner one opens. Both open at
    the win, for good. In a later go as they were then, tic by tic; before
    the hall's go as at its start. Make the outer one worked from the
    lobby's side (its face a-b there): whoever is under it when it shuts is
    put into the lobby."""
    m.thing(x, y, LOCK_T, args=(h, outer, inner, lobby))


def plate(m, x, y, n):
    """Plate n (the end of part n), on the floor."""
    m.thing(x, y, ajartime.PLATE_T, args=(0, 0, 0, n))


def wind(m, x, y, angle, z=30):
    """A plate on a wall, facing `angle`, `z` over the floor: USE winds the
    clock on to two seconds before an earlier self next steps on its plate.
    Stand it 2 off the wall."""
    m.thing(x, y, WIND_T, angle=angle, height=float(z))


def stand_tag(k):
    """The sector tag of stand k: where go k stands at the last hall."""
    return 3360 + k


def last(m, x, y, hall_tag, *, first=30, later=15, gate=0):
    """The last hall (third.zs, AjarThirdLast): every sector with `hall_tag`
    (its floor, pedestals, bays). Empty until plate 1 is first pressed in a
    go: the alarm, and its guards come. Time door 1 opens once plate 1 has
    been stood on `first` seconds in all since the alarm; time door k > 1
    once plate k has been stood on `later` seconds in all while the earlier
    plates are pressed. `gate`: the tag of an AjarShutter (ajartime.shutter)
    that the alarm opens for the rest of the go (the last stand's way down)."""
    m.thing(x, y, LAST_T, args=(hall_tag, first, later, gate))


def guard(m, x, y, kind, angle=0, z=0, skill=None):
    """A monster of Doom editor number `kind` in the last hall: it comes at
    the alarm, here, facing `angle`, awake. `z` over the floor (a flyer).
    `skill` n: there from difficulty n up (Map.thing's; without it on all)."""
    kw = {"height": float(z)} if z else {}
    if skill:
        kw["skill"] = skill
    m.thing(x, y, GUARD_T, angle=angle, args=(kind,), **kw)


def railing(m, a, b):
    """A stand's front a-b over the last hall: the gantry's railing, a
    two-sided line nobody walks or flies over; shots and sight pass it."""
    m.line(a, b, mid="AJRAIL", midboth=True, blocking=True, blockmonsters=True, dontpegbottom=True)


def tiles(x1, y1, x2, y2, holes):
    """The rectangle x1..x2, y1..y2 less the rectangles `holes` (x1, y1, x2,
    y2), as rectangles: a floor round its islands (pedestals, blocks, a
    pillar: each declared by itself, or left out for a solid one)."""
    xs = sorted({x1, x2} | {v for h in holes for v in (h[0], h[2]) if x1 < v < x2})
    ys = sorted({y1, y2} | {v for h in holes for v in (h[1], h[3]) if y1 < v < y2})
    def free(ax, ay):
        return not any(h[0] <= ax < h[2] and h[1] <= ay < h[3] for h in holes)
    rows = []
    for ya, yb in zip(ys, ys[1:]):
        run = None
        for xa, xb in zip(xs, xs[1:]):
            if free(xa, ya):
                run = (run[0], xb) if run else (xa, xb)
            elif run:
                rows.append((run[0], ya, run[1], yb)); run = None
        if run:
            rows.append((run[0], ya, run[1], yb))
    # strips of the same width one over the other become one
    out = []
    for r in rows:
        for i, o in enumerate(out):
            if o[0] == r[0] and o[2] == r[2] and o[3] == r[1]:
                out[i] = (o[0], o[1], o[2], r[3])
                break
        else:
            out.append(r)
    return out


def closed(m, tag_a, tag_b):
    """Every line between a sector with `tag_a` and one with `tag_b` blocks
    players and monsters (a stand's railing over the last hall). Returns how
    many there are."""
    text = m.textmap()
    tags = [int(t.group(1)) if t else 0 for t in
            (re.search(r"\bid=(-?\d+);", s) for s in re.findall(r"sector\{([^}]*)\}", text))]
    sides = [int(s) for s in re.findall(r"sidedef\{[^}]*?sector=(\d+);", text)]
    n = 0
    for ld in re.findall(r"linedef\{([^}]*)\}", text):
        if "sideback" not in ld:
            continue
        f = tags[sides[int(re.search(r"sidefront=(\d+);", ld).group(1))]]
        k = tags[sides[int(re.search(r"sideback=(\d+);", ld).group(1))]]
        if {f, k} != {tag_a, tag_b}:
            continue
        assert "blocking=true" in ld and "blockmonsters=true" in ld, f"a line between tags {tag_a} and {tag_b} is open: {ld}"
        n += 1
    return n


def ways(m):
    """Sector -> the sectors beside it over a two-sided line that does not block."""
    text = m.textmap()
    sides = [int(s) for s in re.findall(r"sidedef\{[^}]*?sector=(\d+);", text)]
    nxt = {}
    for ld in re.findall(r"linedef\{([^}]*)\}", text):
        if "sideback" not in ld or "blocking=true" in ld:
            continue
        f = sides[int(re.search(r"sidefront=(\d+);", ld).group(1))]
        k = sides[int(re.search(r"sideback=(\d+);", ld).group(1))]
        nxt.setdefault(f, set()).add(k)
        nxt.setdefault(k, set()).add(f)
    return nxt


def reach(m, start, nxt=None):
    """The sectors reached on foot from sector `start` (or from any of a list
    of them), both ways over every two-sided line that does not block (heights
    are not looked at: a drop counts as a way back up, which only makes the
    check stricter). `nxt`: ways(m), when it is made already."""
    nxt = nxt if nxt is not None else ways(m)
    starts = list(start) if isinstance(start, (list, tuple, set)) else [start]
    seen, todo = set(starts), list(starts)
    while todo:
        for q in nxt.get(todo.pop(), ()):
            if q not in seen:
                seen.add(q)
                todo.append(q)
    return seen


def apart(m, starts):
    """No part is joined to another on foot: `starts` {part: a sector of it,
    or a list of them (a part whose way on is a door: the sectors beyond its
    far sides too)}; what is reached from each is reached from no other."""
    nxt = ways(m)
    got = {p: reach(m, s, nxt) for p, s in starts.items()}
    for p in got:
        for q in got:
            assert p == q or not got[p] & got[q], f"part {p} and part {q} are joined on foot"
    return got
