# Build + headless test image for Ajar. Nothing is installed on the host.
#  - python3: generates textures and the UDMF map, zips the pk3
#  - xvfb + mesa (llvmpipe) + SDL2 runtime: runs the host's GZDoom binary
#    (bind-mounted read-only from /opt/gzdoom) for automated smoke tests
FROM ubuntu:24.04
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      python3 xvfb xauth libsdl2-2.0-0 libopenal1 libgl1 libgl1-mesa-dri libglx-mesa0 libegl1 \
      libgomp1 libsndfile1 libmpg123-0 libpulse0 libasound2t64 libdecor-0-0 libxss1 \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends libglib2.0-0t64 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /work
