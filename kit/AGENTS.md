# passagemath — Agent Context

This file is the authoritative context document for AI agents working in this
directory. Claude Code also reads `CLAUDE.md` (which points here).

---

## Writing style: commits, PR bodies, issue comments

All public prose must read as neutral engineering writing. Not like an AI
wrote it; not like the user personally performed and vouched for every step.

**Voice**

* Impersonal and evidence-based. State what the change does and what the
  evidence shows, never who did it: "Verified in a native xpython kernel:
  display_data emitted" — not "I tested this and it works."
* Never claim first-person verification ("I verified", "I confirmed"). The
  user cannot independently verify most changes and the prose must not imply
  they did.
* No AI tells: no emoji, no filler adjectives ("comprehensive", "robust",
  "seamless"), no bullet-point padding, no restating the diff in prose.
* Concise. Say what changed, why, and how it was verified. Stop.

**Attribution**

* No `Co-Authored-By: Claude` trailers. No "Generated with Claude Code"
  footers. No claude.ai session URLs. Commit messages stand alone.

**Structure — the Perfect Commit** (Simon Willison)

* One commit changes one thing; bundles implementation + tests + docs.
* Subject line: `area: what changed`, imperative mood.
* Body: the problem, the fix, the verification evidence, a link to the issue.
* In docstrings, link issues with the `:passagemathissue:` role — plain
  `:issue:` points at sagemath/sage, the wrong repo.

**Mechanics**

* Refer to Matthias Köppe as `mkoeppe` in all public content.
* PR/issue bodies: write to a file and pass `gh ... --body-file` — backticks
  in `--body` strings are eaten by shell command substitution.
* Each paragraph is one unbroken line: GitHub renders single newlines as
  line breaks, so 80-column wrapping produces mid-sentence breaks.
* When reporting a CI failure without a confident diagnosis, post the raw
  facts (failing test, assertion, file/line) with no interpretation.
* No categorical claims ("none of the packages implement X") unless the
  search that produced them is confirmed exhaustive.

---

## Project directives

### Search tooling

* Use the `Grep` tool (not `Bash` + `rg`) for content search.
* Use the `Glob` tool (not `Bash` + `fd`/`find`) for file discovery.
* When `rg` or `fd` must be used in `Bash` (piped processing or features the
  dedicated tools don't expose), pass `--no-heading` for machine-readable
  output.

### Environment

* Prefer `uv` for all Python environment management. Never suggest `pip` as a
  primary tool.

### Publishing

* Never `git push` or open a PR without explicit per-action permission.
  Plan approval covers local edits and commits only.

---

## User goals

Quality over quantity. One correct, architecturally-aware PR is worth more
than five superficial ones. Current mode: small, verifiable, arc-completing
changes. Do not pitch large design-heavy directions unprompted.

## Work classification (S.N.T.)

Use this lens when evaluating candidates for contribution:

* **Scale** — touches infrastructure shared across many packages (e.g. `.m4`
  templates, `sage-conf`, CI workflows). High impact per fix.
* **Neglected** — modularization blind spots: `except ImportError: pass`
  blocks that leave names unbound, causing `NameError` at runtime in partial
  installs. High value because they require architectural awareness to find.
* **Tractable** — surgical fixes in `src/sage/` with clear scope, testable
  in the local venv, low risk of reviewer pushback.

### Interpreting CI noise (the "triage tax")

When reviewing failed CI runs (especially `test-mod` jobs), distinguish three
types of noise:

1. **Modularity gaps (high value):** a partial install lacks an optional
   dependency (e.g. `linbox`) but a test hits a code path requiring it,
   raising `ModuleNotFoundError`. Fix: add a surgical `# needs sage.libs.X`
   guard to the `sage:` line initiating the test.
2. **Baseline drift (do not touch):** output mismatches flagged as "New
   failures" because `known-test-failures.json` is out of sync. Do NOT edit
   the baseline JSON. If it appears in your PR's CI, note it as pre-existing
   in the PR description; open a separate issue only if mkoeppe confirms.
3. **Log clutter (ignore):** `Warning: The tag '# needs X' may no longer be
   needed` floods logs and is a false positive.

Also: CI red on main is common. Before investigating a PR's red CI, check
whether main's same workflow fails identically. Windows mingw wheel/tox lanes
are known-broken.

---

## Working principles

* **Prove it works**: manual test first, then automated test. Do not ship
  unverified diffs.
* **No unsolicited cleanup**: PEP8 sweeps, typo PRs, docstring reformatting
  are explicitly rejected.
* **Understand before touching**: read the code, trace the execution path,
  understand the architecture before proposing any change.

### Display / notebook fixes

* For rich-output or notebook-display changes, verify both the intended
  frontend context and a nearby non-target context (for example the doctest
  runner or `BackendSimple`).
* Do not use backend capability alone as a proxy for frontend behavior. A
  backend that lacks a rich output type may appear in non-notebook contexts
  too.
* When environment detection is needed, prefer existing Sage helpers over
  introducing a new heuristic.

---

## GitHub identity

* Account: `sacchen`
* Org member: `passagemath`
* Fork of monorepo: `sacchen/passagemath`
* Fork of mip package: `sacchen/passagemath-pkg-numerical-interactive-mip`

---

## Repo architecture (verified)

* `passagemath/passagemath` — monorepo. Source of truth for core library
  (`src/`) and modular packages (`pkgs/`). Uses `.m4` template files for
  `pyproject.toml` generation. All packages use `setuptools.build_meta`.
* `passagemath/passagemath-pkg-numerical-interactive-mip` — independent
  external package, NOT a generated mirror. Predates the fork (2016). Version
  0.3.0. Files there do NOT exist in the monorepo.
* Monorepo's generated/mirrored packages (e.g. `sagemath-polyhedra`) ARE
  separate repos but ARE read-only mirrors. The distinction matters.

---

## Local environment

* Clone `passagemath/passagemath` — shallow blobless clone is sufficient for most contribution work.

* uv venvs (create as needed, all live in the monorepo root):
  * `.venv-plot` — **plot testing venv**: passagemath-plot + passagemath-repl.
    Create fresh: `uv venv .venv-plot --python 3.12 && uv pip install passagemath-plot passagemath-repl --python .venv-plot/bin/python`
  * `.venv-contrib` (Python 3.12) — passagemath-repl, passagemath-combinat,
    passagemath-plot, passagemath-polyhedra, passagemath-glpk. General doctests.
  * `.venv` (Python 3.12) — passagemath-polyhedra + glpk
  * `.venv311` (Python 3.11) — passagemath-polyhedra + glpk

  All `.venv*` directories are gitignored at the root level.

* Cannot run `sage -t` (no full sage CLI in modular installs)

### Running doctests

No full build required. Install `passagemath-repl` (pure Python) into the
working venv, then use `--environment sage.all__sagemath_<package>` matching
the file's package:

```bash
uv pip install passagemath-repl --python .venv/bin/python
python -m sage.doctest --environment sage.all__sagemath_combinat src/sage/combinat/partition.py
```

The `all__sagemath_<package>` modules live in the venv's `sage/` root and
populate the doctest global namespace with that package's symbols. Use the
one matching the package of the file under test:

| File in...           | Environment                       | Venv packages needed          |
| -------------------- | --------------------------------- | ----------------------------- |
| `sage/plot/`         | `sage.all__sagemath_plot`         | passagemath-plot + repl       |
| `sage/combinat/`     | `sage.all__sagemath_combinat`     | passagemath-combinat + repl   |
| `sage/categories/`   | `sage.all__sagemath_categories`   | passagemath-categories + repl |
| `sage/numerical/`    | install `passagemath-polyhedra`   | passagemath-polyhedra + repl  |
| `sage/schemes/`      | `sage.all__sagemath_schemes`      | passagemath-schemes + repl    |

**Do not use:**
- `sage.repl.ipython_kernel.all_jupyter` — still requires `sage.all_cmdline`
- `sage.doctest.all` — too minimal, math symbols not in scope
- `sage.all__sagemath_repl` — repl-only, same problem

`sage.all_cmdline` does NOT exist in a modular passagemath install. It is
only present in the full monolithic SageMath build.

### Testing local source changes

The modular venv runs doctests against the **installed** package in
`site-packages`, not the local `src/` tree. Using `PYTHONPATH=src` fails
because unbuilt compiled modules (`sage.cpython.atexit`,
`sage.structure.element`, etc.) are missing.

To test a patch against local changes without a full build:
1. Copy the modified file(s) into the installed site-packages location
2. Run doctests against `src/` (the runner reads test text from `src/`, executes against the installed copy)
3. Restore the originals when done

```bash
# Example: testing a plot patch
SITE=.venv-plot/lib/python3.12/site-packages
cp src/sage/plot/graphics.py $SITE/sage/plot/graphics.py
.venv-plot/bin/python -m sage.doctest --environment sage.all__sagemath_plot src/sage/plot/graphics.py
```

For most pure-Python PRs, CI is the authoritative test of the actual patch.
Local doctests can verify the installed baseline and catch obvious breakage,
but they do not run against your working tree.

**Circular import gotcha (plot package):** `sage.plot` modules cannot be
imported with a bare `python -c "from sage.plot.line import line"` — a Cython
circular import fires on first import. Always test plot code via
`python -m sage.doctest`, never via a standalone script.

**`multigraphics.py` local limitation:** the file has a module-level
`# sage.doctest: needs sage.symbolic` directive, so all its tests are skipped
unless `passagemath-symbolics` is installed. Rely on CI for that file.

**`# needs sage.libs.singular` tests:** skipped unless `passagemath-singular`
is installed (no working local install path found; source build needs
`mesonpy`). Rely on CI (`test-mod sagemath_schemes-check`).

---

## The FeatureNotPresentError fix pattern

Endorsed by mkoeppe in #2243. Apply to all unbound-import bugs:

```python
# module level
except ImportError:
    x_func = None          # bind to None, NOT pass

# usage site
if x_func is None:
    from sage.features.sagemath import sage__libs__X
    sage__libs__X().require()
```

For cardinality-style methods with a small-n enumerable fallback:
```python
if x_func is None:
    if self.n <= 10:
        return self._cardinality_from_iterator()
    sage__libs__X().require()
```

---

## Reasoning about dependency availability

To determine whether package X is safe to assume present in a source file:
find which `pkgs/sagemath-*` package contains the file, then check that
package's `pyproject.toml.m4` — X in `[project] dependencies` means required;
only in `[project.optional-dependencies]` or absent means optional.

`build/pkgs/<dep>/type` (e.g. `type=standard`) is monolithic-SageMath
metadata and says nothing about what a pip install of a modular package
provides. Do not cite it as evidence.

Known facts:

* **sympy**: required dependency of `passagemath-symbolics`
  (`pkgs/sagemath-symbolics/pyproject.toml.m4`). Safe to assume present in
  that package's files.
* **pari / cypari2**: optional, gated by `passagemath-pari`. Unguarded uses
  are real bugs (class fixed in PR #2282).

---

## Dead ends — do not revisit

* **uv CI migration / workspace restructuring**: tracked in issue #2094;
  mkoeppe's territory. Targeted `# needs` guard fixes are welcome;
  architectural CI rewrites are not.
* **Contributing to upstream SageMath**: CONTRIBUTING.md says "not a safe
  environment as of 2026." Do not cross-post.
* **Windows doctest quirks (#2222, #2223, #2225, #2227)**: need a Windows
  environment. Unresolvable locally.
* **Docstring typo / PEP8 sweeps**: explicitly rejected strategy.
* **HiGHS sensitivity/ranging**: the HiGHS C API does not expose ranging
  functions. Blocked at the API level.
