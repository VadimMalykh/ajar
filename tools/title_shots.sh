#!/bin/bash
# The title's look board (AJAR_TITLE; tools/gfx_title.py): builds the game once per look of the title, the
# menus and the help page (quick builds into build/title<n>.pk3; the game's own build/ajar.pk3 untouched) and
# photographs each, headless at 1024x640, into build/boardtitle/<n>/:
#   view_a  a cold start (no +map): the title with the menu open (looks 1-3 open it by themselves; for 0,
#           Doom II's title, menu_main opens it)
#   view_b  the same with the menu shut: the bare title
#   view_c  in play (MAP01's hall, -nomonsters, looking at its frame and the pictures of doors): Esc's menu
#   view_d  the skill menu (New Game)
#   view_e  the help page (House Rules, F1)
#   view_f  a quit message
# Look 0 is the game as it is (the "before" column). Close-ups of each look's logo, cursor frames and a line
# of its lettering, 4 times the 320 grid on a dark and a light ground, go to build/boardtitle/tex/. The raw
# shots and logs go to build/boardtitle_work/. A look whose module (tools/gfx_title<n>.py) is not there yet
# is skipped.
#   tools/title_shots.sh            looks 0 1 2 3
#   tools/title_shots.sh 1          look 1 again
#   NOBUILD=1 tools/title_shots.sh 1   shoot build/title1.pk3 as it is
set -e -o pipefail
cd "$(dirname "$0")/.."
B="$PWD/build/boardtitle"
W="$PWD/build/boardtitle_work"
IWAD="${IWAD:-$HOME/.config/gzdoom/doom2.wad}"
U="$(id -u):$(id -g)"
mkdir -p "$B/tex" "$W"
[ $# -gt 0 ] || set -- 0 1 2 3

# gzdoom <pk3> <out dir> <cfg text> [args]: one headless run, as tools/smoke.sh runs it
gzdoom() {
  local pk3=$1 out=$2 cfg=$3; shift 3
  mkdir -p "$out"; find "$out" -maxdepth 1 -type f -delete
  printf '%s\n' "$cfg" > "$out/shots.cfg"
  docker run --rm -v "$PWD":/work:ro -v /opt/gzdoom:/opt/gzdoom:ro -v "$IWAD":/iwad/doom2.wad:ro -v "$out":/out \
    -e HOME=/tmp/home -e LD_LIBRARY_PATH=/opt/gzdoom -e LIBGL_ALWAYS_SOFTWARE=1 -e PK3="$pk3" -e ARGS="$*" ajar-tools \
    bash -c 'mkdir -p $HOME; cd /out; timeout 200 xvfb-run -a -s "-screen 0 1024x640x24" \
      /opt/gzdoom/gzdoom -iwad /iwad/doom2.wad -file /work/$PK3 -nosound -shotdir /out \
      +vid_preferbackend 1 +vid_fullscreen 0 +win_w 1024 +win_h 640 $ARGS +exec /out/shots.cfg > /out/log.txt 2>&1;
      echo "  gzdoom exit=$?"; chmod -R a+rw /out'
  grep -E "rror|arning|Unknown|nvalid" "$out/log.txt" | sed 's/^/  log: /' || true
}

for n in "$@"; do
  if [ "$n" != 0 ] && [ ! -f "tools/gfx_title$n.py" ]; then echo "look $n: no tools/gfx_title$n.py yet, skipped"; continue; fi
  pk3=build/title$n.pk3
  if [ -z "$NOBUILD" ] || [ ! -f "$pk3" ]; then
    echo "look $n: building $pk3"
    AJAR_TITLE=$n AJAR_QUICK=1 AJAR_OUT=$pk3 ./build.sh 2>&1 | grep -E "^built /work/build/title|rror|Trace" || true
  fi
  open=""; [ "$n" = 0 ] && open="menu_main;"
  # a, b, d, e, f: from a cold start
  # (one line: a wait holds back the rest of its own line only)
  gzdoom "$pk3" "$W/cold_$n" "wait 105; $open wait 10; screenshot; wait 8; closemenu; wait 15; screenshot; wait 8; menu_game; wait 20; screenshot; wait 8; closemenu; wait 5; menu_help; wait 20; screenshot; wait 8; closemenu; wait 5; menu_quit; wait 20; screenshot; wait 5; quit"
  # c: in play, MAP01's hall seen from its north side, facing the frame and the pictures of doors
  gzdoom "$pk3" "$W/play_$n" "wait 140; warp 384 520; turn180; wait 20; menu_main; wait 15; screenshot; wait 5; quit" \
    -nomonsters +map MAP01
  rm -rf "$B/$n"; mkdir -p "$B/$n"
  shots=($(ls "$W/cold_$n"/Screenshot_*.png | LC_ALL=C sort))     # 1234.png before 1234_01.png
  [ ${#shots[@]} = 5 ] || echo "look $n: ${#shots[@]} shots from the cold start, 5 expected"
  for k in 0 1 2 3 4; do
    v=(a b d e f); [ -n "${shots[$k]}" ] && cp "${shots[$k]}" "$B/$n/view_${v[$k]}.png"
  done
  play=$(ls "$W/play_$n"/Screenshot_*.png 2>/dev/null | head -1)
  [ -n "$play" ] && cp "$play" "$B/$n/view_c.png" || echo "look $n: no shot in play"
  if [ "$n" != 0 ]; then
    docker run --rm -u "$U" -e PYTHONDONTWRITEBYTECODE=1 -e AJAR_TITLE=$n -v "$PWD":/work -w /work/tools ajar-tools \
      python3 -c "import gfx_title; print('  close-ups:', ' '.join(gfx_title.specimens($n, '/work/build/boardtitle/tex')))"
  fi
  echo "look $n: $(ls "$B/$n" | wc -l) views in $B/$n"
done
