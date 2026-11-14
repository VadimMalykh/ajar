#!/bin/bash
# Builds build/ajar.pk3 inside docker (no host tools needed).
set -e
cd "$(dirname "$0")"
docker image inspect ajar-tools >/dev/null 2>&1 || docker build -t ajar-tools tools
docker run --rm -u "$(id -u):$(id -g)" -v "$PWD":/work ajar-tools python3 tools/build.py
