"""Solid things standing in each other or under a ceiling too low for them:
python3 tools/thingcheck.py map_hinges3 ... (in the ajar-tools image, from the project root)"""
import importlib, sys, math
sys.path.insert(0, "tools")
R = {3004: 20, 9: 20, 3001: 20, 65: 20, 3002: 30, 58: 30, 69: 24, 3003: 24, 66: 20, 3006: 16, 3005: 31, 67: 48,
     68: 64, 71: 31, 20003: 20, 20004: 24, 20005: 20, 20007: 20, 2035: 10, 2028: 16, 35: 16, 86: 16, 46: 16, 45: 16, 55: 16,
     1: 16, 20021: 16, 20022: 16, 20023: 16, 20024: 16}
MON = {3004, 9, 3001, 65, 3002, 58, 69, 3003, 66, 3006, 3005, 67, 68, 71, 20003, 20004, 20005, 20007}
H = {3005: 56, 69: 64, 3003: 64, 67: 64, 68: 64, 66: 56, 71: 56, 3002: 56, 58: 56, 3006: 56}
def inside(poly, x, y):
    n = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > y) != (b[1] > y) and x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
            n = not n
    return n
for name in sys.argv[1:]:
    m = importlib.import_module(name).m
    def sec(x, y):
        for i, p in enumerate(m.polys):
            if inside(p, x + .5, y + .5): return m.sectors[i]
    # an ambusher (ajarmap.ambush) is checked as what it will be, but not against
    # monsters: it waits for its place to be free
    T = [dict(t, type=t["args"][1], late=True) if t["type"] == 20030 else t for t in m.things]
    T = [t for t in T if t["type"] in R]
    bad = 0
    for i, a in enumerate(T):
        sa = sec(a["x"], a["y"])
        if sa and a["type"] in MON and sa["ceil"] - sa["floor"] < H.get(a["type"], 56):
            print(name, "LOW ceiling", a["type"], a["x"], a["y"]); bad += 1
        for b in T[i + 1:]:
            if a["type"] == 20003 or (a.get("late") != b.get("late") and {a["type"], b["type"]} <= MON): continue
            d = max(abs(a["x"] - b["x"]), abs(a["y"] - b["y"]))      # Doom's boxes
            if d < R[a["type"]] + R[b["type"]]:
                sb = sec(b["x"], b["y"])
                if sa and sb and abs(sa["floor"] - sb["floor"]) < 56:
                    print(name, "STUCK", a["type"], (a["x"], a["y"]), b["type"], (b["x"], b["y"])); bad += 1
    seen = {}
    for t in m.things:
        k = (t["x"], t["y"])
        if k in seen and t["type"] not in (20002, 20003) and seen[k] not in (20002, 20003):
            print(name, "SAME SPOT", t["type"], seen[k], k); bad += 1
        seen[k] = t["type"]
    print(name, "things check:", bad, "problems")
