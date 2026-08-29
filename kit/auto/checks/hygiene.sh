#!/usr/bin/env bash
# Scope and execution hygiene on the working diff.
#
#   hygiene.sh kit/auto/queue/SLUG.md
#
# Fails when the diff strays outside the paths the task declared, when a
# changed .py does not compile, or when the diff carries whitespace damage
# or debug leftovers.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/env.sh"

TASK="${1:-}"
[ -f "$TASK" ] || die "usage: hygiene.sh <task-file>"
TASK="$(cd "$(dirname "$TASK")" && pwd)/$(basename "$TASK")"

BASE="${PM_BASE:-origin/main}"
rc=0
fail() { echo "FAIL  [$1] $2"; rc=1; }
ok()   { echo "ok    [$1] $2"; }

cd "$REPO" || die "no repo at \$REPO"

CHANGED="$(git diff --name-only "$BASE"...HEAD; git diff --name-only; git diff --cached --name-only)"
CHANGED="$(echo "$CHANGED" | sort -u | sed '/^$/d')"
[ -n "$CHANGED" ] || { echo "FAIL  [scope] no changes against $BASE"; exit 1; }

# --- scope: every changed path must be declared on the task ------------------
ALLOW="$(task_list "$TASK" files)"
[ -n "$ALLOW" ] || die "task file declares no 'files:' list"
stray=""
while IFS= read -r f; do
    if ! grep -Fxq "$f" <<<"$ALLOW"; then stray="$stray$f"$'\n'; fi
done <<<"$CHANGED"
if [ -n "$stray" ]; then
    fail scope "changed paths not declared on the task:"
    echo "$stray" | sed '/^$/d' | sed 's/^/          /'
    echo "          declare them or split them out; a second problem gets its own commit"
else
    ok scope "$(wc -l <<<"$CHANGED" | tr -d ' ') changed path(s), all declared"
fi

# --- whitespace --------------------------------------------------------------
if git diff --check "$BASE"...HEAD >/dev/null 2>&1 && git diff --check >/dev/null 2>&1; then
    ok whitespace "no whitespace errors"
else
    fail whitespace "git diff --check reports errors:"
    git diff --check "$BASE"...HEAD 2>/dev/null | sed 's/^/          /'
    git diff --check 2>/dev/null | sed 's/^/          /'
fi

# --- compile -----------------------------------------------------------------
pyfiles="$(grep '\.py$' <<<"$CHANGED" || true)"
if [ -n "$pyfiles" ]; then
    if "$VENV/bin/python" -m py_compile $pyfiles 2>/tmp/pmc.$$; then
        ok compile "$(wc -l <<<"$pyfiles" | tr -d ' ') .py file(s) compile"
    else
        fail compile "py_compile failed:"; sed 's/^/          /' /tmp/pmc.$$
    fi
    rm -f /tmp/pmc.$$
fi

# --- lazy_import shape -------------------------------------------------------
# feedback_gemini_verification.md: lazy_import('', name) is always wrong.
if git diff "$BASE"...HEAD -U0 -- $CHANGED 2>/dev/null | grep -n "^+" | grep -q "lazy_import(\s*['\"]\s*['\"]"; then
    fail lazy-import "lazy_import with an empty module name"
else
    ok lazy-import "no empty-module lazy_import"
fi

# --- debug leftovers ---------------------------------------------------------
added="$(git diff "$BASE"...HEAD -- $CHANGED 2>/dev/null; git diff -- $CHANGED 2>/dev/null)"
if grep -q "^+.*\(breakpoint()\|pdb\.set_trace\|XXX\|FIXME\)" <<<"$added"; then
    fail leftovers "debug marker added in the diff"
else
    ok leftovers "no debug markers added"
fi

# --- commit shape ------------------------------------------------------------
n="$(git rev-list --count "$BASE"..HEAD 2>/dev/null || echo 0)"
if [ "$n" -gt 1 ]; then
    fail atomic "$n commits ahead of $BASE; one commit changes one thing"
elif [ "$n" -eq 1 ]; then
    git log -1 --format=%B > /tmp/pmm.$$
    ok atomic "one commit ahead of $BASE"
    python3 "$HERE/prose.py" --commit /tmp/pmm.$$ || rc=1
    rm -f /tmp/pmm.$$
else
    echo "note  [atomic] nothing committed yet"
fi

exit $rc
