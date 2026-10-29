#!/bin/sh
# Headless Chrome with locally extracted libnss3/libnspr4/libasound (no system install).
D=$(cd "$(dirname "$0")" && pwd)
export LD_LIBRARY_PATH="$D/libroot/usr/lib/x86_64-linux-gnu"
exec "$D/chrome-headless-shell-linux64/chrome-headless-shell" --use-gl=swiftshader --enable-unsafe-swiftshader --autoplay-policy=no-user-gesture-required "$@"
