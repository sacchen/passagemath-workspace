#!/usr/bin/env bash
# Generate the prompt to hand an outside reviewer (Codex, Gemini, a second
# Claude). Prints to stdout; paste it into the other agent.
#
#   redteam-prompt.sh kit/auto/queue/SLUG.md > prompt.txt
#
# An outside reviewer beats self-review, but it over-reports: past reviews
# mixed real defects with style preferences and speculation. The prompt asks
# for a severity split so the triage in playbooks/redteam.md has something to
# sort on, instead of "use your best judgement on what is relevant".
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/env.sh"

TASK="${1:-}"
[ -f "$TASK" ] || die "usage: redteam-prompt.sh <task-file>"
TASK="$(cd "$(dirname "$TASK")" && pwd)/$(basename "$TASK")"
SLUG="$(task_key "$TASK" slug)"
BRANCH="$(task_key "$TASK" branch)"
ART="$AUTO/artifacts/$SLUG"

cat <<PROMPT
You are the red team on an unmerged passagemath change. Find what is wrong.
The branch is \`$BRANCH\` in a clone of passagemath/passagemath. Read the
diff against origin/main, then the drafts below.

Review these eight axes, in this order, and skip an axis only after trying:

1. relevance   Does a user hit this? Name the install configuration and the
               action. A scanner hit with no configuration is a false positive.
2. scope       Is this one change? Flag any hunk that is not required by the
               stated fix.
3. accuracy    Attack every factual claim in the drafts. Categorical claims
               ("none", "all", "every", "will not") and counts get the most
               attention. For dependency claims, the evidence is the
               containing package's pkgs/sagemath-*/pyproject.toml.m4
               [project] dependencies list, not build/pkgs/<dep>/type.
4. approach    Is the fix the right shape? Name the alternative that should
               have been chosen instead, if there is one. What does the fix
               break?
5. execution   Does the code do what the prose says? Does the new doctest
               fail on unpatched code, or is it decoration? Read for what a
               diff hides: re-indented blocks, an early return, a missing
               finally.
6. source-style Read only added source documentation and configuration lines.
               Check semantic Sphinx roles, distribution-name markup, product
               capitalization, and alignment with the whole local config
               block. Read kit/auto/review-conventions.md. Nearby merged code
               is evidence, not authority. Do not request unrelated cleanup.
7. style       Public drafts only: short paragraphs, plain language, no
               personal pronouns, no em dashes, no AI speak, no headings, no
               signposting.
8. wording     Overstatement of timing or scope. Ambiguous antecedents. Code
               named exactly, never "the counter" or "that part".

Split every finding into exactly one bucket:

  BLOCKER   wrong, or would draw a maintainer comment. Say what to change.
  NIT       a real improvement, not worth a round trip on its own.
  PREFERENCE  your taste. Say so and expect it to be dropped.

For each finding cite the file and line. Do not propose PEP8 changes, typo
sweeps, or docstring reformatting; they are rejected on sight in this repo.
Do not suggest making the prose longer to be safer. If a claim is too broad,
give the narrower wording, not a caveat.

If you find no BLOCKER, say so in one line.

---- task file ----
$(cat "$TASK")
PROMPT

for d in commit.txt issue.md pr-body.md; do
    [ -f "$ART/$d" ] && { echo; echo "---- $d ----"; cat "$ART/$d"; }
done
