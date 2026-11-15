#!/bin/bash
# Second round of the lodger's look (design/lodger-board.html): photographs
# the shadow of a Doom monster (ajar_lodger_look 1..6) and the smoke figure
# (7) in MAP02's kitchen, into build/board_lodger/r2/<look>/pose_N.jpg.
set -e -o pipefail
cd "$(dirname "$0")/.."
B="$PWD/build/board_lodger"
build() { docker run --rm -u "$(id -u):$(id -g)" -e "AJAR_LODGER=$1" -v "$PWD":/work ajar-tools python3 tools/build.py | tail -1; }
[ $# -gt 0 ] || set -- 1 2 3 4 5 6 7
build 7
for v in "$@"; do
  out="$B/raw2_$v"
  rm -rf "$out"; mkdir -p "$B/r2/$v"
  EXTRA="+set ajar_lodger_look $v" MAP=MAP02 MODE=3 ./tools/smoke.sh "$out" | grep -i -E "rror|arning|Unknown|nvalid" || true
  i=0
  for f in $(ls "$out"/Screenshot_*.png | sort); do
    convert "$f" -crop 640x440+90+20 +repage -quality 88 "$B/r2/$v/pose_$i.jpg"; i=$((i+1))
  done
  rm -rf "$out"
  echo "look $v: $i shots"
done
build ""
