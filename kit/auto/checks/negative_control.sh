#!/usr/bin/env bash
# Prove the new doctest discriminates: it must FAIL without the fix.
#
#   negative_control.sh kit/auto/queue/SLUG.md
#
# A test that passes against unpatched code is decoration. Two memories say
# so from experience: passagemath-modular-boundary-testing ("verify the guard
# by running it against the unpatched file; if it passes there, it is
# decoration") and parametric-surface-triangulate-crash.
#
# The mechanic is passagemath's own split, recorded in
# passagemath-single-pyx-rebuild: `sage -t` reads DOCSTRINGS from the repo
# file but imports CODE from site-packages. So:
#
#   run 1  repo docstrings + installed (pristine) code  -> must FAIL
#   run 2  repo docstrings + repo code copied in        -> must PASS
#
# .pyx modules need a rebuild between the runs; this script stops and points
# at kit/plot3d-repr/rebuild.sh rather than guessing.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/env.sh"

TASK="${1:-}"
[ -f "$TASK" ] || die "usage: negative_control.sh <task-file>"
TASK="$(cd "$(dirname "$TASK")" && pwd)/$(basename "$TASK")"

vname="$(task_key "$TASK" venv)"; [ -n "$vname" ] && VENV="$SANDBOX/$vname"
[ -x "$VENV/bin/python" ] || die "no venv at $VENV"
CMD="$(task_key "$TASK" doctest_cmd)"
[ -n "$CMD" ] || die "task file declares no doctest_cmd"

# bash 3.2 (the macOS system bash) has no mapfile.
FILES=()
while IFS= read -r line; do FILES+=("$line"); done < <(task_list "$TASK" files)
[ "${#FILES[@]}" -gt 0 ] || die "task file declares no files"

PYX=""
for f in "${FILES[@]}"; do
    case "$f" in *.pyx|*.pxd) PYX="$f";; esac
done

SP="$(site_packages "$VENV")" || die "cannot resolve site-packages"
cd "$REPO" || die "no repo at $REPO"
BASE="${PM_BASE:-origin/main}"

run_doctest() {
    ( cd "$REPO" && PATH="$VENV/bin:$PATH" eval "$CMD" ) >"$1" 2>&1
}

# ---- Cython path -----------------------------------------------------------
# Same idea as the pure-Python path, but the "installed code" is a .so, so the
# pristine control has to be built. rebuild.sh compiles whatever is on disk at
# the moment it runs, so: check out the base revision, build, restore the
# edited file, and the docstrings are new while the compiled code is old.
if [ -n "$PYX" ]; then
    REBUILD="$WORKSPACE/kit/plot3d-repr/rebuild.sh"
    [ -x "$REBUILD" ] || die "no rebuild.sh at $REBUILD; needed for $PYX"
    DOTTED="$(echo "${PYX#src/}" | sed 's/\.pyx$//; s#/#.#g')"
    STASH="$(mktemp -d)"
    cp "$PYX" "$STASH/edited.pyx"
    restore_pyx() {
        cp "$STASH/edited.pyx" "$REPO/$PYX" 2>/dev/null
        rm -rf "$STASH"
    }
    trap restore_pyx EXIT

    echo "== building pristine control from $BASE"
    git show "$BASE:$PYX" > "$PYX" || die "cannot read $PYX at $BASE"
    "$REBUILD" "$VENV" "$DOTTED" "$REPO/src" >/dev/null || die "pristine build failed"
    cp "$STASH/edited.pyx" "$PYX"

    echo "== run 1: edited docstrings against the pristine build"
    set +e; run_doctest "$STASH/run1.log"; rc1=$?; set -e
    tail -5 "$STASH/run1.log" | sed 's/^/     /'; echo "     exit $rc1"
    if [ "$rc1" -eq 0 ]; then
        echo
        echo "FAIL  [negative-control] the doctest passes against unpatched code."
        echo "      The test does not discriminate. Set"
        echo "      negative_control: DOES-NOT-DISCRIMINATE and go back to implement.md."
        exit 1
    fi

    echo
    echo "== rebuilding from the edited source"
    "$REBUILD" "$VENV" "$DOTTED" "$REPO/src" >/dev/null || die "edited build failed"
    echo "== run 2: edited docstrings against the edited build"
    set +e; run_doctest "$STASH/run2.log"; rc2=$?; set -e
    tail -5 "$STASH/run2.log" | sed 's/^/     /'; echo "     exit $rc2"
    if [ "$rc2" -ne 0 ]; then
        echo; echo "FAIL  [negative-control] still failing with the fix applied."
        echo "      Log kept: $STASH/run2.log"
        trap - EXIT; exit 1
    fi
    echo
    echo "PASS  [negative-control] fails unpatched (exit $rc1), passes patched (exit $rc2)."
    echo "      Record it, then set negative_control: fail-on-unpatched"
    exit 0
fi

# ---- pure-Python path ------------------------------------------------------
BACKUP="$(mktemp -d)"
restore() {
    for f in "${FILES[@]}"; do
        rel="${f#src/}"
        [ -f "$BACKUP/$(basename "$f")" ] && cp "$BACKUP/$(basename "$f")" "$SP/$rel"
    done
    rm -rf "$BACKUP"
}
trap restore EXIT

for f in "${FILES[@]}"; do
    rel="${f#src/}"
    [ -f "$SP/$rel" ] || die "$rel is not installed in $SP; install the package that ships it"
    cp "$SP/$rel" "$BACKUP/$(basename "$f")"
done

echo "== run 1: repo docstrings against installed (pristine) code"
set +e
( cd "$REPO" && PATH="$VENV/bin:$PATH" eval "$CMD" ) >"$BACKUP/run1.log" 2>&1
rc1=$?
set -e
tail -5 "$BACKUP/run1.log" | sed 's/^/     /'
echo "     exit $rc1"

if [ "$rc1" -eq 0 ]; then
    echo
    echo "FAIL  [negative-control] the doctest passes against unpatched code."
    echo "      The test does not discriminate. Either it exercises a path the"
    echo "      fix does not change, or the installed code already has the fix"
    echo "      (a previous run copied it in: reinstall the package and retry)."
    echo "      Set negative_control: DOES-NOT-DISCRIMINATE and go back to"
    echo "      playbooks/implement.md."
    exit 1
fi

echo
echo "== run 2: repo docstrings against repo code"
for f in "${FILES[@]}"; do cp "$f" "$SP/${f#src/}"; done
set +e
( cd "$REPO" && PATH="$VENV/bin:$PATH" eval "$CMD" ) >"$BACKUP/run2.log" 2>&1
rc2=$?
set -e
tail -5 "$BACKUP/run2.log" | sed 's/^/     /'
echo "     exit $rc2"

if [ "$rc2" -ne 0 ]; then
    echo
    echo "FAIL  [negative-control] the doctest still fails with the fix applied."
    echo "      Full log: $BACKUP/run2.log (kept)"
    trap - EXIT
    exit 1
fi

echo
echo "PASS  [negative-control] fails unpatched (exit $rc1), passes patched (exit $rc2)."
echo "      Record in the task's ## Evidence section:"
echo "        - claim: the doctest fails on unpatched code"
echo "          check: \`kit/auto/checks/negative_control.sh $TASK\` -> exit $rc1 unpatched, exit $rc2 patched"
echo "      Then set negative_control: fail-on-unpatched"
