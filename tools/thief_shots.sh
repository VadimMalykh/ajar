#!/bin/bash
# The thief's look board (design/thief-board.html): photographs each candidate
# look (ajar_thief_look 1..6, see AjarThief.Portrait) posed in MAP04's yard,
# into build/board_thief/<look>/pose_N.jpg. Needs a built pk3.
set -e -o pipefail
cd "$(dirname "$0")/.."
B="$PWD/build/board_thief"
[ $# -gt 0 ] || set -- 1 2 3 4 5 6
for v in "$@"; do
  out="$B/raw_$v"
  rm -rf "$out"; mkdir -p "$B/$v"
  EXTRA="+set ajar_thief_look $v" MAP=MAP04 MODE=0 ./tools/smoke.sh "$out" | grep -i -E "rror|arning|Unknown|nvalid" || true
  i=0
  for f in $(ls "$out"/Screenshot_*.png | sort); do
    convert "$f" -crop 400x400+210+70 +repage -quality 88 "$B/$v/pose_$i.jpg"; i=$((i+1))
  done
  echo "look $v: $i shots"
done
