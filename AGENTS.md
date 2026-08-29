# Agent entrypoint

Any agent working in this repo: read `kit/auto/README.md`, then the playbook
for the stage you are on in `kit/auto/playbooks/`.

## The pipeline

Four stages over a queue of task files, with a mechanical gate between the
last stage and anything public.

```
scope -> implement -> redteam -> ship -> STOP
```

State lives in `kit/auto/queue/<slug>.md` frontmatter. Any agent can read it,
advance one stage, and write it back. Nothing about the pipeline is specific
to one model: the checks are bash and Python, the playbooks are Markdown.

## The one hard rule

**Nothing in this pipeline pushes, files an issue, opens a PR, or posts a
comment.** `state: ready` is terminal. `kit/auto/checks/ship-commands.sh`
prints the outward commands for a human to run. Reading GitHub is fine;
writing to it is not.

## The gate

```
kit/auto/checks/gate.sh kit/auto/queue/<slug>.md
```

It is the contract between agents. A task is ready when the gate says so, so
no agent has to trust another agent's report. Run it before claiming a stage
is done.

## Roles

The split matches what each tool is good at, and what the transcripts show
already happening by hand.

| Agent | Stage | Why |
|---|---|---|
| Gemini | scope | repo-wide search, CI log forensics, locating neglected patterns |
| Claude | implement | refactors, Cython, `sage.categories`, the doctest |
| Codex | redteam | outside review; `checks/redteam-prompt.sh` writes the prompt |

Verify any agent's findings against the code before acting. Gemini has
produced `lazy_import('', 'sympy')`, which compiles and is meaningless, and
has called real bugs false positives after reading the wrong file version.
Outside reviews over-report by design; triage them by the rules in
`playbooks/redteam.md`.

## Deciding without asking

`kit/auto/playbooks/judgment.md` says what to decide alone and what to stop
for. Read it before asking a question.

## Project context

`kit/AGENTS.md` has the architecture, the environment, the completed
contributions, and the dead ends. `kit/PRIVACY.md` applies to everything
committed here: this repo is public and the maintainer reads it. No absolute
paths, no local usernames.
