#!/bin/bash
# Photographs every candidate look of the lodger (tools/gfx_lodger.py) in
# MAP02's kitchen, for design/lodger-board.html: five poses per look into
# build/board_lodger/<look>/pose_N.jpg, the sprites themselves into
# build/board_lodger/s/.
set -e -o pipefail
cd "$(dirname "$0")/.."
B="$PWD/build/board_lodger"
build() { docker run --rm -u "$(id -u):$(id -g)" -e "AJAR_LODGER=$1" -v "$PWD":/work ajar-tools python3 tools/build.py | tail -1; }
docker run --rm -u "$(id -u):$(id -g)" -v "$PWD":/work ajar-tools python3 tools/gfx_lodger.py build/board_lodger/s
[ $# -gt 0 ] || set -- 1 2 3 4 5 6
for v in "$@"; do
  out="$B/raw_$v"
  rm -rf "$out"; mkdir -p "$B/$v"
  build "$v"
  EXTRA="+set ajar_lodger_look 8" MAP=MAP02 MODE=3 ./tools/smoke.sh "$out" | grep -i -E "rror|arning|Unknown|nvalid" || true
  i=0
  for f in $(ls "$out"/Screenshot_*.png | sort); do
    convert "$f" -crop 640x440+90+20 +repage -quality 88 "$B/$v/pose_$i.jpg"; i=$((i+1))
  done
  echo "look $v: $i shots"
done
build ""
