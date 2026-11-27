"""The pictures of MAP23's look board (tools/board23_shots.sh runs this in the ajar-pil image: Pillow).

    python3 board23_sheets.py views <raw dir> <out dir> <sheet.jpg>
        raw/view_NN.png -> out/view_NN.jpg (the test's text lines, 40 px, cropped off the top; 819 wide) and a
        contact sheet with each view's number on it
    python3 board23_sheets.py swatches <dir> <sheet.jpg>
        every PNG in dir (textures, flats, sprites of a look) on one sheet, named, each at most 192 high
"""
import glob
import os
import sys

from PIL import Image, ImageDraw


def views(raw, out, sheet):
    os.makedirs(out, exist_ok=True)
    names = sorted(glob.glob(os.path.join(raw, "view_*.png")))
    thumbs = []
    for p in names:
        im = Image.open(p).convert("RGB")
        im = im.crop((0, 40, im.width, im.height))
        im = im.resize((819, round(im.height * 819 / im.width)), Image.LANCZOS)
        q = os.path.join(out, os.path.basename(p)[:-4] + ".jpg")
        im.save(q, quality=86)
        thumbs.append((os.path.basename(p)[5:7], im))
    if not thumbs:
        return
    tw, th, cols = 320, round(320 * thumbs[0][1].height / 819), 6
    rows = (len(thumbs) + cols - 1) // cols
    S = Image.new("RGB", (cols * (tw + 4) + 4, rows * (th + 4) + 4), (34, 34, 34))
    d = ImageDraw.Draw(S)
    for k, (n, im) in enumerate(thumbs):
        x, y = 4 + (k % cols) * (tw + 4), 4 + (k // cols) * (th + 4)
        S.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        d.rectangle((x, y, x + 26, y + 16), fill=(0, 0, 0))
        d.text((x + 4, y + 2), n, fill=(255, 255, 0))
    S.save(sheet, quality=85)


def swatches(folder, sheet):
    names = sorted(p for p in glob.glob(os.path.join(folder, "*.png")))
    cells = []
    for p in names:
        im = Image.open(p).convert("RGBA")
        if im.height > 192:
            im = im.resize((max(1, round(im.width * 192 / im.height)), 192), Image.NEAREST)
        if im.width > 256:
            im = im.resize((256, max(1, round(im.height * 256 / im.width))), Image.NEAREST)
        scale = 2 if im.width <= 64 and im.height <= 96 else 1
        if scale > 1:
            im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        cells.append((os.path.basename(p)[:-4], im))
    W = 1600
    x, y, rowh, placed = 4, 4, 0, []
    for nm, im in cells:
        w, h = im.width, im.height + 14
        if x + w > W - 4:
            x, y, rowh = 4, y + rowh + 6, 0
        placed.append((nm, im, x, y))
        x += w + 6
        rowh = max(rowh, h)
    S = Image.new("RGB", (W, y + rowh + 8), (40, 40, 44))
    d = ImageDraw.Draw(S)
    for nm, im, x, y in placed:
        bg = Image.new("RGB", im.size, (90, 0, 90))
        bg.paste(im, (0, 0), im)
        S.paste(bg, (x, y + 14))
        d.text((x, y), nm, fill=(255, 255, 255))
    S.save(sheet, quality=88)


if __name__ == "__main__":
    if sys.argv[1] == "views":
        views(*sys.argv[2:5])
    else:
        swatches(*sys.argv[2:4])
