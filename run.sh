#!/bin/bash
# Plays Ajar (MAP=MAP02 or MAP03 ./run.sh for the later levels, MAP=TEST for the mechanics test box, MAP=LAB for the Pair door). Uses doom2.wad
# only as a temporary host IWAD (palette, fonts, menus) until the standalone
# build (M0) exists.
#
# Ajar is designed for the hardware renderer at normal gamma, so it runs with
# its own config, ajar.ini: a copy of your GZDoom config (keys, mouse, IWAD
# paths) with the settings below left out, which puts them at GZDoom's
# defaults. Your own config is never written. Delete ajar.ini to make it again.
# SKILL=1..4 picks the difficulty (1 "Just visiting", 2 "Short stay",
# 3 "Resident": the game as designed and the default, 4 "Night shift").
# The game's output is kept in build/run.log.
# DEMO=3 ./run.sh plays MAP32's room 3 by itself, the way its fight is meant
# to be fought (a bait under the press, a later self at the lever), with a
# caption saying what each self does (src/zscript/fightdemo.zs; PLAN.md, "MAP32
# room 3: the fight as fought" and "an open front"). It plays honestly and, on
# the room with its open front (2026-11-21), does not win: in ten runs of three
# times through the four goes it never got below 10 left, and after the fourth
# go the fight begins anew. Watch it; keys and mouse would play along with it.
cd "$(dirname "$0")"
[ -f build/ajar.pk3 ] || ./build.sh
LOOK='vid_rendermode|vid_gamma|vid_brightness|vid_contrast|vid_saturation|gl_lightmode|gl_tonemap'
if [ ! -f ajar.ini ] && [ -f "$HOME/.config/gzdoom/gzdoom.ini" ]; then
  grep -v -E "^($LOOK)=" "$HOME/.config/gzdoom/gzdoom.ini" > ajar.ini
fi
# With GZDoom 4.12.2 here, the hardware renderer draws a black screen on the
# OpenGL backend (0), and GZDoom falls back to that one, and saves it, when
# Vulkan (1) will not start. The GLES backend (2) works, so it is set again
# before every start.
[ -f ajar.ini ] && sed -i -e 's/^vid_preferbackend=.*/vid_preferbackend=2/' -e 's/^vid_rendermode=.*/vid_rendermode=4/' ajar.ini
# -noautoload: the config is a copy of yours, and so are its Autoload lists.
# Whatever you load on top of Doom II by habit (a megawad with its own
# monsters and palette) must not be under Ajar.
DEMOARGS=()
[ "${DEMO:-}" = 3 ] && { DEMOARGS=(+set ajar_autotest 20); MAP=MAP32; }
gzdoom -config "$PWD/ajar.ini" -noautoload -iwad doom2.wad -file build/ajar.pk3 +skill "$((${SKILL:-3} - 1))" "${DEMOARGS[@]}" +map "${MAP:-MAP01}" "$@" 2>&1 | tee build/run.log
