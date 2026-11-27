#!/bin/bash
# MAP23's look board (tools/dogs23.py, PLAN.md "Look: MAP23, the animal house"): photographs the tour
# (MAP=MAP23 MODE=5, src/zscript/map23.zs Tour, tools/smoke_MAP23_5.cfg: a camera of its own, the player at the
# start, NOW's ordinary company cleared, the specimens THEN and their bones NOW kept) of a built package into
# build/board23/look<n>/view_NN.jpg (819 wide, the test's text lines cropped off the top), a contact sheet
# build/board23/sheet_look<n>.jpg (each view's number on it) and the look's textures, flats and sprites in
# build/board23/tex_<n>/ with their sheet build/board23/tex_<n>/sheet.jpg.
#   AJAR_QUICK=1 AJAR_DOGS=1 AJAR_OUT=build/look1.pk3 ./build.sh
#   flock build/.disklock tools/board23_shots.sh 1 build/look1.pk3     (0 and the plain package: the plain level;
#                                                                        mix: the picks, look4/, textures of all three)
# FROM=dir: the screenshots of a tour already run (Screenshot_*.png in dir).
#
# The views, by number (NOW's coordinates; THEN is y - 8192; facing in degrees, east 0, north 90). A place shot at
# both times is THEN first and NOW next; the hall's are NOW only, the isolation passage's THEN only:
#   yard        00 THEN, 01 NOW  (600, -200) 110   the front, the door, the shelter
#               02 THEN, 03 NOW  (120, 40) 15      the glass, the gateway
#               04 THEN, 05 NOW  (300, 224) 180    the shelter straight on
#   hall        06 NOW           (60, 640) 45
#               07 NOW           (700, 1180) 225
#   runs        08 THEN, 09 NOW  (-60, 1088) 180   the kennels' run
#               10 THEN, 11 NOW  (1280, 1500) 270  the stalls' run to its funnel
#               12 THEN, 13 NOW  (784, 520) 270    the big run
#               14 THEN, 15 NOW  (40, 1376) 0      the isolation run THEN, the antechamber NOW
#   pens        16 THEN, 17 NOW  (-760, 1100) 270  into pen 1
#               18 THEN, 19 NOW  (-420, 1180) 250  the gates of pens 2 and 3
#               20 THEN, 21 NOW  (1280, 600) 270   the stall
#               22 THEN, 23 NOW  (784, -900) 270   the crush
#               24 THEN, 25 NOW  (700, 1376) 0     the isolation pen THEN, the guard room's end NOW
#   passages    26 THEN, 27 NOW  (-60, 608) 180    the kennels' passage
#               28 THEN, 29 NOW  (-700, 600) 90    pen 1's hatch, lever and readout
#               30 THEN, 31 NOW  (1500, 200) 180   the stalls' passage
#               32 THEN, 33 NOW  (1040, -1400) 180 the big run's passage
#               34 THEN          (40, 1552) 0      the isolation passage
#   plates      35 THEN, 36 NOW  (600, 224) 180    1 LINE 6, THE INSTITUTE (the shelter)
#               37 THEN, 38 NOW  (320, 352) 90     2 ANIMAL HOUSE
#               39 THEN, 40 NOW  (144, 352) 90     2 the plan (the yard)
#               41 NOW           (496, 752) 270    2 the plan (the hall)
#               42 THEN, 43 NOW  (-608, 668) 270   4 the rules (kennels' passage)
#               44 THEN, 45 NOW  (1376, 218) 270   4 the rules (stalls' passage)
#               46 THEN          (480, 1492) 90    4 the rules (isolation passage)
#               47 THEN, 48 NOW  (736, -1364) 270  4 the rules (big run's passage)
#               49 THEN, 50 NOW  (-928, 668) 270   5 the weigh record
#               51 THEN, 52 NOW  (480, 32) 0       6 DO NOT TAP ON THE GLASS
#               53 THEN, 54 NOW  (-1030, 1088) 0   6 KEEPERS ONLY (kennels)
#               55 THEN, 56 NOW  (1530, 1376) 180  6 KEEPERS ONLY (stalls)
#               57 THEN          (208, 1610) 270   6 KEEPERS ONLY (isolation)
#               58 THEN, 59 NOW  (-480, 1056) 90   7 the kennels' name board
#               60 THEN, 61 NOW  (1248, 1024) 0    7 the stalls' name board
#               62 THEN, 63 NOW  (480, 1440) 270   7 the isolation run's name board
#               64 THEN, 65 NOW  (752, 288) 0      7 the big run's name board
#   things      66 THEN, 67 NOW  (-488, 860) 270   a bowl at pen 2's hatch, from inside the pen
#               68 THEN, 69 NOW  (-760, 610) 180   a bucket and a store in the kennels' passage
set -e -o pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
n="$1"; pk3="$2"
[ "$n" = mix ] && n=4
P="$n"; [ "$n" = 4 ] && P="[123]"
B="$PWD/build/board23"
raw="$B/raw_$n"
rm -rf "$raw" "$B/look$n"; mkdir -p "$raw" "$B/look$n"
U="$(id -u):$(id -g)"
if [ -n "$FROM" ]; then cp "$FROM"/Screenshot_*.png "$raw"/
else PK3="$pk3" MAP=MAP23 MODE=5 TIMEOUT=${TIMEOUT:-900} ./tools/smoke.sh "$raw" | grep -E "tour over|rror|nvalid" || true
fi
# two shots a view: the later kept
i=0
for f in $(ls "$raw"/Screenshot_*.png | sort); do
  [ $((i % 2)) = 1 ] && mv "$f" "$raw/$(printf 'view_%02d.png' $((i / 2)))"
  i=$((i + 1))
done
docker run --rm -u "$U" -e PYTHONDONTWRITEBYTECODE=1 -v "$ROOT":/w -w /w ajar-pil \
  python3 tools/board23_sheets.py views "build/board23/raw_$n" "build/board23/look$n" "build/board23/sheet_look$n.jpg"
if [ "$n" != 0 ]; then
  rm -rf "$B/tex_$n"; mkdir -p "$B/tex_$n"
  (cd "$B/tex_$n" && unzip -q -j "$ROOT/$pk3" "textures/AJD$P*" "flats/AJD$P*" "sprites/AJV*" 2>/dev/null || true)
  docker run --rm -u "$U" -e PYTHONDONTWRITEBYTECODE=1 -v "$ROOT":/w -w /w ajar-pil \
    python3 tools/board23_sheets.py swatches "build/board23/tex_$n" "build/board23/tex_$n/sheet.jpg"
fi
echo "look $n: $(ls "$B/look$n" | wc -l) views"
