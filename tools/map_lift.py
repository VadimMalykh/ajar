"""The lift (map LIFT): a room to try the moving room in. MAP=LIFT ./run.sh

One lift car and three floors round it: the hall (west, the ground), the
first floor (north, 192 up) and the top (east, 384 up). The car has a frame
(110) and RED's far side in its south wall, and both ORANGE leaves lean in it.
  RED hung anywhere opens onto the car, so onto whichever floor the car is at.
  A leaf hung in the car's frame, its twin anywhere: that place rides.
Buttons: in the car, one beside each opening (ground, first; the one for the
top is dead); in the hall, one that calls the car and one that sends it to
the top; on the first floor, one that calls it. The top has none, and the
way out is there: hang RED in the hall, send the car up, go through RED.
The checks are in src/zscript/lift.zs (MODE=1, 2 tools/smoke.sh).
"""
import ajarmap
from ajarmap import RED, TEAL, ORANGE, LIFT
from udmf import Map, rect

m = Map()
HALL, CAR, FIRST, TOP = 0xD8E8FF, 0xFFE8C0, 0xD0FFD0, 0xFFD8E8
Z1, Z2 = 192, 384           # the first floor and the top
CAR_H = 128

m.sector(rect(0, 0, 608, 384), ceil=192, light=200, color=HALL)                     # the hall
m.sector(rect(608, 144, 640, 240), ceil=112, light=176)                             # its way into the car
m.sector(rect(640, 96, 832, 288), ceil=CAR_H, light=220, color=CAR, id=LIFT)        # the car
m.sector(rect(688, 288, 784, 320), floor=Z1, ceil=Z1 + 112, light=176)              # the first floor's way in
m.sector(rect(624, 320, 848, 640), floor=Z1, ceil=Z1 + 192, light=200, color=FIRST)
m.sector(rect(832, 144, 864, 240), floor=Z2, ceil=Z2 + 112, light=176)              # the top's way in
m.sector(rect(864, 0, 1248, 384), floor=Z2, ceil=Z2 + 192, light=200, color=TOP)

ajarmap.recess(m, (0, 160), (0, 224), (-1, 0), 0, 101, 201, color=HALL)
ajarmap.recess(m, (224, 0), (288, 0), (0, -1), 0, 102, 201, color=HALL)
ajarmap.recess(m, (1248, 160), (1248, 224), (1, 0), Z2, 103, 201, color=TOP)
ajarmap.recess(m, (704, 640), (768, 640), (0, 1), Z1, 104, 201, color=FIRST)
ajarmap.recess(m, (656, 96), (720, 96), (0, -1), 0, 110, 201, color=CAR, tag=LIFT)
ajarmap.recess(m, (752, 96), (816, 96), (0, -1), 0, ajarmap.far_id(RED), 101, far_colour=RED, color=CAR, tag=LIFT)

ajarmap.lift_button(m, (640, 104), (640, 136), 0, 711, (672, 128))          # in the car: beside the way out to the hall
ajarmap.lift_button(m, (648, 288), (680, 288), Z1, 712, (672, 256))         # ...and to the first floor
ajarmap.lift_button(m, (608, 256), (608, 288), 0, 713, (560, 272))          # the hall: call
ajarmap.lift_button(m, (608, 304), (608, 336), Z2, 714, (560, 320))         # the hall: send it to the top
ajarmap.lift_button(m, (800, 320), (832, 320), Z1, 715, (816, 368))         # the first floor: call
m.cut((1248, 288), (1248, 352))
m.line((1248, 288), (1248, 352), special=243, playeruse=True, mid="AJEXIT", exact=True)

m.thing(300, 192, 1, angle=0)
ajarmap.door(m, RED, 120, 340, angle=270)
ajarmap.pair(m, TEAL, (300, 340, 270), (420, 340, 270))
ajarmap.pair(m, ORANGE, (668, 264, 270), (808, 264, 270))

PUZZLE = dict(
    start="hall", goal="top",
    walk=[],
    frames={101: "hall", 102: "hall", 103: "top", 104: "first", 110: "car"},
    doors={RED: dict(home="car", lean="hall"), **ajarmap.leaves(TEAL, "hall", "hall"),
           **ajarmap.leaves(ORANGE, "car", "car")},
    lift=dict(car="car", floors=["hall", "first", "top"], buttons={"car": (0, 1), "hall": (0, 2), "first": (1,)}),
)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
