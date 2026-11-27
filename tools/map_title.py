"""The title maps: what the title shows behind the menu (maps/TITLEMAP.wad; AJAR_TITLE, tools/gfx_title.py).

GZDoom plays a map named TITLEMAP as the title, in place of the title picture (gamestate GS_TITLELEVEL). It
is built here like every other map, and src/zscript/title.zs runs it: AjarTitleHandler (named in the map's
mapinfo block, so it is there only when the switch is on) puts the view on the map's camera, opens the main
menu once at the start and moves the camera, if the map asks for that:

  camera(m, x, y, z, angle, pitch=0, sway=0, period=0, glide=0)
      the camera (thing 20200, AjarTitleCamera): its eye at height z over the floor, looking `angle`
      degrees round and `pitch` down (negative: up). sway: it drifts that many units to and fro across
      its view and back in `period` seconds (0: it holds still). glide: the id of a spot (thing 20201,
      spot()) it glides to and back in `period` seconds instead, turning to the spot's angle as it goes.
  spot(m, x, y, z, angle, pitch, tid)
      where a gliding camera goes.
  closet(m, x, y)
      a small room apart, out of every view, where the title's player pawn stands (a map must have a
      player start; the pawn is never seen, and no HUD or weapon is drawn while the view is the camera's).

A look's title map is a function returning (wad bytes, extra lines of its mapinfo block); look 1's is cell().
"""
import ajarmap
from ajarmap import RED, far_id
import map_hinges1
from udmf import Map, rect

CAMERA_T, SPOT_T = 20200, 20201


def camera(m, x, y, z, angle, pitch=0, sway=0, period=0, glide=0):
    m.thing(x, y, CAMERA_T, angle=int(angle), height=z, args=(int(sway), int(period), int(glide), int(pitch)))


def spot(m, x, y, z, angle, pitch, tid):
    m.thing(x, y, SPOT_T, angle=int(angle), height=z, id=tid, args=(0, 0, 0, int(pitch)))


def closet(m, x, y):
    """A 128 x 128 room with the player start in it; returns its box."""
    m.sector(rect(x, y, x + 128, y + 128), ceil=96, light=96, wall="AJWALL")
    m.thing(x + 64, y + 64, 1, angle=90)
    return (x, y, x + 128, y + 128)


def cell():
    """Look 1, "The Cell": MAP01's cell, built by MAP01's own code (map_hinges1.cell, its RED_LEANS and
    CANDLES), the RED door leaning on its wall (the real AjarDoor, as MAP01 places it) and the empty frame
    with its hinge plates. RED's far side (which the frame's portal names) is in the closet, out of view.
    MAP01 leans RED a hand's breadth (16 units) from the frame, so no view has room for the menu between
    them: the camera stands in the west half of the cell, turned a little to the left of the north wall,
    so that RED is in the middle of the picture, the frame (with its hinge plates) on the right and the
    west wall on the left, where the menu stands (gfx_title1.MENU_X). It sways a few units across and
    back, once in forty seconds.
    """
    m = Map()
    map_hinges1.cell(m)
    box = closet(m, 1024, 1024)
    ajarmap.recess(m, (box[0], box[1] + 32), (box[0], box[1] + 96), (-1, 0), 0, far_id(RED), 101, far_colour=RED)
    ajarmap.door(m, RED, map_hinges1.RED_LEANS["x"], map_hinges1.RED_LEANS["y"], angle=map_hinges1.RED_LEANS["angle"])
    for x, y in map_hinges1.CANDLES:
        m.thing(x, y, 34)                                    # candle
    camera(m, 44, -1372, 52, 97, pitch=-2, sway=3, period=40)
    return m.wad("TITLEMAP"), []
