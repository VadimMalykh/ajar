#!/bin/bash
# MAP31's look board (design/secret1-board.html): builds the game once per
# look (AJAR_CINEMA 2, 3, 0 the plain level, then 1) and photographs the tour
# (25 views, monsters off) into build/board31/<look>/view_NN.jpg, 819 by 512,
# with a contact sheet build/board31/sheet_<look>.jpg. The swatches go to
# build/board31/tex/. The pk3 is left in the last look built: end with 1,
# the look the game wears.
#   tools/board31_shots.sh          all four
#   tools/board31_shots.sh 2 1      look 2 again, then the game's own
#   SHOOT=1 tools/board31_shots.sh 1    photograph the pk3 as it is, as look 1
set -e -o pipefail
cd "$(dirname "$0")/.."
B="$PWD/build/board31"
mkdir -p "$B/tex"
U="$(id -u):$(id -g)"
[ -n "$SHOOT" ] || docker run --rm -u "$U" -v "$PWD":/work -w /work ajar-tools python3 tools/gfx_cinema.py build/board31/tex
[ $# -gt 0 ] || set -- 2 3 0 1
for v in "$@"; do
  out="$B/raw_$v"
  rm -rf "$out" "$B/$v"; mkdir -p "$out" "$B/$v"
  [ -n "$SHOOT" ] || docker run --rm -u "$U" -e AJAR_QUICK=1 -e "AJAR_CINEMA=$v" -v "$PWD":/work -w /work ajar-tools python3 tools/build.py | tail -1
  MAP=MAP31 MODE=2 TIMEOUT=400 EXTRA=-nomonsters ./tools/smoke.sh "$out" | grep -i -E "rror|arning|Unknown|nvalid" || true
  i=0
  for f in $(ls "$out"/Screenshot_*.png | sort); do mv "$f" "$out/$(printf 'view_%02d.png' $i)"; i=$((i+1)); done
  docker run --rm -u "$U" -v "$B":/w -w /w --entrypoint sh dpokidov/imagemagick -c \
    "mogrify -path $v -format jpg -resize 819x512 -quality 86 raw_$v/view_*.png && montage $v/view_*.jpg -tile 5x -geometry 400x250+3+3 -background '#222' sheet_$v.jpg"
  echo "look $v: $i shots"
done
