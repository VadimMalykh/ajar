#!/bin/bash
# Design trials: builds MAP01 once per value of a map switch and photographs
# each with the tour (tools/smoke.sh, mode 2).
#   tools/trial.sh AJAR_HALL 1 2 3 4 5
# Shots land in build/trial/<switch>_<value>/view_NN.png. The pk3 is rebuilt
# without the switch at the end.
set -e -o pipefail
cd "$(dirname "$0")/.."
VAR="$1"; shift
build() { docker run --rm -u "$(id -u):$(id -g)" -e "$VAR=$1" -v "$PWD":/work ajar-tools python3 tools/build.py | tail -1; }
for v in "$@"; do
  out="$PWD/build/trial/${VAR}_$v"
  rm -rf "$out"
  build "$v"
  MAP=MAP01 MODE=2 ./tools/smoke.sh "$out" | grep -i -E "rror|arning|Unknown|nvalid" || true
  i=0
  for f in $(ls "$out"/Screenshot_*.png | sort); do mv "$f" "$out/$(printf 'view_%02d.png' $i)"; i=$((i+1)); done
  echo "$VAR=$v: $i shots"
done
build ""
