#!/usr/bin/env bash
# Print the outward commands for a task that has passed the gate. Prints
# only. The autonomous run stops here by design: everything above this line
# is reversible, everything below it is not.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/env.sh"

TASK="${1:-}"
[ -f "$TASK" ] || die "usage: ship-commands.sh <task-file>"
TASK="$(cd "$(dirname "$TASK")" && pwd)/$(basename "$TASK")"
SLUG="$(task_key "$TASK" slug)"
BRANCH="$(task_key "$TASK" branch)"
ISSUE="$(task_key "$TASK" issue)"
ART="$AUTO/artifacts/$SLUG"

bash "$HERE/gate.sh" "$TASK" >/dev/null 2>&1 || {
    echo "gate has not passed; run: kit/auto/checks/gate.sh $TASK"
    exit 1
}

echo "# Review the drafts first:"
echo "#   \$EDITOR $ART/commit.txt $ART/pr-body.md"
echo
echo "cd \"$REPO\""
if [ -z "$ISSUE" ] && [ -f "$ART/issue.md" ]; then
cat <<CMD
# 1. file the issue (the commit needs its number)
gh issue create --repo passagemath/passagemath \\
  --title "$(head -1 "$ART/issue.md" | sed 's/^#\s*//')" \\
  --body-file "$ART/issue.md"
# then: put the number in $TASK, rerun the gate, and amend the commit message

CMD
fi
cat <<CMD
# 2. push the branch to the fork
git push -u fork "$BRANCH"

# 3. open the PR (--body-file, never --body: backticks die in --body)
gh pr create --repo passagemath/passagemath \\
  --base main --head sacchen:$BRANCH \\
  --title "$(head -1 "$ART/commit.txt")" \\
  --body-file "$ART/pr-body.md"

# 4. record the PR number in $TASK and set state: shipped
CMD
