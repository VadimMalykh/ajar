#!/bin/bash
# Plays Ajar (MAP=TEST ./run.sh for the mechanics test box). Uses doom2.wad
# only as a temporary host IWAD (palette, fonts, menus) until the standalone
# build (M0) exists.
cd "$(dirname "$0")"
[ -f build/ajar.pk3 ] || ./build.sh
exec gzdoom -iwad doom2.wad -file build/ajar.pk3 +map "${MAP:-MAP01}" "$@"
