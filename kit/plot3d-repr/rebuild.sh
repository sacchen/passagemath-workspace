#!/bin/bash
# Rebuild one sage .pyx extension into a venv.
# Usage: rebuild.sh <venv-dir> [module-path] [src-dir]
#   module-path: dotted or slashed path under src/, no extension.
#                Default: sage.plot.plot3d.base
set -e
VENV="$1"
MOD="${2:-sage.plot.plot3d.base}"
SRC="${3:-$HOME/foundry/sandbox/passagemath/passagemath/src}"
MOD="${MOD%.pyx}"
DOTTED="${MOD//\//.}"
SLASHED=$(echo "$DOTTED" | tr . /)
SP="$VENV/lib/python3.12/site-packages"
PYINC=$("$VENV/bin/python" -c 'import sysconfig; print(sysconfig.get_paths()["include"])')
WORK=$(mktemp -d)
cd "$SRC"
# Flags mirror src/meson.build (~line 280) — they drift; re-check when it breaks.
"$VENV/bin/cython" --cplus -3 -I . --module-name "$DOTTED" \
  -X auto_pickle=False -X autotestdict=False -X binding=True \
  -X c_api_binop_methods=True -X cdivision=True -X cpow=True \
  -X embedsignature=True --embed-positions -X fast_getattr=True \
  -X legacy_implicit_noexcept=True -X preliminary_late_includes_cy28=True \
  -o "$WORK/mod.cpp" "$SLASHED.pyx"
clang++ -std=c++11 -O1 -shared -undefined dynamic_lookup -fPIC \
  -I"$PYINC" -I"$SP" -I"$SP/cysignals" -I"$SP/gmpy2" -I"$SP/numpy/_core/include" \
  "$WORK/mod.cpp" -o "$SP/$SLASHED.cpython-312-darwin.so"
rm -rf "$WORK"
echo "built -> $SP/$SLASHED.cpython-312-darwin.so"
