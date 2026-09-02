# auto — the contribution pipeline

Four stages, one queue, one gate. The queue holds state, so any session can
pick up where the last one stopped. The gate is scripts rather than judgment,
because a model reviewing its own work is the weakest link in the loop.

```
scope ──> implement ──> redteam ──> ship ──> STOP
  │           │             │          │
  └───────────┴─────────────┴──────────┴──> kit/auto/queue/<slug>.md
                                            (state lives here)
```

## Run it

```
/pm-next                    # advance the queue one stage
/loop /pm-next              # self-paced, one stage per wake
```

Or a stage directly: `/pm-scope`, `/pm-implement <slug>`, `/pm-redteam <slug>`,
`/pm-ship <slug>`.

## Running a check by hand

Nothing to install or activate. They are plain scripts; run one and read the
exit code, 0 for pass and 1 for fail.

```
kit/auto/checks/prose.py --kind commit  <file>   # commit | pr | issue | comment
kit/auto/checks/source-style.sh <task>           # added source prose and config
kit/auto/checks/claims.py --list        <file>   # what needs evidence
kit/auto/checks/claims.py --task <task> <file>   # check against the ledger
kit/auto/checks/drift.py --save <dir>   <file>   # snapshot before editing
kit/auto/checks/drift.py <old> <new>             # did shortening broaden a claim
kit/auto/checks/gate.sh  <task>                  # everything, one verdict
```

`--kind` sets the structural budget and switches rules that differ by
document. Hard wrapping is an error in a `pr` or `issue`, where GitHub renders
a newline as `<br>`, and allowed in a `commit`, where git wraps at 72 and
renders in a `<pre>`. A `Co-Authored-By` trailer is an error in a `pr` or
`issue` and a warning in a `commit`, where it is a case-by-case call.

## The stop

`state: ready` is terminal for the autonomous loop. Nothing in this pipeline
pushes a branch, files an issue, opens a PR, or posts a comment. The last
step prints the commands:

```
kit/auto/checks/ship-commands.sh kit/auto/queue/<slug>.md
```

Everything before that line is reversible in a local git repo. Everything
after it is public and permanent on a repo whose maintainer reads
everything.

## The gate

`checks/gate.sh` is the only thing that moves a task to `ready`. Seven checks:

| check | script | fails on |
|---|---|---|
| scope, whitespace, compile, atomicity | `hygiene.sh` | a changed path the task did not declare; `py_compile` failure; `lazy_import('', x)`; more than one commit; a commit message without `Fixes #N` |
| source editorial conventions | `source-style.sh` | deterministic terminology errors in added lines; contextual markup and alignment findings are warnings that must be resolved in the `source-style` axis |
| negative control | `negative_control.sh` | the new doctest passing against unpatched code |
| public-prose style and wording | `prose.py` | pronouns, em dashes, AI speak, hard-wrapped paragraphs, `Matthias` instead of `mkoeppe`, generated-by footers, escaped backticks |
| accuracy | `claims.py` | a categorical or numeric claim with no matching entry in the task's `## Evidence` section |
| shortening drift | `drift.py` | a surviving sentence that got broader than the revision before it |
| red team | `redteam_record.py` | fewer than eight recorded axes, including a separate source-style pass; or an axis line that reports a pass without saying what it found |

`prose.py --kind {commit,pr,issue,comment}` also enforces the structural
budget: paragraph counts, no headings, one code block.

The negative control is the one worth understanding. `sage -t` reads
docstrings from the repo file but imports code from site-packages, so running
a new doctest before copying the fix in gives a free unpatched control. It
must fail there. A test that passes without the fix is decoration, and that
mistake has been made here before.

## The failure modes this is built around

All three come from reading past sessions in this repo, not from theory.

**Shortening breaks claims.** About a fifth of all instructions in those
sessions were some form of "make it shorter". The draft came out long, got
cut, and the cut turned scoped claims into broad ones: "In the minimal
`passagemath-plot[tachyon]` installation this PR targets, `sage.repl` is
absent" became "`sage.repl` will not be installed", and an outside review
sent it back. Two fixes. Write to the budget the first time, so there is no
cutting pass. When cutting anyway, delete a claim whole rather than
compressing it, and run `drift.py` across the revision.

**Outside review needs triage, not adoption.** Codex reviews were pasted in
six times, every time with some version of "use your best judgement on what
is relevant". `redteam-prompt.sh` asks the reviewer to split findings into
BLOCKER, NIT, and PREFERENCE so there is something to sort on, and
`playbooks/redteam.md` says what to do with each bucket. Verify BLOCKERs
against the code before acting: outside reviewers have been confidently wrong
here in both directions.

**A trailing checklist eats the prompt above it.** A detailed output spec at
the end of a prompt is the most concrete and most recent thing in it, and a
model will optimize for it in preference to requirements spread through the
body. `scope-prompt.sh` used to end by asking for a task file "at state
scoped" with "a repro you actually ran", contradicting the read-only,
`state: proposed` rule it had stated forty lines earlier; the tail is the
half that gets followed. Three rules follow from that.

Put the operative constraint last, not the output format. Keep the format
spec short, and say plainly that it is not the job. And where a check reads
the output, make it read for substance: `gate.sh` used to grep for eight
`- [x] <axis>:` lines, which meant eight lines reading "checked" scored the
same as a real red team. `redteam_record.py` rejects those now.

It does not fix the underlying problem, and should not be read as fixing it.
A model that wants to pass can still write eight padded sentences; the check
raises the price of faking from nothing to a little, and that is all. Every
mechanical check on a reporting field has this ceiling, which is why the
playbooks say in words what the checks cannot enforce.

## The eight red-team axes

`playbooks/redteam.md`. relevance, scope, accuracy, approach, execution,
source-style, style, wording. Each needs a `- [x] <axis>: ...` line on the
task file saying what was attacked and what survived. `source-style` reads
changed source documentation and configuration; `style` reads the public
drafts. The line is the receipt for the pass, not the pass; `checks/redteam_record.py`
rejects a line that only reports a verdict.

## Layout

```
queue/_TEMPLATE.md      task file schema; state lives in the frontmatter
queue/<slug>.md         one task
artifacts/<slug>/       repro.py, commit.txt, issue.md, pr-body.md
artifacts/<slug>/revisions/   snapshots, for the drift check
playbooks/*.md          what each stage does; the skills defer to these
checks/*.sh, *.py       the gate
checks/test_*.py        run with python3 -m unittest discover kit/auto/checks
review-conventions.md   maintainer conventions learned from reviews
```

Paths resolve through `checks/env.sh`. The workspace is derived from that
file's own location, so a fresh clone runs the gate with no configuration;
the monorepo checkout is looked for beside it and next to `PM_SANDBOX`, and
the first candidate holding `src/sage` wins. Override any of it with
`PM_WORKSPACE`, `PM_SANDBOX`, `PM_REPO`, `PM_VENV`, `PM_BASE`.

No absolute paths are committed; this repo is public (`kit/PRIVACY.md`).
`scope-prompt.sh` collapses `$HOME` to `~` for that reason, since its output
is saved under `artifacts/_prompts/`.
