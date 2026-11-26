#!/bin/bash
# MAP33's look board (tools/power33.py): photographs the tour (MAP=MAP33 MODE=5, 35 views, monsters off;
# src/zscript/map33.zs, Tour33) of a built package into build/board33/look<n>/view_NN.jpg, 819 by 512, with
# a contact sheet build/board33/sheet_look<n>.jpg (each view's number on it).
#   AJAR_QUICK=1 AJAR_OUT=build/look1.pk3 AJAR_POWER=1 ./build.sh
#   tools/board33_shots.sh 1 build/look1.pk3        (look 1; 0 and the plain level's package for the plain level)
# The look's textures and flats, one sheet: build/board33/tex_look<n>.jpg (from the package).
set -e -o pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
n="$1"; pk3="$2"
B="$PWD/build/board33"
out="$B/raw_$n"
rm -rf "$out" "$B/look$n"; mkdir -p "$out" "$B/look$n"
U="$(id -u):$(id -g)"
# (FROM=build/dir: the screenshots of a tour already run)
if [ -n "$FROM" ]; then cp "$FROM"/Screenshot_*.png "$out"/
else PK3="$pk3" MAP=MAP33 MODE=5 TIMEOUT=900 EXTRA=-nomonsters ./tools/smoke.sh "$out" | grep -E "view=|tour over|rror|nvalid" || true
fi
i=0
for f in $(ls "$out"/Screenshot_*.png | sort); do mv "$f" "$out/$(printf 'view_%02d.png' $i)"; i=$((i+1)); done
docker run --rm -u "$U" -v "$B":/w -w /w --entrypoint sh dpokidov/imagemagick -c "
  mogrify -path look$n -format jpg -resize 819x512 -quality 86 raw_$n/view_*.png &&
  montage -label '%t' look$n/view_*.jpg -tile 5x -geometry 400x250+3+3 -background '#222' -fill white \
    -pointsize 16 sheet_look$n.jpg"
if [ "$n" != 0 ]; then
  rm -rf "$B/tex_$n"; mkdir -p "$B/tex_$n"
  (cd "$B/tex_$n" && unzip -q -j "$ROOT/$pk3" "textures/AJP$n*" "flats/AJP$n*")
  docker run --rm -u "$U" -v "$B":/w -w /w/tex_$n --entrypoint sh dpokidov/imagemagick -c "
    montage -label '%t' \$(ls AJP${n}[A-Z][A-Z][0-9]*.png) \$(ls AJP${n}??.png) AJP${n}SKY.png -tile 14x -geometry '128x128>+3+3' \
      -background '#222' -fill white -pointsize 11 ../tex_look$n.jpg"
fi
echo "look $n: $i shots"
