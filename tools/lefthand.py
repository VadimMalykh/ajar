"""The left-handed copy (PLAN.md, "The left-handed room lab"): a room built a
second time as its own mirror image, so that a plain line portal onto it
looks like a mirror (MAP20's secret way out).

    import lefthand
    src = Map()                     # the room as it stands, built on its own
    ...                             # (anything a Map can hold)
    lefthand.left_handed(m, src, "y", 392, (2048, 48))

puts into the Map `m` the whole of `src` reflected in the line y = 392 and
then moved by (2048, 48). A pane of glass in the plane of reflection whose
line is a portal onto its own image in the copy is then exactly where a
mirror in that plane would show the room: the portal is a pure shift (its
two lines are one line reflected, so the engine's turn is none).

What is reflected, and how:
- The plan: every vertex. Every line runs the other way (v1 and v2
  swapped), so that each side stays on the side of its own sector: a wall
  keeps its face to its room.
- Wall textures: each is replaced by a copy flipped left to right (made by
  flip_all() in the build, named AJLHnnn), and its x offset is set so that
  each column of the wall shows what the mirror shows there: on a line of
  length L with offset o and scale k the new offset is -(o + L k).
- Flats: replaced by a copy flipped across the plane (rows for a plane
  along x, columns for one along y). Flats are laid by world position, so
  the copy must stand where the 64 grid comes out right: for axis "y" the
  shift's x a multiple of 64 and 2 * at + its y a multiple of 64 (the same
  the other way round for "x"). Panning across the plane and rotation are
  negated (untested: the lab has none).
- Things: at the mirrored place, the angle mirrored; their sprites are
  flipped by the engine (SPRITEFLIP, which also mirrors which rotation is
  shown) for every actor standing in the copy at the start: a marker thing
  (AjarLeftHanded, src/zscript/lefthand.zs) over the copy's box does it.
  An actor that comes into the copy later is not flipped.
- Light, heights, specials, ids, tags and flags are kept as they are.

The copy is put in whole (Map.chunks): it shares no vertex or line with the
rest of `m`, so it is an island, joined to the rest only by portals (and
it is not seen by tools/mapcheck.py, which reads Map.polys: check `src`).
Only textures made by the build (tools/gfx*.py) can be flipped; a Doom
texture stops the build (flip_all).
"""
FLIPPED = {}            # (name, how) -> the flipped copy's name; how: "x" a wall texture, "fx"/"fy" a flat across x / y
LEFTHANDED_T = 20150    # AjarLeftHanded (lefthand.zs): args half width, half height of the box it stands in the middle of
KEEP = {"-", "", "F_SKY1"}


def flipped(name, how):
    if name in KEEP:
        return name
    return FLIPPED.setdefault((name, how), "AJLH%03d" % len(FLIPPED))


def left_handed(dest, src, axis, at, shift, *, marker=True, hide=False):
    """Puts `src` (a udmf.Map) into `dest` reflected in the line axis = at
    ("y": y -> 2 at - y; "x": x -> 2 at - x), then moved by shift = (dx, dy).
    `hide`: the copy is not drawn on the automap until a player stands in it
    (AjarLeftHanded's args[2]). Returns the copy's box (x1, y1, x2, y2) in `dest`."""
    dx, dy = shift
    if axis == "y":
        assert dx % 64 == 0 and (2 * at + dy) % 64 == 0, "the flats would not line up: see lefthand.py"
        place = lambda p: (p[0] + dx, 2 * at - p[1] + dy)
        turn = lambda a: (360 - a) % 360
        across, flat = "y", "fy"
    else:
        assert dy % 64 == 0 and (2 * at + dx) % 64 == 0, "the flats would not line up: see lefthand.py"
        place = lambda p: (2 * at - p[0] + dx, p[1] + dy)
        turn = lambda a: (180 - a) % 360
        across, flat = "x", "fx"
    verts, lines, sides, sectors, things = src.parts()
    nverts = [place(v) for v in verts]
    nlines, nsides = [], [dict(sd) for sd in sides]
    for ld in lines:
        ld = dict(ld)
        a, b = verts[ld["v1"]], verts[ld["v2"]]
        length = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
        ld["v1"], ld["v2"] = ld["v2"], ld["v1"]
        for k in ("sidefront", "sideback"):
            if k in ld:
                sd = nsides[ld[k]]
                if "offsetx" in sd:
                    sd["offsetx"] = -sd["offsetx"]
                for part, tex in (("top", "texturetop"), ("mid", "texturemiddle"), ("bottom", "texturebottom")):
                    if sd.get(tex) and sd[tex] not in KEEP:
                        sd[tex] = flipped(sd[tex], "x")
                        o = sd.get("offsetx_" + part, 0.0)
                        sd["offsetx_" + part] = float(-(o + length * sd.get("scalex_" + part, 1.0)))
        nlines.append(ld)
    nsectors = []
    for d in sectors:
        d = dict(d)
        for k in ("texturefloor", "textureceiling"):
            d[k] = flipped(d[k], flat)
        for part in ("floor", "ceiling"):
            for k in (across + "panning" + part, "rotation" + part):
                if k in d:
                    d[k] = -d[k]
        nsectors.append(d)
    nthings = []
    for t in things:
        t = dict(t)
        t["x"], t["y"] = (float(v) for v in place((t["x"], t["y"])))
        t["angle"] = turn(t.get("angle", 0))
        nthings.append(t)
    xs, ys = [v[0] for v in nverts], [v[1] for v in nverts]
    box = (min(xs), min(ys), max(xs), max(ys))
    if marker:
        nthings.append(dict(x=float((box[0] + box[2]) / 2), y=float((box[1] + box[3]) / 2), type=LEFTHANDED_T, angle=0,
                            arg0=int((box[2] - box[0]) / 2) + 1, arg1=int((box[3] - box[1]) / 2) + 1, **({"arg2": 1} if hide else {}),
                            **{f"skill{n}": True for n in range(1, 6)}, single=True, coop=True, dm=True))
    dest.chunks.append((nverts, nlines, nsides, nsectors, nthings))
    return box


def flip_all(out):
    """The flipped copies FLIPPED asks for, from the textures and flats in
    `out` (gfx.make_all's dict): a wall texture flipped left to right goes to
    textures/, a flat flipped across x or y to flats/."""
    import gfx
    for (name, how), new in sorted(FLIPPED.items(), key=lambda kv: kv[1]):
        data = out.get(f"textures/{name}.png") or out.get(f"flats/{name}.png")
        if data is None:
            raise SystemExit(f"lefthand: {name} is not made by the build and cannot be flipped (a Doom texture?)")
        im = gfx.unpng(data)
        rows = [im.px[y * im.w:(y + 1) * im.w] for y in range(im.h)]
        if how in ("x", "fx"):
            rows = [r[::-1] for r in rows]
        else:
            rows = rows[::-1]
        im.px = [p for r in rows for p in r]
        out[("textures/" if how == "x" else "flats/") + new + ".png"] = im.png()
