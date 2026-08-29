#!/usr/bin/env bash
# Diff-scoped source editorial review.
#
#   source-style.sh kit/auto/queue/SLUG.md
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/env.sh"

TASK="${1:-}"
[ -f "$TASK" ] || die "usage: source-style.sh <task-file>"
TASK="$(cd "$(dirname "$TASK")" && pwd)/$(basename "$TASK")"

python3 "$HERE/source_style.py" \
    --repo "$REPO" \
    --base "${PM_BASE:-origin/main}" \
    "$TASK"
