"""The engine tests for levels 11 to 20 (map ENG): MAP=ENG ./run.sh

Five bays off one corridor, west to east; none of them uses a door that is
carried. Their portals are joined when the map loads and stay so.
  1 the lift: a portal in a lift car (its recess rides with the car), its
    other end in the lower hall. Buttons: the car's south wall, the hall's
    south wall, the landing's south wall.
  2 the loop: a corridor whose two ends open onto each other, a line across
    it that a missile sets off, and a shutter that line raises. The button
    on the south wall sends an imp's fireball round.
  3 the inside-out room: a hall with a frame in each wall; each opens out of
    the same face of a booth that stands in a square far away.
  4 mirrors: a mirror on the west wall, a portal opposite to a side room that
    has a mirror of its own, and two things that only a mirror shows.
  5 slanted walls: a six-sided room, every wall a door onto the one opposite,
    and a three-sided one with two doors a wall, each onto its neighbour
    round the corner.
The checks are in src/zscript/engtest.zs (MODE=1..5 tools/smoke.sh).
"""
import math
from udmf import Map, rect

m = Map()
DEPTH, STUB, DOOR_H = 16, 48, 96
BUTTON_T, GHOST_T = 20090, 20091


def P(x, y):
    return (round(x, 3), round(y, 3))


def gate(m1, m2, out, floor, line_id, target, tag=0, color=None):
    """A door recess as ajarmap.recess makes it, but its portal line leads to
    the line `target` from the start, and all of it can carry a sector tag."""
    b1, b2 = P(m1[0] + out[0] * DEPTH, m1[1] + out[1] * DEPTH), P(m2[0] + out[0] * DEPTH, m2[1] + out[1] * DEPTH)
    c1, c2 = P(b1[0] + out[0] * STUB, b1[1] + out[1] * STUB), P(b2[0] + out[0] * STUB, b2[1] + out[1] * STUB)
    look = dict(wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
    m.sector([m1, m2, b2, b1], floor=floor, ceil=floor + DOOR_H, light=176, color=color, id=tag, **look)
    m.sector([b1, b2, c2, c1], floor=floor, ceil=floor + DOOR_H, light=96, id=tag, **look)
    m.line(b1, b2, id=line_id, special=156, args=(target, 0, 1, 1))


def button(a, b, tid):
    m.line(a, b, special=130, args=(tid,), playeruse=True, repeatspecial=True, mid="AJEXIT", exact=True)


# --- the corridor, and a neck into each bay ---------------------------------
m.sector(rect(0, -192, 6000, -64), light=160)
for x in (64, 1100, 2272, 4100):
    m.sector(rect(x, -64, x + 96, 32), light=160)
m.thing(112, -128, 1, angle=90)

# --- 1: the lift ------------------------------------------------------------
LIFT = 0xC0D8FF
m.sector(rect(0, 32, 256, 288), color=LIFT)                               # the lower hall
m.sector(rect(256, 96, 384, 224), ceil=128, id=1, color=0xFFE8C0)         # the car
m.sector(rect(384, 32, 640, 288), floor=192, ceil=384, color=0xD0FFD0)    # the landing
gate((288, 224), (352, 224), (0, 1), 0, 301, 302, tag=1)                  # in the car's north wall
gate((0, 128), (0, 192), (-1, 0), 0, 302, 301, color=LIFT)                # in the hall's west wall
m.cut((288, 96), (352, 96), (176, 32), (240, 32), (400, 32), (464, 32))
button((288, 96), (352, 96), 901)
button((176, 32), (240, 32), 901)
button((400, 32), (464, 32), 901)
m.thing(320, 160, BUTTON_T, id=901, args=(1,))
m.thing(64, 256, 2028)                                                    # a lamp in the hall
m.thing(600, 256, 35)                                                     # a candelabra on the landing

# --- 2: the loop ------------------------------------------------------------
LOOP = 0xFFD8C0
m.sector(rect(1000, 32, 1256, 224), color=LOOP)
m.sector(rect(1256, 32, 1512, 224), color=LOOP)
m.line((1256, 32), (1256, 224), special=12, args=(2, 64, 20), missilecross=True, repeatspecial=True)
gate((1000, 96), (1000, 160), (-1, 0), 0, 311, 312, color=LOOP)
gate((1512, 96), (1512, 160), (1, 0), 0, 312, 311, color=LOOP)
m.sector(rect(1320, 224, 1384, 240), ceil=0, id=2, wall="AJTRIM")         # the shutter
m.sector(rect(1320, 240, 1384, 304), ceil=96, light=255, color=0x80FF90)  # what is behind it
m.cut((1400, 32), (1464, 32))
button((1400, 32), (1464, 32), 902)
m.thing(1300, 60, BUTTON_T, id=902, args=(2,))

# --- 3: the inside-out room -------------------------------------------------
HX, HY, HS = 2000, 32, 384                                                # the hall
m.sector(rect(HX, HY, HX + HS, HY + HS), color=0xE8E8E8)
c = HS // 2
gate((HX + c - 32, HY + HS), (HX + c + 32, HY + HS), (0, 1), 0, 331, 341)     # north
gate((HX + HS, HY + c - 32), (HX + HS, HY + c + 32), (1, 0), 0, 332, 342)     # east
gate((HX + c - 32, HY), (HX + c + 32, HY), (0, -1), 0, 333, 343)              # south
gate((HX, HY + c - 32), (HX, HY + c + 32), (-1, 0), 0, 334, 344)              # west
m.thing(HX + 60, HY + HS - 60, 2028)
BX, BY, B, Q = 2500, 3000, 96, 600                                        # the booth's middle, half its side; the square's half
sides = dict(n=(0xFF9080, 30), e=(0x80FF90, 32), s=(0x90B0FF, 85), w=(0xFFF080, 35))
m.sector([(BX - B, BY + B), (BX + B, BY + B), (BX + Q, BY + Q), (BX - Q, BY + Q)], ceil=256, light=230, color=sides["n"][0])
m.sector([(BX + B, BY + B), (BX + B, BY - B), (BX + Q, BY - Q), (BX + Q, BY + Q)], ceil=256, light=230, color=sides["e"][0])
m.sector([(BX + B, BY - B), (BX - B, BY - B), (BX - Q, BY - Q), (BX + Q, BY - Q)], ceil=256, light=230, color=sides["s"][0])
m.sector([(BX - B, BY - B), (BX - B, BY + B), (BX - Q, BY + Q), (BX - Q, BY - Q)], ceil=256, light=230, color=sides["w"][0])
gate((BX - 32, BY + B), (BX + 32, BY + B), (0, -1), 0, 341, 331)
gate((BX + B, BY - 32), (BX + B, BY + 32), (-1, 0), 0, 342, 332)
gate((BX - 32, BY - B), (BX + 32, BY - B), (0, 1), 0, 343, 333)
gate((BX - B, BY - 32), (BX - B, BY + 32), (1, 0), 0, 344, 334)
for (dx, dy), (_, kind) in zip(((0, 1), (1, 0), (0, -1), (-1, 0)), sides.values()):
    for k in (-1, 1):                                                     # a pair of each side's own thing
        m.thing(BX + dx * 400 + dy * k * 120, BY + dy * 400 + dx * k * 120, kind)

# --- 4: mirrors -------------------------------------------------------------
MX, MY = 4000, 32
MIR = 0xE0D0FF
m.sector(rect(MX, MY, MX + 384, MY + 320), color=MIR)
m.cut((MX, MY + 64), (MX, MY + 256))
m.line((MX, MY + 64), (MX, MY + 256), special=182)                        # Line_Mirror
gate((MX + 384, MY + 128), (MX + 384, MY + 192), (1, 0), 0, 351, 352, color=MIR)
SX, SY = 4000, 2000                                                       # the side room
SIDE = 0xFFC0A0
m.sector(rect(SX, SY, SX + 320, SY + 256), color=SIDE)
gate((SX, SY + 96), (SX, SY + 160), (-1, 0), 0, 352, 351, color=SIDE)
m.cut((SX + 320, SY + 32), (SX + 320, SY + 224))
m.line((SX + 320, SY + 32), (SX + 320, SY + 224), special=182)
m.thing(MX + 120, MY + 250, GHOST_T)                                      # seen only in a mirror, it is hoped
m.thing(MX + 120, MY + 70, 2028)                                          # a lamp, to compare it with
m.thing(SX + 200, SY + 200, GHOST_T)
m.thing(SX + 200, SY + 56, 2028)

# --- 5: slanted walls -------------------------------------------------------
def many_sided(cx, cy, n, side, offsets, first_id, links, neck, color):
    """A regular room of n walls, the bottom one level; on each wall a door
    recess at each of `offsets` from its middle, line ids from first_id on in
    the order walls then offsets; `links` says which opening each one leads
    to. `neck` is where along the bottom wall the way in from the corridor is."""
    r = side / 2 / math.sin(math.pi / n)
    vs = [P(cx + r * math.cos(math.radians(-90 - 180 / n + k * 360 / n)),
            cy + r * math.sin(math.radians(-90 - 180 / n + k * 360 / n))) for k in range(n)]
    poly, gates = [], []
    for k in range(n):
        a, b = vs[k], vs[(k + 1) % n]
        d = ((b[0] - a[0]) / side, (b[1] - a[1]) / side)
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        out = (d[1], -d[0])
        at = lambda u: P(mid[0] + d[0] * u, mid[1] + d[1] * u) if k else P(mid[0] + u, a[1])
        poly.append(a)
        marks = [(o - 32, o + 32, True) for o in offsets] + ([neck + (False,)] if k == 0 else [])
        for u1, u2, is_gate in sorted(marks):
            p1, p2 = at(u1), at(u2)
            poly += [p for p in (p1, p2) if p != poly[-1] and p != b]
            if is_gate:
                gates.append((p1, p2, out))
            else:
                m.sector([(p1[0], -64), p1, p2, (p2[0], -64)], light=160)
    m.sector(poly, light=220, color=color)
    for i, (p1, p2, out) in enumerate(gates):
        gate(p1, p2, out, 0, first_id + i, first_id + links[i], color=color)
    return vs


# six walls, one door each (361..366), each onto the wall opposite
many_sided(5000, 240, 6, 192, (0,), 361, [3, 4, 5, 0, 1, 2], (40, 96), 0xD0F0FF)
m.thing(4950, 300, 2028)
# three walls, two doors each (371..376: wall 0 left, wall 0 right, wall 1 left...);
# a wall's right door opens onto the next wall's left one, round the corner
many_sided(5600, 180, 3, 320, (-96, 96), 371, [5, 2, 1, 4, 3, 0], (-28, 28), 0xFFE0F0)
m.thing(5600, 260, 2028)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
