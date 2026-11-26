#!/bin/bash
# The clocked door's look board (design/clockdoor-board.html): builds the game once per look of the door and its
# frame's trim (AJAR_CLOCKDOOR 0, 1, 2, 3; quick builds into build/clock<n>.pk3, the game's own build/ajar.pk3
# untouched) and photographs MAP21's MODE=8 views (src/zscript/clockdoorviews.zs: 8 views, monsters off) into
# build/boardclock/<n>/view_NN.jpg, 819 wide with the test's text lines cut off the top. The leaf, the wall trim
# and the flat of each look go to build/boardclock/tex/ (leaf<n>.png, wall<n>.png, flat<n>.png). The page is
# copied to build/boardclock/index.html: that folder is the whole board (and nothing else). The raw shots and a
# contact sheet per look go to build/boardclock_work/. Look 3 is the game's since 2026-11-26 (Vadim's choice; the
# build's default, gfx.CLOCKDOOR); 0 is the old art, built here with AJAR_CLOCKDOOR=0.
#   tools/clockdoor_shots.sh          all four
#   tools/clockdoor_shots.sh 2        look 2 again
set -e -o pipefail
cd "$(dirname "$0")/.."
B="$PWD/build/boardclock"
W="$PWD/build/boardclock_work"
mkdir -p "$B/tex" "$W"
U="$(id -u):$(id -g)"
docker run --rm -u "$U" -e PYTHONDONTWRITEBYTECODE=1 -e AJAR_CLOCKDOOR=0 -v "$PWD":/work -w /work/tools ajar-tools python3 -c '
import gfx, gfx_then, gfx_clockdoor as C
o = "/work/build/boardclock/tex/"
for n in range(4):
    if n:
        leaf, (wall, flat) = C.leaf(n), C.trim(n)
    else:
        leaf, wall = gfx.clocked_door(), gfx_then.clock_trim()
        flat = wall
    for nm, im in (("leaf", leaf), ("wall", wall), ("flat", flat)):
        open(o + nm + str(n) + ".png", "wb").write(im.png())
'
[ $# -gt 0 ] || set -- 0 1 2 3
for v in "$@"; do
  out="$W/raw_$v"
  rm -rf "$out" "$B/$v"; mkdir -p "$out" "$B/$v"
  AJAR_QUICK=1 AJAR_CLOCKDOOR=$v AJAR_OUT=build/clock$v.pk3 ./build.sh 2>&1 | grep -E "^built /work/build/clock|rror|Trace" || true
  PK3=build/clock$v.pk3 MAP=MAP21 MODE=8 TIMEOUT=300 EXTRA="-nomonsters" ./tools/smoke.sh "$out" \
    | grep -i -E "rror|nvalid|Unknown|clockViewsDone" || true
  i=0
  for f in $(ls "$out"/Screenshot_*.png | sort); do
    k=$((i / 2)); [ $((i % 2)) = 1 ] && [ $k -lt 8 ] && cp "$f" "$out/$(printf 'view_%02d.png' $k)"; i=$((i + 1))
  done
  docker run --rm -u "$U" -v "$PWD/build":/w -w /w --entrypoint sh dpokidov/imagemagick -c \
    "for f in boardclock_work/raw_$v/view_*.png; do magick \$f -crop +0+48 +repage -resize 819x -quality 88 boardclock/$v/\$(basename \$f .png).jpg; done &&
     montage boardclock/$v/view_*.jpg -tile 4x -geometry 400x230+3+3 -background '#222' boardclock_work/sheet_$v.jpg"
  echo "look $v: $(ls "$B/$v" | wc -l) views"
done
cp design/clockdoor-board.html "$B/index.html"
