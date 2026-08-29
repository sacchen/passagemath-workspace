# Red-team prompt: ParametricSurface triangulate fix

You are red-teaming a bug fix and its issue report for passagemath before
they are filed upstream. Your job is to break the work: find factual errors,
unsound reasoning, untested paths, and writing problems. Assume the author is
wrong until the evidence in front of you says otherwise. Reproduce claims
yourself; do not trust the author's transcripts. Report findings only: do not
fix, amend, commit, push, or file anything.

## The claims under attack

1. Root cause: in `src/sage/plot/plot3d/parametric_surface.pyx`,
   `triangulate()`'s try/except covers only `realloc()`/`eval_grid()`. An
   exception in the face-construction loop after it (from `sig_check()` or a
   user color function) leaves `fcount = m*n` with `face.vertices` unassigned
   past the failure point, because `realloc()` sets `fcount` up front.
2. Crash mechanism: the retry short-circuits on
   `if self.render_grid == (urange, vrange) and self.fcount: return` and the
   renderer dies (SIGSEGV/SIGBUS) in `IndexFaceSet._separate_creases`.
   `face_list()` raising `IndexError` is a softer symptom of the same state.
3. The fix (commit `953874bc5a`, branch
   `fix/parametric-surface-triangulate-guard`): extend the guard over the
   whole triangulation, resetting only `fcount`/`vcount` on failure. The
   commit deliberately does NOT reset `render_grid`, claiming `get_grid()`
   returns it for function-based surfaces and clearing it would leave the
   object permanently unrenderable (claimed to be a second, pre-existing bug
   in the old guard, reachable by interrupting `eval_grid()`).
4. The re-indentation in the diff is content-identical to the original loop
   code; only the guard, hoisted cdefs, and one comment changed.
5. The new regression doctest in `triangulate()` is deterministic, passes,
   and exercises the same except-path a real Ctrl-C takes. It uses
   `ValueError` because a doctest raising `KeyboardInterrupt` would abort
   Sage's doctest runner.
6. The issue draft is accurate, and appropriate for its audience.
7. The bug is independent of PR #2698 (which touches `base.pyx`, not this
   file).

## Artifacts

- Repo: `~/foundry/sandbox/passagemath/passagemath`, branch
  `fix/parametric-surface-triangulate-guard`, one commit ahead of `main`.
- `kit/plot3d-repr/` (in `~/foundry/sandbox/passagemath-workspace/`):
  - `issue-draft.md`: the report to be filed. Audience is mkoeppe, who
    knows this codebase well. Style constraints it must meet: at most 5
    short paragraphs plus the code block, no personal pronouns, no em
    dashes, plain language, only relevant content.
  - `triangulate-guard.patch`: format-patch of the commit.
  - `repro_triangulate_corruption.py`: 4 modes, see its docstring.
  - `rebuild.sh <venv> <dotted.module>`: rebuilds one .pyx into a venv.

## Environment facts (verify, then rely on)

- Venv: `~/foundry/sandbox/passagemath/.venv-plot3d`
  (Python 3.12). Its `parametric_surface` extension currently holds the
  FIXED build. For a pristine control:
  `git checkout main -- src/sage/plot/plot3d/parametric_surface.pyx`,
  rebuild, test, then `git checkout <branch> -- <file>` and rebuild again.
- Crash repros MUST run in a subprocess; they kill the interpreter
  (exit 138/139).
- Doctests: `sage -t --environment=sage_plot3d_env
  --optional=sage,sage.symbolic <file>` from the repo root. Without the
  `--optional` tag the file is feature-gated and reports 0 tests, which
  looks like success.
- `stash@{0}` in the repo belongs to unrelated docs work. Do not pop it.
- Leave the repo on the fix branch with a clean tree and the venv holding
  the fixed build when done.

## Minimum attack surface

- Strip-whitespace-compare the old and new `triangulate()` bodies; hunt for
  any dropped, duplicated, or reordered statement the author's own check
  might have normalized away.
- Attack the render_grid reasoning: find a caller or subclass
  (`MoebiusStrip`, `Sphere`, `Torus`, revolution surfaces, transformed
  render params) where NOT resetting `render_grid` gives a stale or wrong
  result. Check `enclosed`, `_clean_point_list()` side effects, and repeated
  failure/retry cycles, including a failure at a different grid than a
  previous success.
- Attack the doctest: feature availability under the file's gates
  (`colormaps`, `srange`), the hardcoded face count 81, the call counter
  crossing attempts, behavior under `sage -t --random-seed` reordering
  assumptions, and whether it would pass on UNPATCHED code (it must fail
  there to be a regression test; verify, do not assume).
- Attack the issue draft line by line: every factual claim (version, commit
  hash, signal names, "every subclass is affected", "unchanged on current
  main") and every style constraint listed above. Run its embedded script
  verbatim against both builds.
- Attack the commit: does the message overclaim anywhere, and does the diff
  contain anything the message does not admit to?

## Report format

Rank findings by severity (crash/correctness > test validity > factual error
in draft > wording). For each: the claim attacked, the evidence (commands run
and their actual output), and whether the finding is CONFIRMED or SUSPECTED.
Close with the list of claims that survived attack and any claims that could
not be tested in this environment, stated as such. An empty findings list is
an acceptable outcome; an unverified "looks good" is not.
