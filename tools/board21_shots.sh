#!/bin/bash
# MAP21's apparatus look board (design/map21-board.html): builds the game once per look of the apparatus
# (AJAR_APPARATUS 1, 2, 3; quick builds into build/look<v>.pk3, the game's own build/ajar.pk3 untouched) and
# photographs the MODE=7 views (18 places, each THEN and NOW: 36 views, monsters off) into
# build/board21/<look>/view_NN.jpg, 819 wide with the test's text lines cut off the top. Swatches of the
# parts go to build/board21/tex/. The page is copied to build/board21/index.html: that folder is the whole
# board (and nothing else). The raw shots and a contact sheet per look go to build/board21_work/.
#   tools/board21_shots.sh          all three
#   tools/board21_shots.sh 2        look 2 again
set -e -o pipefail
cd "$(dirname "$0")/.."
B="$PWD/build/board21"
W="$PWD/build/board21_work"
mkdir -p "$B/tex" "$W"
U="$(id -u):$(id -g)"
docker run --rm -u "$U" -e PYTHONDONTWRITEBYTECODE=1 -v "$PWD":/work -w /work/tools ajar-tools python3 -c '
import gfx_longrun as L
out = {}
L.make(out)
for n in L.LOOKS:
    for nm in ("AJUCB%dA" % n, L.name("RK", n), L.name("TK", n), L.name("PM", n), L.name("BM", n), L.name("CN", n),
               L.name("OB", n), L.name("BB", n)):
        key = next(k for k in out if k.endswith("/" + nm + ".png"))
        open("/work/build/board21/tex/" + nm + ".png", "wb").write(out[key])
'
[ $# -gt 0 ] || set -- 1 2 3
for v in "$@"; do
  out="$W/raw_$v"
  rm -rf "$out" "$B/$v"; mkdir -p "$out" "$B/$v"
  AJAR_QUICK=1 AJAR_APPARATUS=$v AJAR_OUT=build/look$v.pk3 ./build.sh 2>&1 | grep -E "^built /work/build/look|rror|Trace" || true
  PK3=build/look$v.pk3 MAP=MAP21 MODE=7 TIMEOUT=200 EXTRA="-nomonsters +set r_drawplayersprites 0" ./tools/smoke.sh "$out" \
    | grep -i -E "rror|nvalid|Unknown|lookViewsDone" || true
  i=0
  for f in $(ls "$out"/Screenshot_*.png | sort); do
    k=$((i / 2)); [ $((i % 2)) = 1 ] && [ $k -lt 36 ] && cp "$f" "$out/$(printf 'view_%02d.png' $k)"; i=$((i + 1))
  done
  docker run --rm -u "$U" -v "$PWD/build":/w -w /w --entrypoint sh dpokidov/imagemagick -c \
    "for f in board21_work/raw_$v/view_*.png; do magick \$f -crop +0+40 +repage -resize 819x -quality 86 board21/$v/\$(basename \$f .png).jpg; done &&
     montage board21/$v/view_*.jpg -tile 6x -geometry 400x230+3+3 -background '#222' board21_work/sheet_$v.jpg"
  echo "look $v: $(ls "$B/$v" | wc -l) views"
done
cp design/map21-board.html "$B/index.html"
