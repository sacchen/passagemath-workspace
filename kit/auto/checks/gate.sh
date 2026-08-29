#!/usr/bin/env bash
# The ship gate. Nothing goes outward until this exits 0.
#
#   gate.sh kit/auto/queue/SLUG.md
#
# Runs every mechanical check and prints one verdict. Judgment checks live in
# playbooks/redteam.md and are recorded on the task file, not here.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/env.sh"

TASK="${1:-}"
[ -f "$TASK" ] || die "usage: gate.sh <task-file>"
TASK="$(cd "$(dirname "$TASK")" && pwd)/$(basename "$TASK")"
SLUG="$(task_key "$TASK" slug)"
ART="$AUTO/artifacts/$SLUG"

rc=0
section() { echo; echo "=== $1"; }

section "1. scope + execution hygiene"
bash "$HERE/hygiene.sh" "$TASK" || rc=1

section "2. source editorial review"
bash "$HERE/source-style.sh" "$TASK" || rc=1

section "3. negative control"
nc="$(task_key "$TASK" negative_control)"
case "$nc" in
    fail-on-unpatched) echo "ok    recorded: fails unpatched, passes patched";;
    *) echo "FAIL  negative_control is '$nc'; run checks/negative_control.sh and record the result"; rc=1;;
esac

section "4. public prose style and wording"
drafts=()
for d in "$ART/commit.txt" "$ART/pr-body.md" "$ART/issue.md"; do
    [ -f "$d" ] && drafts+=("$d")
done
if [ "${#drafts[@]}" -eq 0 ]; then
    echo "FAIL  no drafts in $ART (expected commit.txt, and pr-body.md or issue.md)"
    rc=1
else
    [ -f "$ART/commit.txt" ] && { python3 "$HERE/prose.py" --commit "$ART/commit.txt" || rc=1; }
    for d in "$ART/pr-body.md" "$ART/issue.md"; do
        [ -f "$d" ] && { python3 "$HERE/prose.py" "$d" || rc=1; }
    done
fi

section "5. accuracy: claims against evidence"
if [ "${#drafts[@]}" -gt 0 ]; then
    python3 "$HERE/claims.py" --task "$TASK" "${drafts[@]}" || rc=1
fi

section "6. shortening drift"
REV="$ART/revisions"
if [ -d "$REV" ]; then
    for d in commit.txt pr-body.md issue.md; do
        [ -f "$ART/$d" ] || continue
        prev="$(ls -1 "$REV/$d".* 2>/dev/null | tail -1)"
        [ -n "$prev" ] || continue
        echo "-- $d vs $(basename "$prev")"
        python3 "$HERE/drift.py" "$prev" "$ART/$d" || rc=1
    done
else
    echo "note  no revision snapshots; drift check skipped"
    echo "      snapshot before every shortening pass:"
    echo "        checks/drift.py --save $ART/revisions $ART/pr-body.md"
fi

section "7. red-team record"
missing=""
for axis in relevance scope accuracy approach execution source-style style wording; do
    grep -qiE "^-?\s*\[x\]\s*$axis\b" "$TASK" || missing="$missing $axis"
done
if [ -n "$missing" ]; then
    echo "FAIL  red team not recorded on the task for:$missing"
    echo "      see playbooks/redteam.md; each axis needs a '- [x] <axis>: <what was attacked, what survived>' line"
    rc=1
else
    echo "ok    all eight axes recorded"
fi

echo
if [ "$rc" -eq 0 ]; then
    echo "GATE PASS  $SLUG is ready. Nothing has been pushed."
    echo "  branch:  $(task_key "$TASK" branch)"
    echo "  ship it: kit/auto/checks/ship-commands.sh $TASK"
else
    echo "GATE FAIL  $SLUG stays in state '$(task_key "$TASK" state)'."
fi
exit $rc
