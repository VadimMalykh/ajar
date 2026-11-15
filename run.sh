#!/bin/bash
# Plays Ajar (MAP=MAP02 or MAP03 ./run.sh for the later levels, MAP=TEST for the mechanics test box). Uses doom2.wad
# only as a temporary host IWAD (palette, fonts, menus) until the standalone
# build (M0) exists.
cd "$(dirname "$0")"
[ -f build/ajar.pk3 ] || ./build.sh
exec gzdoom -iwad doom2.wad -file build/ajar.pk3 +map "${MAP:-MAP01}" "$@"
