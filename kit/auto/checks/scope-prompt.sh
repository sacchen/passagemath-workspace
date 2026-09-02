#!/usr/bin/env bash
# Generate the scope-stage prompt for an outside agent, Gemini by default.
# Scope is repo-wide search and CI log forensics, which is what Gemini is for.
#
#   scope-prompt.sh > prompt.txt      # then paste, or: gemini -p "$(scope-prompt.sh)"
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/env.sh"

echo "Work the scope stage of the passagemath contribution pipeline."
echo "Read $(tilde "$WORKSPACE")/AGENTS.md and $(tilde "$AUTO")/playbooks/scope.md first, then follow them."
echo "The monorepo clone is at $(tilde "$REPO"). Read it; do not modify it."
echo
echo "The queue already holds these, so do not re-scope them:"
for f in "$QUEUE"/*.md; do
    [ "$(basename "$f")" = "_TEMPLATE.md" ] && continue
    echo "  - $(task_key "$f" slug) ($(task_key "$f" state)): $(task_key "$f" branch)"
done
cat <<'BODY'

## Read only. Execute nothing.

You do not need uv, a virtualenv, a build, or a Python run, and you should
not ask for permission to use them. Scoping is reading: source files, git
history, GitHub issues and PRs, and CI logs. The commands you need are git,
gh, grep, and a file reader.

Write the repro, do not run it. Fill in expected_failure: with what it should
print or raise, and name the venv it needs. Leave repro_status: unrun and
stop at state: proposed. Whoever holds the environment runs it and promotes
the task. A proposed task is a claim, not a finding.

## Work the sources in order, and report coverage

Your job is to find work worth doing, in this order:

1. Review comments on open PRs by sacchen, and CI on those PRs. Pull job logs
   with the gh api call in the playbook, grep "New failures, not in baseline",
   read the next 30 lines. ntests in known-test-failures.json is the total
   tests run, not a failure count.
2. Follow-ups already recorded in the queue at state parked.
3. kit/nerdsnipe/ deep dives that end in a fix.
4. Open issues mentioning sacchen.

A candidate becomes a task only when all four of these hold. Missing any one
means it stays a note:

  a. a user-visible symptom, with the install configuration that produces it
  b. a root cause named at the level of functions and fields
  c. the exact file list the diff would touch
  d. a repro written to kit/auto/artifacts/<slug>/repro.py, with
     expected_failure: filled in. You write it; you do not run it.

Rank by impact, not by size. Record a tier (beginner, intermediate,
advanced) as an effort estimate only; it is not a filter. A one-line fix that
unblocks CI for every contributor outranks a large change that helps one
person.

Hard exclusions. PEP8, typo, and docstring sweeps are rejected on sight. Do
not propose unsolicited CI rewrites, upstream SageMath work, or anything
needing Windows.

Do not skip ahead. Finish source 1 before starting source 2, and report what
you found and what you rejected at each one, including the sources that came
back empty. A source reported without evidence of having been searched counts
as not searched.

Then rank what survives. For each candidate say who is affected and how
often, and say which candidate you would do first and why. If the queue
already holds something more important than anything you found, say that
instead of padding the list.

Producing no task is a correct outcome. Do not manufacture work to fill the
queue, and do not lower the bar.

Do not write to GitHub: no comments, no issues, no PRs. Read only.

Hand back one task file per candidate, in the format of
kit/auto/queue/_TEMPLATE.md, at state proposed. Say which of the four bars
each candidate cleared and how you checked. Where you are not certain, say so
rather than asserting. Never write "none", "all", or "every" about a search
result unless you confirmed the result set was complete.

## The format is the smallest part of this

Everything above is the job. A correctly formatted task file for a candidate
you did not actually search out is worse than returning nothing: it reads as
a finding, and the next stage spends a pass discovering it is empty. If you
have to choose, spend the effort on working the four sources in order and
reporting honestly what each one returned, not on the shape of the output.
BODY
