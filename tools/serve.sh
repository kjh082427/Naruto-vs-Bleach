#!/bin/sh
# Serve the game at http://127.0.0.1:8765/ — dist/ (Korean edition build) if present, else game/ (original).
# usage: tools/serve.sh [dist|game]
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="${1:-$( [ -f "$ROOT/dist/game.swf" ] && echo dist || echo game )}"
cd "$ROOT/$DIR" && exec python3 -I -m http.server 8765 --bind 127.0.0.1
