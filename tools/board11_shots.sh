#!/bin/bash
# MAP11's look board (design/map11-board.html): builds the game once per look
# (AJAR_INSTITUTE 2, 3, 0 the plain level, then 1) and photographs the tour
# (37 views, monsters off) into build/board11/<look>/view_NN.jpg, 819 by 512,
# with a contact sheet build/board11/sheet_<look>.jpg. The swatches go to
# build/board11/tex/. The pk3 is left in the last look built: end with 1,
# the look the game wears until one is chosen.
#   tools/board11_shots.sh          all four
#   tools/board11_shots.sh 2 1      look 2 again, then the game's own
set -e -o pipefail
cd "$(dirname "$0")/.."
B="$PWD/build/board11"
mkdir -p "$B/tex"
U="$(id -u):$(id -g)"
docker run --rm -u "$U" -v "$PWD":/work -w /work ajar-tools python3 tools/gfx_institute.py build/board11/tex
[ $# -gt 0 ] || set -- 2 3 0 1
for v in "$@"; do
  out="$B/raw_$v"
  rm -rf "$out" "$B/$v"; mkdir -p "$out" "$B/$v"
  docker run --rm -u "$U" -e AJAR_QUICK=1 -e "AJAR_INSTITUTE=$v" -v "$PWD":/work -w /work ajar-tools python3 tools/build.py | tail -1
  MAP=MAP11 MODE=2 TIMEOUT=400 EXTRA=-nomonsters ./tools/smoke.sh "$out" | grep -i -E "rror|arning|Unknown|nvalid" || true
  i=0
  for f in $(ls "$out"/Screenshot_*.png | sort); do mv "$f" "$out/$(printf 'view_%02d.png' $i)"; i=$((i+1)); done
  docker run --rm -u "$U" -v "$B":/w -w /w --entrypoint sh dpokidov/imagemagick -c \
    "mogrify -path $v -format jpg -resize 819x512 -quality 86 raw_$v/view_*.png && montage $v/view_*.jpg -tile 6x -geometry 400x250+3+3 -background '#222' sheet_$v.jpg"
  echo "look $v: $i shots"
done
