#!/bin/bash
# Headless smoke test: runs the host GZDoom inside docker under Xvfb with
# software GL and plays a scripted walkthrough (ajar_autotest in ajar.zs).
#   MAP=MAP01 (default) plays the level's solution; MAP=TEST is the test box,
#   where MODE=2 uses real USE key presses instead of script calls.
# Screenshots and the log go to $1 (default build/smoke).
set -e
cd "$(dirname "$0")/.."
OUT="${1:-$PWD/build/smoke}"
IWAD="${IWAD:-$HOME/.config/gzdoom/doom2.wad}"
MAP="${MAP:-MAP01}"
MODE="${MODE:-1}"
mkdir -p "$OUT"
docker run --rm -v "$PWD":/work:ro -v /opt/gzdoom:/opt/gzdoom:ro -v "$IWAD":/iwad/doom2.wad:ro \
  -v "$OUT":/out -e HOME=/tmp/home -e LD_LIBRARY_PATH=/opt/gzdoom -e LIBGL_ALWAYS_SOFTWARE=1 \
  -e MAP="$MAP" -e MODE="$MODE" ajar-tools \
  bash -c 'mkdir -p $HOME; cd /out; timeout 150 xvfb-run -a -s "-screen 0 1024x640x24" \
    /opt/gzdoom/gzdoom -iwad /iwad/doom2.wad -file /work/build/ajar.pk3 -nosound -shotdir /out \
    +vid_preferbackend 1 +vid_fullscreen 0 +set ajar_autotest $MODE +map $MAP +exec /work/tools/smoke_${MAP}_${MODE}.cfg \
    > /out/log.txt 2>&1; echo "exit=$?"; chmod -R a+rw /out'
grep -E "AJARTEST [a-zA-Z0-9]+=|rror|arning|Unknown|nvalid" "$OUT/log.txt" || true
