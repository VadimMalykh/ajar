#!/bin/bash
# Headless smoke test: runs the host GZDoom inside docker under Xvfb with
# software GL and plays a scripted walkthrough (ajar_autotest in ajar.zs).
#   MAP=MAP01 (default) plays the level's solution; MAP=TEST is the test box,
#   where MODE=2 uses real USE key presses instead of script calls.
# Screenshots and the log go to $1 (default build/smoke).
# EXTRA="+set name value" adds to GZDoom's command line.
# PK3=build/mine.pk3 tests another build (see AJAR_OUT in build.py).
set -e
cd "$(dirname "$0")/.."
OUT="${1:-$PWD/build/smoke}"
IWAD="${IWAD:-$HOME/.config/gzdoom/doom2.wad}"
MAP="${MAP:-MAP01}"
MODE="${MODE:-1}"
mkdir -p "$OUT"
# The image may be gone: another project's clean-up removes every image no container uses when the system drive is
# short of room (seen 2026-11-22). Its layers stay in the build cache, so this takes seconds. As in build.sh.
docker image inspect ajar-tools >/dev/null 2>&1 || docker build -q -t ajar-tools tools >/dev/null
docker run --rm -v "$PWD":/work:ro -v /opt/gzdoom:/opt/gzdoom:ro -v "$IWAD":/iwad/doom2.wad:ro \
  -v "$OUT":/out -e HOME=/tmp/home -e LD_LIBRARY_PATH=/opt/gzdoom -e LIBGL_ALWAYS_SOFTWARE=1 \
  -e PK3="${PK3:-build/ajar.pk3}" -e MAP="$MAP" -e MODE="$MODE" -e EXTRA="$EXTRA" -e TIMEOUT="${TIMEOUT:-170}" ajar-tools \
  bash -c 'mkdir -p $HOME; cd /out; timeout ${TIMEOUT:-170} xvfb-run -a -s "-screen 0 1024x640x24" \
    /opt/gzdoom/gzdoom -iwad /iwad/doom2.wad -file /work/$PK3 -nosound -shotdir /out \
    +vid_preferbackend 1 +vid_fullscreen 0 +set ajar_autotest $MODE $EXTRA +map $MAP +exec /work/tools/smoke_${MAP}_${MODE}.cfg \
    > /out/log.txt 2>&1; echo "exit=$?"; chmod -R a+rw /out'
grep -E "AJARTEST [a-zA-Z0-9]+=|rror|arning|Unknown|nvalid" "$OUT/log.txt" || true
