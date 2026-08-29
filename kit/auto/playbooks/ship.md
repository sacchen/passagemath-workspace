# Stage 4 — Ship

Input: `state: redteamed`. Output: `state: ready`, and a stop.

## Write to the budget, do not write long and cut

Across past sessions roughly a fifth of all instructions were some form of
"make it shorter". The draft came out long, got cut twice, and the second cut
broke claims that the first one had left intact. Writing to the budget the
first time removes both passes.

| document | budget |
|---|---|
| `commit.txt` | subject at most 72 chars, imperative, then at most 3 short paragraphs: the bug, the change, the test. Ends `Fixes #NNNN`. |
| `pr-body.md` | `Closes #NNNN.` then at most 3 short paragraphs: what the change does, the judgment call a reviewer would question, testing evidence with numbers. |
| `issue.md` | at most 5 short paragraphs and one code block. |
| a comment reply | at most 2 short paragraphs. Usually two sentences. |

No headings. No bullet lists standing in for paragraphs. One code block at
most. `prose.py --kind {commit,pr,issue,comment}` enforces all of it.

Then read once for the things a checker cannot see: background mkoeppe
already has, a sentence that restates the diff, a paragraph that exists to
introduce the next one.

## Shortening without breaking the claims

Cutting words is safe. Cutting qualifiers is not. The failure mode has a
signature: a surviving sentence loses the clause that scoped it and becomes
broader than the evidence. "In the minimal `passagemath-plot[tachyon]`
installation this PR targets, `sage.repl` is absent" became "`sage.repl` will
not be installed", and an outside reviewer sent it back.

So the rule is: **delete a claim whole, or leave it exactly as scoped.**
Never compress a claim into a shorter, bigger one.

Snapshot before each pass and check after:

```
kit/auto/checks/drift.py --save kit/auto/artifacts/<slug>/revisions kit/auto/artifacts/<slug>/pr-body.md
# edit
kit/auto/checks/drift.py kit/auto/artifacts/<slug>/revisions/pr-body.md.<stamp> kit/auto/artifacts/<slug>/pr-body.md
```

Anything it reports as BROADENED goes back to the task's `## Evidence`
section: either restore the qualifier or drop the sentence.

## Issues

The embedded script is law. Extract it from the draft and run it verbatim
against a broken build, and against the fixed build if one exists, before
filing. Record the exit codes.

## Gate

```
kit/auto/checks/gate.sh kit/auto/queue/<slug>.md
```

Seven checks: hygiene and scope, source editorial review, negative control
recorded, public-prose style and wording, claims covered by evidence,
shortening drift, eight red-team axes recorded.
On failure the task keeps its state. Fix and rerun. Do not rationalize past a
gate; if a check is wrong, fix the check and say so.

## The stop

On pass, set `state: ready` and run:

```
kit/auto/checks/ship-commands.sh kit/auto/queue/<slug>.md
```

That prints the push, issue, and PR commands. It does not run them. The
autonomous run ends here. Everything above this line is reversible in a local
git repo; everything below it is public and permanent on a repo whose
maintainer reads everything.

Hand back: the slug, the branch, the one-line summary, and the commands.
