"""Question 1 of the left-handed room lab, measured: the pane wall photographed
as built (bay A: the fourth pane is the opening) and with the opening a real
mirror (bay B), from the same five cameras, each with the player drawn and
hidden (MAP=LEFT MODE=2 tools/smoke.sh writes the 22 screenshots in order).

    MAP=LEFT MODE=2 tools/smoke.sh "$PWD/build/smokeL2"
    docker run --rm -v "$PWD/build/smokeL2":/d -v "$PWD/tools":/t:ro python:3.12-slim \
        sh -c "pip install -q pillow && python /t/lefthand_compare.py /d"

(EXTRA="+gl_mirror_envmap 0" for the run without the mirrors' sheen). Prints, for
each camera: the pixels that differ between A and B with the player hidden
(everything that is not the player), and with him drawn, outside the place
where his reflection stands (found as where B differs from B without him);
and writes diff_c<n>.png (A | B | where they differ, in red over B dimmed)
into the folder. Views 20 and 21 (A and B turned to the south wall, away
from the glass) are the control: any difference there is not the panes'.
A pixel differs when one of its channels differs by more than 24 (of 255).
"""
import glob
import os
import sys

from PIL import Image, ImageChops, ImageFilter

THRESHOLD = 24
d = sys.argv[1]
shots = sorted(glob.glob(os.path.join(d, "*.png")))
shots = [s for s in shots if os.path.basename(s).startswith("Screenshot")]
if len(shots) < 22:
    sys.exit(f"{len(shots)} screenshots in {d}, 22 wanted")
img = [Image.open(s).convert("RGB") for s in shots[:22]]
W, H = img[0].size
HUD = int(os.environ.get("HUD_ROWS", "0"))     # rows at the bottom to leave out (the HUD is the same in both)


def mask_of(a, b):
    """Where a and b differ: a 1-bit picture."""
    diff = ImageChops.difference(a, b)
    r, g, bl = diff.split()
    m = ImageChops.lighter(ImageChops.lighter(r, g), bl).point(lambda v: 255 if v > THRESHOLD else 0)
    if HUD:
        m.paste(0, (0, H - HUD, W, H))
    return m


def count(m, exclude=None):
    if exclude is not None:
        m = ImageChops.subtract(m, exclude)
    n = sum(1 for v in m.getdata() if v)
    return n, m.getbbox()


def picture(a, b, m, path):
    out = Image.new("RGB", (W * 3, H))
    out.paste(a, (0, 0))
    out.paste(b, (W, 0))
    dim = b.point(lambda v: v // 3)
    red = Image.new("RGB", (W, H), (255, 40, 40))
    dim.paste(red, (0, 0), m)
    out.paste(dim, (2 * W, 0))
    out.resize((W * 3 // 2, H // 2)).save(path)


total = W * (H - HUD)
names = ["straight on", "from the west at a slant", "from the east at a slant", "from the far corner",
         "before the fourth pane"]
for c in range(5):
    a_seen, b_seen, a_hid, b_hid = img[4 * c:4 * c + 4]
    hidden = mask_of(a_hid, b_hid)
    n_hid, box_hid = count(hidden)
    player = mask_of(b_seen, b_hid).filter(ImageFilter.MaxFilter(9))     # his reflection in B, widened by 4
    seen = mask_of(a_seen, b_seen)
    n_out, box_out = count(seen, player)
    n_in, _ = count(player)
    n_tell = sum(1 for p, q in zip(seen.getdata(), player.getdata()) if p and q)
    print(f"camera {c} ({names[c]}): player hidden: {n_hid} pixels differ ({100 * n_hid / total:.3f}%), box {box_hid}; "
          f"player drawn, outside his reflection ({n_in} pixels): {n_out} ({100 * n_out / total:.3f}%), box {box_out}; "
          f"inside it: {n_tell} differ (the tell)")
    picture(a_hid, b_hid, hidden, os.path.join(d, f"diff_c{c}_hidden.png"))
    picture(a_seen, b_seen, seen, os.path.join(d, f"diff_c{c}_seen.png"))
ctl = mask_of(img[20], img[21])
n, box = count(ctl)
print(f"control (A and B turned to the south wall): {n} pixels differ, box {box}")
