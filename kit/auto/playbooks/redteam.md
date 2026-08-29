# Stage 3 — Red team

Input: `state: implemented`. Output: `state: redteamed`, with all seven axes
recorded on the task file.

Attack the work as an adversary who wants it rejected. Self-review finds
nothing; adversarial review finds wording bugs and overstatements that
survive every other pass.

Record each axis on the task file as a line the gate can read:

```
- [x] relevance: <what was attacked, what survived, what changed>
```

An axis with nothing to say still gets a line saying that. Seven `[x]` lines
are required before the gate will pass.

## relevance

Does anyone hit this? Name the install configuration and the user action.
If the only evidence is a scanner hit, this is a false positive until a
configuration is named. Check the issue is not already filed, in this repo
and upstream.

## scope

Is this one thing? Every changed path must be on the task's `files:` list,
and every path on that list must be needed. A second problem found along the
way gets its own issue and its own commit, never a ride-along. No PEP8
drift, no reformatting, no renames that were not the point.

## accuracy

Attack every factual claim in the drafts. For each one, name the command
that checks it and run it. Specific failure modes with history here:

- Categorical claims. "none", "all", "every", "no remaining". A public
  correction already happened from a paginated org listing that missed
  `passagemath-pkg-slabbe`. Use `gh search code "pattern" --owner passagemath --limit 100` and confirm the result set is complete before writing "none".
- Dependency availability. Trace which `pkgs/sagemath-*` package ships the
  file, then read that package's `pyproject.toml.m4` `[project] dependencies`.
  Not `build/pkgs/<dep>/type`.
- Anything an agent produced. Re-read the lines yourself. `lazy_import('', x)`
  compiles and is always wrong; the first argument is the module to import
  from.
- Counts. Recount them.

Every surviving claim goes in the task's `## Evidence` section with its
check. `claims.py` fails the gate on any flagged sentence not covered there.

## approach

Is the fix the right shape? State the alternative that was rejected and why.
Ask what the fix breaks: the `render_grid` trap was found this way, and the
existing `eval_grid` guard still has a softer version of it. Ask whether the
guard is reachable, and whether a narrower fix would do.

## execution

Does the code do what the prose says? The one check that matters:
`checks/negative_control.sh` must show the doctest failing on unpatched code.
A test that passes without the fix is decoration. If the negative control
cannot run (Cython), build the control by hand and record both exit codes.

Then read the diff line by line as a reviewer would, and check the things a
diff hides: moved or re-indented blocks, an early return that changes a path
you did not consider, a `finally` that was needed and is not there.

## style

`prose.py` covers the mechanical half: pronouns, em dashes, AI speak, hard
wraps, first names, footers. Run it and fix the errors. Then read for what it
cannot see: paragraphs longer than they need to be, background the maintainer
already has, a sentence that restates the diff.

## wording

Hunt overstatement of timing and scope. "always", "immediately", "no
regressions" are claims, not adjectives. Name code exactly: the function, the
field, the file, never "the counter" or "the evaluation step". Past tense for
what the bug did, present tense for what the change does. Read the title
alone and ask whether it is honest about the conditions.

## Reviewer pass

Last, read the whole thing as mkoeppe: fast, one issue per comment, pointing
at an exact line. Write down the comments it would draw. Fix them now instead
of after posting.

## Outside review

Self-review finds little. A second model finds more, and a different family
finds different things. Generate the prompt:

```
kit/auto/checks/redteam-prompt.sh kit/auto/queue/<slug>.md
```

Paste it into Codex or another agent with the branch available. The prompt
asks for findings split into BLOCKER, NIT, and PREFERENCE, because outside
reviews over-report: past ones mixed real defects with taste and speculation,
and every one of them needed sorting by hand before anything could be acted
on.

### Triage the response

Work the findings in this order and write the verdict next to each one.

- **BLOCKER** — verify it against the code yourself before acting. Outside
  reviewers have been wrong here in both directions: an agent called two real
  bugs false positives after reading the wrong version of a file, and wrote
  `lazy_import('', 'sympy')`, which compiles and is meaningless. A finding
  that survives verification gets fixed now.
- **NIT** — take it if the fix is smaller than the finding. Otherwise drop it
  and say why.
- **PREFERENCE** — drop it unless it agrees with `~/.claude/commit-pr-style.md`.
- **Anything asking for more words** — drop it. A claim that is too broad
  gets narrower wording, never an added caveat.
- **Anything out of scope** — file it as a new task at `state: parked`. It
  does not ride along on this commit.

Record the triage on the task file under the axis it belongs to. A rejected
finding needs a reason; "not relevant" is not one.

### After a fix round

Rerun `checks/drift.py` against the pre-review snapshot. Fixes that respond
to accuracy findings tend to lengthen the draft, and the next shortening pass
is exactly where the claims break again.
