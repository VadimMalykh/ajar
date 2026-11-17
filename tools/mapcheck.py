"""Checks a level's geometry and draws it: python3 tools/mapcheck.py map_hinges6 [out.png]

Reports sectors that overlap, things that stand in no sector or in a sector
too low for them, and things closer than 16 to a wall or a step they cannot
climb. The picture (4 map units to a pixel, north up) shows floors by
height, things as dots (red: monsters, green: the rest) and doors, frames
and keys in white.
"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import gfx

mod = importlib.import_module(sys.argv[1])
m = mod.m
S = 4
polys = m.polys
xs = [p[0] for poly in polys for p in poly if p[0] < 3000]
ys = [p[1] for poly in polys for p in poly]
x0, x1, y0, y1 = min(xs) - 32, max(xs) + 32, min(ys) - 32, max(ys) + 32
W, H = (x1 - x0) // S, (y1 - y0) // S


def inside(poly, x, y):
    n = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > y) != (b[1] > y) and x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
            n = not n
    return n


def sector_at(x, y):
    return [i for i, poly in enumerate(polys) if inside(poly, x, y)]


bad = 0
boxes = [(min(p[0] for p in poly), min(p[1] for p in poly), max(p[0] for p in poly), max(p[1] for p in poly))
         for poly in polys]
for i in range(len(polys)):
    for j in range(i + 1, len(polys)):
        a, b = boxes[i], boxes[j]
        if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
            cx, cy = (max(a[0], b[0]) + min(a[2], b[2])) / 2, (max(a[1], b[1]) + min(a[3], b[3])) / 2
            if inside(polys[i], cx + 0.5, cy + 0.5) and inside(polys[j], cx + 0.5, cy + 0.5):
                print(f"OVERLAP sectors {i} {boxes[i]} and {j} {boxes[j]}")
                bad += 1

MONSTERS = {3004, 9, 3001, 3002, 58, 65, 69, 3003, 66, 3006, 3005, 67, 68, 71, 64, 20003, 20004, 20005, 20007}
RADIUS = {3002: 30, 58: 30, 69: 24, 3003: 24, 3005: 31, 67: 48, 68: 64, 71: 31, 66: 20}
for t in m.things:
    x, y = t["x"], t["y"]
    s = sector_at(x + 0.5, y + 0.5)
    if not s:
        print(f"VOID thing {t['type']} at {x},{y}")
        bad += 1
        continue
    sec = m.sectors[s[0]]
    r = RADIUS.get(t["type"], 20 if t["type"] in MONSTERS else 16)
    if t["type"] in (20001, 20002):
        continue
    for dx in (-r, 0, r):
        for dy in (-r, 0, r):
            o = sector_at(x + dx + 0.5, y + dy + 0.5)
            if not o:
                print(f"WALL thing {t['type']} at {x},{y} (radius {r}) reaches a wall")
                bad += 1
                break
            f = m.sectors[o[0]]["floor"]
            if abs(f - sec["floor"]) > 24 and t["type"] in MONSTERS:
                print(f"EDGE thing {t['type']} at {x},{y} (radius {r}) hangs over a step of {f - sec['floor']}")
                break
        else:
            continue
        break

if len(sys.argv) > 2:
    im = gfx.Img(W, H, (16, 16, 24))
    floors = sorted({s["floor"] for s in m.sectors})
    for i, b in enumerate(boxes):
        if b[0] > 3000:
            continue
        sec = m.sectors[i]
        k = floors.index(sec["floor"]) / max(1, len(floors) - 1)
        c = (int(60 + 150 * k), int(70 + 100 * k), int(150 - 90 * k))
        if sec["floor"] == sec["ceil"]:
            c = (200, 120, 40)                      # a shut door
        if sec["special"] == 1024:
            c = (c[0], min(255, c[1] + 60), c[2])
        im.rect((b[0] - x0) // S + 1, H - (b[3] - y0) // S + 1, (b[2] - x0) // S, H - (b[1] - y0) // S, c)
    for t in m.things:
        if t["x"] > 3000:
            continue
        c = (255, 60, 60) if t["type"] in MONSTERS else (255, 255, 255) if t["type"] in (
            20001, 20002, 20011, 20012, 20013, 20014, 1) else (80, 255, 80)
        px, py = int(t["x"] - x0) // S, H - int(t["y"] - y0) // S
        im.rect(px - 1, py - 1, px + 2, py + 2, c)
    with open(sys.argv[2], "wb") as f:
        f.write(im.png())
print(f"{len(polys)} sectors, {len(m.things)} things, {sum(t['type'] in MONSTERS for t in m.things)} monsters, "
      f"{sum(s['special'] == 1024 for s in m.sectors)} secret sectors, {bad} problems")
