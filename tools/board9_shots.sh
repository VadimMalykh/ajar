#!/bin/bash
# MAP09's look board (design/map09-board.html): builds the game once per look
# (AJAR_EXCHANGE 1 to 3, then 0, the plain level) and photographs the tour
# (48 views, monsters off) into build/board9/<look>/view_NN.jpg, 819 by 512.
# The swatches go to build/board9/tex/. The pk3 is left in the last look
# built: end with 1, the look the game wears.
#   tools/board9_shots.sh          all four
#   tools/board9_shots.sh 2 1      look 2 again, then the game's own
set -e -o pipefail
cd "$(dirname "$0")/.."
B="$PWD/build/board9"
mkdir -p "$B/tex"
U="$(id -u):$(id -g)"
docker run --rm -u "$U" -v "$PWD":/work ajar-tools python3 tools/gfx_exchange.py build/board9/tex
[ $# -gt 0 ] || set -- 2 3 0 1
for v in "$@"; do
  out="$B/raw_$v"
  rm -rf "$out" "$B/$v"; mkdir -p "$B/$v"
  docker run --rm -u "$U" -e AJAR_QUICK=1 -e "AJAR_EXCHANGE=$v" -v "$PWD":/work ajar-tools python3 tools/build.py | tail -1
  MAP=MAP09 MODE=2 TIMEOUT=400 EXTRA=-nomonsters ./tools/smoke.sh "$out" | grep -i -E "rror|arning|Unknown|nvalid" || true
  i=0
  for f in $(ls "$out"/Screenshot_*.png | sort); do mv "$f" "$out/$(printf 'view_%02d.png' $i)"; i=$((i+1)); done
  docker run --rm -u "$U" -v "$B":/w -w /w --entrypoint sh dpokidov/imagemagick -c \
    "mogrify -path $v -format jpg -resize 819x512 -quality 86 raw_$v/view_*.png"
  echo "look $v: $i shots"
done
