---
slug: graphics3d-repr-html
state: shipped
issue: 2236
pr: 2708
branch: feat/graphics3d-repr-html
venv: .venv-plot3d
tier: advanced
snt: neglected
files:
  - src/sage/plot/plot3d/base.pyx
  - src/sage/features/threejs.py
  - src/sage/repl/rich_output/display_manager.py
  - pkgs/sagemath-plot/tox.ini
doctest_cmd: >-
  sage -t --environment=sage_plot3d_env --optional=sage,sage.symbolic
  src/sage/plot/plot3d/base.pyx
repro:
negative_control: fail-on-unpatched
---

# Graphics3d._repr_html_() for interactive 3D in plain notebooks

## Symptom

Plain Python notebooks (Colab, marimo) get a static Tachyon PNG from #2698
but cannot reach the Three.js viewer. `_rich_repr_threejs()` builds the scene
and returns an `OutputSceneThreejs`, a container that ships in
`passagemath-repl`.

## Root cause

The page build is entangled with the rich-output container, so a kernel
without `passagemath-repl` cannot get the HTML.

## Approach

Move the page out of `_rich_repr_threejs()` into `_render_html_(**kwds)`.
`_repr_html_()` escapes it into an `<iframe srcdoc>`; `_rich_repr_threejs()`
stays as the container wrapper. The `online=True` branch of
`threejs_scripts()` moves to `Threejs.cdn_scripts()`.

## Evidence

Verified 2026-08-29 against `origin/main`. Freeze this set before drafting.
A claim may be deleted whole; a surviving claim keeps its qualifier.

- claim: OutputSceneThreejs is absent from a plain passagemath-plot install
  check: `grep -n "class OutputSceneThreejs" src/sage/repl/rich_output/output_graphics3d.py` -> line 154; `sed -n '/^dependencies/,/^]/p' pkgs/sagemath-plot/pyproject.toml.m4` -> no sagemath_repl entry
- claim: threejs_scripts() serves the online=True case without dispatching to a backend
  check: `src/sage/repl/rich_output/display_manager.py:717` docstring -- "This base method handles online=True case only, serving CDN script tag. Location of script for offline usage is backend-specific."
- claim: a plain Python kernel has no display backend
  check: pkgs/sagemath-plot/pyproject.toml.m4 dependencies list omits sagemath_repl, which ships the backends

### Corrected, do not reuse the old wording

The current commit says OutputSceneThreejs is "a container that ships **only**
in passagemath-repl". That is not established.

- `pkgs/sagemath-repl/MANIFEST.in:6` -- `graft sage/repl`, the explicit one.
- `pkgs/sagemath-standard-no-symbolics/MANIFEST.in:7` -- `graft sage`, which
  takes all of it, and line 86 is `## prune sage/repl`, commented out. No
  uncommented `prune sage/repl` exists in any manifest.

So by MANIFEST.in logic a second distribution carries `sage/repl`. That
contradicts [[passagemath-modular-boundary-testing]], which records "sage/repl
ships only in passagemath-repl", and MANIFEST.in governs the sdist while the
wheel is built from the package list, so the two are not the same question.

Do not spend a round trip settling it. The claim the change actually depends
on is narrower and independently verified: OutputSceneThreejs is absent from a
plain passagemath-plot install, because pkgs/sagemath-plot/pyproject.toml.m4
does not list sagemath_repl. Use that and the ambiguity never arises.

### Verified 2026-08-29 in .venv-plot3d

The doctest counts in the drafted commit and PR body were wrong. 406 and 416
are not reproducible under any command recorded on this task. The measured
figures, both runs `sage -t --environment=sage_plot3d_env
--optional=sage,sage.symbolic src/sage/plot/plot3d/base.pyx`:

- claim: base.pyx goes from 430 to 440 doctests, all passing
  check: origin/main docstrings -> `[430 tests, 5.70s wall] All tests passed!`;
    branch docstrings -> `[440 tests, 6.16s wall] All tests passed!`
- claim: the new doctests fail on unpatched code
  check: `kit/auto/checks/negative_control.sh kit/auto/queue/graphics3d-repr-html.md`
    -> `PASS ... fails unpatched (exit 1), passes patched (exit 0)`
- claim: the tox check needs no !notest gate
  check: `pkgs/sagemath-plot/tox.ini:46` -- `extras = !notest: test`, and the
    three lines above the _repr_png_ check are ungated, so an ungated line is
    the file's own convention for a check that does not need the test extra.
    `pkgs/sagemath-plot/MANIFEST.in:17` -- `graft sage/ext_data/threejs`, so
    the template and version file the online path reads ship with the wheel.
- claim: save('foo.html') keeps needing passagemath-repl unless online=True
  check: `src/sage/plot/plot3d/base.pyx:2154` -- the save doctest is
    `G.save(f, frame=False, online=True)`
- claim: the commandline backend answers with a local path
  check: `src/sage/repl/rich_output/backend_ipython.py:407` --
    `script = Threejs().absolute_filename()`
- claim: the iframe matches the ones already in the backends
  check: `backend_ipython.py:412` IFRAME_TEMPLATE and `backend_marimo.py:166`,
    neither carrying a sandbox attribute
- claim: sandboxing would block the viewer's save items
  check: `src/sage/ext_data/threejs/threejs_template.html:588-589` --
    `onclick="saveAsPNG()"` and `onclick="saveAsHTML()"`
- claim: show() is untouched and has no fallback
  check: `src/sage/plot/plot3d/base.pyx:1989-1991` -- get_display_manager()
    then dm.display_immediately(self, **kwds)
- claim: nothing on the origin/main class chain defines _repr_html_
  check: `git grep -n _repr_html_ origin/main -- src/sage/plot/ src/sage/structure/`
    -> no hits

### Draft claims

Each line below is a verbatim substring of the drafted commit or PR body, which
is how `checks/claims.py` matches a claim to its evidence.

- claim: a plain kernel has none
  check: `pkgs/sagemath-plot/pyproject.toml.m4` dependencies omit sagemath_repl,
    which ships the display backends; `src/sage/repl/rich_output/display_manager.py:717`
    docstring -- offline script location "is backend-specific"
- claim: renders a sphere with sage.repl blocked
  check: `python -c '...sys.modules["sage.repl"] = None; Sphere(1)._repr_html_()...'`
    in .venv-plot3d -> exit 0 patched; exit 1 unpatched with
    `AttributeError: 'sage.plot.plot3d.shapes.Sphere' object has no attribute '_repr_html_'`
- claim: on the unpatched build it fails with
  check: same run as above, pristine base.pyx rebuilt from origin/main -> exit 1
- claim: 430 to 440 under
  check: `sage -t --environment=sage_plot3d_env --optional=sage,sage.symbolic
    src/sage/plot/plot3d/base.pyx` -> origin/main docstrings `[430 tests]`,
    branch docstrings `[440 tests]`, both "All tests passed!"
- claim: all three copies should change together
  check: `grep -n sandbox src/sage/plot/plot3d/base.pyx
    src/sage/repl/rich_output/backend_ipython.py
    src/sage/repl/rich_output/backend_marimo.py` -> no hits, and the three
    iframes are base.pyx THREEJS_IFRAME_TEMPLATE, backend_ipython.py:412
    IFRAME_TEMPLATE, backend_marimo.py:166
- claim: a sandboxed copy renders the same scene
  check: kit/plot3d-repr-html/plain-kernel-evidence.txt, 2026-08-28 --
    the sphere page in an iframe with `sandbox="allow-scripts"` and one without
    screenshot byte-identical (sha256 60d1645e2463b616...), and nothing under
    src/sage/ext_data/threejs touches localStorage, sessionStorage, cookie,
    parent, top or postMessage
- claim: blocks the viewer's Save as PNG and Save as HTML
  check: `src/sage/ext_data/threejs/threejs_template.html:506-525` --
    `saveAsPNG()` and `saveAsHTML()` are both `a.download` plus `a.click()`,
    which a sandbox blocks without `allow-downloads`
- claim: only the TESTS block carried over
  check: `git diff origin/main...HEAD -- src/sage/plot/plot3d/base.pyx` -- the
    surviving `sage:` lines in the moved docstring are the TESTS block with
    `._rich_repr_threejs(online=True).html.get_str()` rewritten to
    `._render_html_(online=True)`; header, INPUT, OUTPUT and EXAMPLES are new
- claim: the runtime body is 143 lines
  check: `_render_html_` docstring ends at base.pyx:560, `return html` at
    base.pyx:703 -> 143 lines

### Pipeline bugs found and fixed while verifying

Both were silent, and both made a green result meaningless.

- `checks/env.sh` `task_key` returned the literal `>-` for any YAML block
  scalar, so `doctest_cmd` never reached `negative_control.sh`. `eval ">-"`
  creates a file named `-` and exits 0, which the script read as a passing
  control that had run no doctest. Fixed to fold block scalars.
- `checks/negative_control.sh` used `mapfile`, which bash 3.2 (the only bash
  on this machine) does not have, so the script died before run 1. Replaced
  with a read loop.
- the task's `doctest_cmd` omitted `--environment=sage_plot3d_env`, without
  which `sage -t` dies on `ModuleNotFoundError: No module named
  'sage.all_cmdline'`. Recorded in [[passagemath-single-pyx-rebuild]].

## Red team

- [x] relevance: named the configuration and the action rather than trusting the
  issue. `pip install passagemath-plot passagemath-symbolics` with no
  passagemath-repl, Colab or marimo on the stock python3 kernel, evaluating
  `sphere()` in a cell: after #2698 that is a static Tachyon PNG and never the
  viewer. Duplicate hunt: `gh search issues --repo passagemath/passagemath
  "_repr_html_"` returns only #2236 and the unrelated #2269, and no open PR
  touches plot3d rich output (#2701 is Kitty protocol, #2693 NetworkX layouts).
  Survives unchanged.
- [x] scope: `git diff --name-only origin/main...HEAD` returns exactly the four
  paths on `files:`, none extra and none unused. `git diff --stat -w` differs
  from the plain stat by two lines, so no reformatting is riding along. The
  display_manager.py hunk is five lines and is the extraction the change needs.
  Survives unchanged.
- [x] accuracy: recounted, and the drafts were wrong. 406 and 416 are not
  reproducible under any command recorded on this task; measured 430 to 440.
  Corrected in commit.txt and pr-body.md, and the drift report on that sentence
  is a correction, not a broadening, reconciled against the count evidence
  above. `claims.py --task` now reports 0 unevidenced across both drafts. The
  disproved "ships only in passagemath-repl" wording stays out.
- [x] approach: the alternative is keeping the page inside
  `_rich_repr_threejs()` and unwrapping `.html.get_str()` at the call site,
  rejected because the unwrap still constructs an OutputSceneThreejs and a
  plain passagemath-plot install has none. Asked what it breaks:
  `save('foo.html')` moves off `OutputBuffer.save_as`, and the replacement is
  byte-identical, since `buffer.py:53` encodes str as utf-8 and `save_as` at
  `buffer.py:310` writes it with `open(filename, 'wb')`. The iframe is filled
  `width='100%', height=400`, the same values `backend_ipython.py:557` passes,
  so the plain-kernel frame matches the Sage-kernel one rather than inventing a
  size.
- [x] execution: `checks/negative_control.sh` -> `PASS ... fails unpatched
  (exit 1), passes patched (exit 0)`. Getting there took fixing two harness
  bugs that both reported green without running anything; see the section
  above. Attacked the Sage kernel for double rendering, which adding a second
  mime representation invites: `SageDisplayFormatter.format`
  (`src/sage/repl/display/formatter.py:193-201`) returns `sage_format` as soon
  as the display manager offers more than plain text, so `super().format()`
  never runs and `_repr_html_` is never consulted there. The bare `except
  Exception: return None` swallows real errors, kept because `_repr_png_` from
  #2698 does the same and the tox check reruns `_render_html_()` to surface the
  traceback.
- [x] source-style: ran after mkoeppe's review, which is the wrong order and is
  why he found these first. `checks/source-style.sh` on the branch against
  `upstream/main` reported 3 errors and 4 warnings; his five comments cover
  five of the seven. product-case (ERROR) on `features/threejs.py:77`,
  `base.pyx:476` and `base.pyx:715`: `three.js` -> `Three.js`, and 77 and 715
  are the two he did not comment on. package-markup (WARN) on
  `features/threejs.py:82` and `base.pyx:480`: both name the distribution in
  prose, not a requirement specifier, so both take `**passagemath-plot**`.
  class-role (WARN) on `base.pyx:709`: `Graphics3d` is documented in this same
  module, so `:class:` resolves; the line goes to 82 characters, under the
  160 `max-line-length` in `src/tox.ini:186`, and no lint select carries E501.
  config-alignment (WARN) on `tox.ini:85`: indented to the column the `!notest:`
  command above it uses, 20 spaces, so the block reads as one group.
  Sibling scan of the touched documentation: `three.js` survives at
  `base.pyx:33`, `:2672` and `:2953`, none adjacent to a changed line, left
  alone per the no-repository-wide-cleanup rule; `` `passagemath-plot[tachyon]` ``
  at `base.pyx:203` and `:266` is extra syntax and correctly stays literal.
  Re-run reports 0 errors, 0 warnings. `relint -c src/.relint.yml` and
  `flake8 --select=RST` both exit 0 on the changed files.
- [x] style: rewrote pr-body.md shorter after the first pass read as a pile of
  identifiers. Four short paragraphs, one point each, instead of three dense
  ones. `drift.py` caught six specifics dropped in that pass, and all six went
  back: the `<iframe srcdoc>` in the opening sentence, "returns the HTML
  document", `DisplayManager` as the caller of `cdn_scripts()`, the literal
  `sys.modules["sage.repl"] = None`, `IPython.core.formatters.DisplayFormatter`
  in the screenshot sentence, and "unchanged except for" on the moved body. The
  remaining drift entries are one deliberate drop (#2351 and #2366, background
  mkoeppe has) and sentence-splitting artifacts where a long sentence became
  two and the tool pairs the old one against a single half. `prose.py` reports
  0 errors on both drafts. The two warnings are
  deliberate. Co-Authored-By matches the merged precedent in #2698 and #2700.
  `Refs:` rather than `Fixes` is correct because #2236 is an open umbrella
  issue covering latex and 2D as well, which this does not close.
- [x] wording: hunted overstatement. The title says "for interactive 3D in
  notebooks", not "in Colab", which is honest about a path neither the tox
  check nor the screenshot pins to one host. The last sentence of the testing
  paragraph is the one that could overstate, so it names the limit outright:
  `sphere()` displays and `sphere().show()` does not. Every categorical left
  standing ("all three", "only the TESTS markers", "all passing") has a check
  recorded above.


## Log

- 2026-08-29 imported at state implemented; commit a600d6387d exists on the branch
- 2026-08-29 evidence ledger filled; "ships only in passagemath-repl" disproved (two manifests graft sage/repl)
- 2026-08-29 draft PR #2708 opened; commit 19e5f63d26 force-pushed to fork (message-only amend)
- 2026-08-29 relevance pass on pr-body.md: cut the #2698 recap, the save() round-trip
  clause, and the sandbox paragraph from three sentences to two; 356 words
- 2026-08-29 red teamed on all seven axes; state -> redteamed
- 2026-08-29 negative control run and passed; doctest counts corrected 406/416 -> 430/440; two pipeline bugs fixed (task_key block scalars, mapfile on bash 3.2)
- 2026-08-30 source-style axis run for the first time, post-review: 7 findings,
  5 of them mkoeppe's comments and 2 he missed (three.js at features/threejs.py:77
  and base.pyx:715); all 7 fixed, checker back to 0/0, commit amended
