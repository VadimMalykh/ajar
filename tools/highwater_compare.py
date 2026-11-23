"""MAP20's secret way out, measured (PLAN.md, "MAP20: the secret way out, built"): the swimming bath's
pane wall photographed as built (the fourth pane the opening onto the left-handed bath) and with the
fourth pane a real mirror (AJAR_SBMIRROR=1 ./build.sh), from the same places (MAP=MAP20 MODE=7
tools/smoke.sh writes 32 screenshots in order; src/zscript/map20.zs, PaneViews). As
tools/lefthand_compare.py does for the lab: a pixel differs when one of its channels differs by more
than 24 (of 255).

    AJAR_QUICK=1 AJAR_OUT=build/mirror.pk3 AJAR_SBMIRROR=1 ./build.sh
    MAP=MAP20 MODE=7 EXTRA=-nomonsters TIMEOUT=500 tools/smoke.sh "$PWD/build/v7"
    MAP=MAP20 MODE=7 EXTRA=-nomonsters TIMEOUT=500 PK3=build/mirror.pk3 tools/smoke.sh "$PWD/build/v7m"
    docker run --rm -v "$PWD/build":/d -v "$PWD/tools":/t:ro python:3.12-slim \
        sh -c "pip install -q pillow && python /t/highwater_compare.py /d/v7 /d/v7m [/d/v7before]"

Views (map20.zs): 0..8 three places on the poolside (0 straight on from the east, 1 from the north
walk, 2 from the south end) x the bath dry, at -64, at 0, the player hidden; 9..11 the three at 0
with the player drawn; 12..16 the player before each pane in turn, at 0; 17 along the wall (the
copy's door in the fourth pane); 18 from the north walk with BLUE hung in 142; 19..21 the notch
(P at 48 at its pressure door, K at 48 at its door, C at -64 at E2 and the cells); 22 from the copy;
23..31 views 0..8 again. From view 9 on, but for 19..21, the water's surface is a still flat in
both baths (AJLBFLOR): the engine animates FWATER1 by the clock, so no two runs show the same frame
of it, and views 0..8 differ in the water between any two runs, even of one build. A third folder may be
another run of the same build (the noise between runs) or an earlier one (the notch before).
Writes cmp_<view>.png (as built | mirror | where they differ, in red over the mirror dimmed) into the
first folder; with a third folder (an earlier run as built), notch_<view>.png for views 19..21
(before | after | the difference).
"""
import glob
import os
import sys

from PIL import Image, ImageChops, ImageFilter

THRESHOLD = 24


def shots(d):
    s = sorted(p for p in glob.glob(os.path.join(d, "*.png")) if os.path.basename(p).startswith("Screenshot"))
    if len(s) < 32:
        sys.exit(f"{len(s)} screenshots in {d}, 32 wanted")
    return [Image.open(p).convert("RGB") for p in s[:32]]


def mask_of(a, b):
    diff = ImageChops.difference(a, b)
    r, g, bl = diff.split()
    return ImageChops.lighter(ImageChops.lighter(r, g), bl).point(lambda v: 255 if v > THRESHOLD else 0)


def count(m, exclude=None):
    if exclude is not None:
        m = ImageChops.subtract(m, exclude)
    return sum(1 for v in m.getdata() if v), m.getbbox()


def picture(a, b, m, path):
    W, H = a.size
    out = Image.new("RGB", (W * 3, H))
    out.paste(a, (0, 0))
    out.paste(b, (W, 0))
    dim = b.point(lambda v: v // 3)
    dim.paste(Image.new("RGB", (W, H), (255, 40, 40)), (0, 0), m)
    out.paste(dim, (2 * W, 0))
    out.resize((W * 3 // 2, H // 2)).save(path)


A, B = shots(sys.argv[1]), shots(sys.argv[2])
W, H = A[0].size
total = W * H
pct = lambda n: f"{100 * n / total:.3f}%"
places = ["straight on from the east poolside", "from the north walk", "from the south end of the poolside"]
waters = ["dry", "at -64", "at 0"]
print(f"{W}x{H} = {total} pixels a view")
for i in range(9):
    m = mask_of(A[i], B[i])
    n, box = count(m)
    print(f"view {i:2} ({places[i // 3]}, the bath {waters[i % 3]}, player hidden): {n} pixels differ ({pct(n)}), box {box}")
    picture(A[i], B[i], m, os.path.join(sys.argv[1], f"cmp_{i:02}.png"))
for c in range(3):
    i, hid = 9 + c, 23 + 3 * c + 2
    player = mask_of(B[i], B[hid]).filter(ImageFilter.MaxFilter(9))      # his reflection in the mirrors, widened by 4
    seen = mask_of(A[i], B[i])
    n_in, pbox = count(player)
    n_out, box = count(seen, player)
    n_tell = sum(1 for p, q in zip(seen.getdata(), player.getdata()) if p and q)
    print(f"view {i:2} ({places[c]}, at 0, player drawn): outside his reflection ({n_in} pixels, box {pbox}) {n_out} differ "
          f"({pct(n_out)}), box {box}; inside it {n_tell} differ (the tell)")
    picture(A[i], B[i], seen, os.path.join(sys.argv[1], f"cmp_{i:02}.png"))
for i in range(23, 32):
    m = mask_of(A[i], B[i])
    n, box = count(m)
    print(f"view {i:2} ({places[(i - 23) // 3]}, the bath {waters[(i - 23) % 3]}, player hidden, still water): "
          f"{n} pixels differ ({pct(n)}), box {box}")
    picture(A[i], B[i], m, os.path.join(sys.argv[1], f"cmp_{i:02}.png"))
for k in range(5):
    i = 12 + k
    m = mask_of(A[i], B[i])
    n, box = count(m)
    print(f"view {i:2} (the player before pane {k + 1}, at 0): {n} pixels differ, box {box}")
    picture(A[i], B[i], m, os.path.join(sys.argv[1], f"cmp_{i:02}.png"))
for i, what in ((17, "along the wall, the copy's door"), (18, "from the north walk, BLUE in 142"), (22, "from the copy")):
    m = mask_of(A[i], B[i])
    n, box = count(m)
    print(f"view {i:2} ({what}): {n} pixels differ ({pct(n)}), box {box}")
    picture(A[i], B[i], m, os.path.join(sys.argv[1], f"cmp_{i:02}.png"))
if len(sys.argv) > 3:
    C = shots(sys.argv[3])
    for i in list(range(0, 18)) + list(range(23, 32)):
        n, box = count(mask_of(C[i], A[i]))
        print(f"the same build, two runs: view {i:2}: {n} pixels differ, box {box}")
    for i, what in ((19, "P at 48, its pressure door"), (20, "K at 48, its door"), (21, "C at -64, E2 and the cells")):
        m = mask_of(C[i], A[i])
        n, box = count(m)
        print(f"notch view {i} ({what}): before and after differ in {n} pixels, box {box}")
        picture(C[i], A[i], m, os.path.join(sys.argv[1], f"notch_{i:02}.png"))
