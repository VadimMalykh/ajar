#!/bin/bash
# Headless check of a GZDoom config: starts MAP01 with the given ini (a copy
# is used, the original is not written) and saves one screenshot.
#   tools/cfgtest.sh <ini or "none"> <outdir> [extra gzdoom args...]
cd "$(dirname "$0")/.."
INI="$1"; OUT="$PWD/build/cfgtest/$2"; shift 2
rm -rf "$OUT"; mkdir -p "$OUT"
CFG=""
if [ "$INI" != none ]; then cp "$INI" "$OUT/test.ini"; CFG="-config /out/test.ini"; fi
docker run --rm -v "$PWD":/work:ro -v /opt/gzdoom:/opt/gzdoom:ro -v "$HOME/.config/gzdoom/doom2.wad":/iwad/doom2.wad:ro \
  -v "$OUT":/out -e HOME=/tmp/home -e LD_LIBRARY_PATH=/opt/gzdoom -e LIBGL_ALWAYS_SOFTWARE=1 -e CFG="$CFG" ${NOPK3:+-e PK3=} -e EXTRA="$*" ajar-tools \
  bash -c 'mkdir -p $HOME; cd /out; timeout 120 xvfb-run -a -s "-screen 0 1024x640x24" \
    /opt/gzdoom/gzdoom $CFG -iwad /iwad/doom2.wad ${PK3--file /work/build/ajar.pk3} -nosound -shotdir /out \
    +vid_fullscreen 0 $EXTRA +map MAP01 "+wait 150; screenshot; wait 10; quit" > /out/log.txt 2>&1; chmod -R a+rw /out'
ls -la "$OUT"/*.png 2>/dev/null | awk '{print $5, $NF}'
