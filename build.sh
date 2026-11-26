#!/bin/bash
# Builds build/ajar.pk3 inside docker (no host tools needed). Design switches
# are passed on: AJAR_HALL=3 ./build.sh
set -e
cd "$(dirname "$0")"
docker image inspect ajar-tools >/dev/null 2>&1 || docker build -t ajar-tools tools
docker run --rm -u "$(id -u):$(id -g)" $(env | grep -o '^AJAR_[A-Z]*' | sed 's/^/-e /') -v "$PWD":/work ajar-tools python3 tools/build.py
# The joined Doom II maps (MAP=CLASSIC; tools/classic.py): made from the player's own doom2.wad, into
# build/ajar-classic.pk3 only, never into ajar.pk3. GZDoom's translation table is read from /opt/gzdoom.
IWAD="${IWAD:-$HOME/.config/gzdoom/doom2.wad}"
if [ -f "$IWAD" ] && [ -f /opt/gzdoom/gzdoom.pk3 ]; then
  docker run --rm -u "$(id -u):$(id -g)" $(env | grep -o '^AJAR_[A-Z_]*' | sed 's/^/-e /') -v "$PWD":/work \
    -v "$IWAD":/iwad/doom2.wad:ro -v /opt/gzdoom:/opt/gzdoom:ro ajar-tools python3 tools/classic.py
else
  echo "no doom2.wad at $IWAD (or no /opt/gzdoom/gzdoom.pk3): build/ajar-classic.pk3, Doom II's maps joined (MAP=CLASSIC), not built"
fi
