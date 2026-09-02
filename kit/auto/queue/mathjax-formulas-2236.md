---
slug: mathjax-formulas-2236
state: shipped
issue: 2236
pr: 2767
branch: fix/mathjax-formulas-2236
venv: .venv
tier: advanced
snt: scale
files:
  - src/sage/structure/sage_object.pyx
  - src/sage/repl/display/formatter.py
  - pkgs/sagemath-objects/tox.ini
  - pkgs/sagemath-categories/tox.ini
doctest_cmd: >-
  ../.venv/bin/python
  ../passagemath-workspace/kit/auto/artifacts/mathjax-formulas-2236/repro.py
repro: kit/auto/artifacts/mathjax-formulas-2236/repro.py
repro_status: reproduced
expected_failure: >-
  AssertionError: rational, polynomial, and parent objects publish no
  MathJax-ready text/latex representation in plain IPython.
negative_control: fail-on-unpatched
deliverable: pr
---

# Render Sage formulas in plain Python notebooks

## Symptom

With **passagemath-categories** and IPython installed in a stock Python
kernel, evaluating a rational, polynomial, or parent publishes only
`text/plain`. The same objects have mathematical LaTeX representations, but
plain IPython cannot discover them, so Jupyter frontends show linear text
instead of a typeset formula. This is the formula work left on issue #2236
after the 2D and 3D plot representation hooks.

This task covers individual Sage objects with mathematical representations.
It does not cover issue #2384: that output is an `HtmlFragment` containing
mixed prose, HTML, inline math, and equation environments, and remains parked
until a real Colab representation matrix identifies a working payload.

## Root cause

`SageObject` in `src/sage/structure/sage_object.pyx` is the common base for
user-visible Sage objects, but it provides no standard IPython
`_repr_latex_()` hook. The monorepo has 478 files defining `_latex_()` and no
definition of `_repr_latex_()` on current upstream `main`.

The Sage kernel avoids this gap by installing `SageDisplayFormatter` from
`src/sage/repl/display/formatter.py`. Its `DisplayManager` routes a LaTeX text
preference through `BackendBase.latex_formatter()`, which calls
`MathJax().eval()`. A stock Python kernel uses IPython's `DisplayFormatter`
directly and therefore publishes only `repr(obj)` unless the object implements
a standard `_repr_*_()` method.

The common base and formatter belong to different modular layers:
`SageObject` ships in **passagemath-objects**, while `MathJax` and the macro
definitions needed for objects such as `QQ` ship in
**passagemath-categories**. The implementation must keep an objects-only
installation importable and fall back to text when the higher layer is
absent. It must also avoid invoking expensive or conflicting `_latex_()`
implementations on objects with their own `_rich_repr_()` path; in particular,
`Graphics` and `MultiGraphics` already have standard image hooks and their
`_latex_()` methods render PGF through Matplotlib.

The two tox files are in scope for boundary checks: the objects environment
must prove that the optional hook does not require categories, and the
categories environment must prove that plain IPython publishes
MathJax-ready `text/latex` while retaining `text/plain` and not using
`sage.repl`.

The formatter check proves MIME publication, not visible typesetting. Final
acceptance also requires a stock Google Colab Python kernel to render the
three repro objects, including the `\Bold` macro in `QQ`; save the executed
notebook output or a screenshot. A frontend failure blocks shipment rather
than changing the generic `HtmlFragment` experiment.

Implementation found one additional in-repository boundary. When Sage's own
formatter produces only text, `SageDisplayFormatter.format()` deliberately
falls through to IPython's standard hooks. The new `_repr_latex_()` therefore
adds `text/latex` even under explicit `plain`, `ascii_art`, and `unicode_art`
preferences. Preserving those modes requires the focused guard and regression
test in `src/sage/repl/display/formatter.py` now included in the declared
file list.

### The Sage kernel reads `_repr_latex_` too

Adding the hook to `SageObject` is not confined to plain kernels.
`SageDisplayFormatter.format()` returns Sage's own MIME dictionary early only
when it holds more than `text/plain`. For an ordinary rational or parent it
does not, so control reaches `super().format(obj, exclude=['text/plain'])`,
which is IPython's own formatter, which calls `_repr_latex_()`. A new hook on
`SageObject` therefore turns on typeset output in the Sage Jupyter notebook
under `%display default`, where the documented behaviour is plain text.

Measured against upstream `eb735110258` with `BackendIPythonNotebook`
installed and `preferences.text` unset, using a `SageObject` subclass to stand
in for the base class, which is an immutable extension type:

    plain SageObject             ({'text/plain': 'I am Plain'}, {})
    SageObject + _repr_latex_    ({'text/latex': '$\displaystyle \frac{1}{2}$',
                                   'text/plain': 'I am WithLatex'}, {})

That fallthrough is load-bearing and cannot simply be closed: it is how third
party objects such as sympy expressions, `IPython.display.Image`, and
ipywidgets render under a Sage kernel today, and `format()` carries doctests
for the latter two. Any suppression has to be narrowed to `SageObject`
instances rather than applied to the `text/latex` slot as a whole.

### The payload has to carry math delimiters

`MathJax().eval(obj, mode='plain')` returns a bare body,
`\newcommand{\Bold}[1]{\mathbf{#1}}\Bold{Q}`, with no `$` or `\(`. Jupyter and
Colab do not typeset an undelimited `text/latex` payload. The string to match
is the one the Sage kernel already publishes: `OutputHtml.__init__` runs
`latex_re` over the `<html>\(\displaystyle ...\)</html>` wrapper from
`sage.misc.html.html` and stores a `latex` twin, which
`BackendIPythonNotebook.displayhook` emits as `text/latex`. For `QQ` that twin
is `$\displaystyle \newcommand{\Bold}[1]{\mathbf{#1}}\Bold{Q}$`. Matching it
gives Sage-kernel parity and matches sympy's convention.

## Approach

Two edits, one per layer.

**passagemath-objects.** `SageObject._repr_latex_()` returns
`'$\displaystyle ' + MathJax().eval(self, mode='plain') + '$'`, the same
string `BackendIPythonNotebook` publishes as `text/latex` under
`%display latex`. It returns `None` when the object has its own
`_rich_repr_()`, when it has no `_latex_()`, when `sage.misc.html` is absent,
and when `_latex_()` raises. The `_rich_repr_()` test is what keeps `Graphics`
and `MultiGraphics` out: they already have image hooks and their `_latex_()`
renders PGF through Matplotlib.

**passagemath-repl.** `SageDisplayFormatter.format()` adds `TEXT_LATEX` to the
`exclude` list it passes to `super().format()` when the object is a
`SageObject` and `preferences.text != 'latex'`. Without this the hook leaks
into the Sage kernel, because the fallthrough to IPython's formatter runs
whenever Sage's own output is text-only, which is every non-LaTeX text mode:
`default`, `plain`, `ascii_art`, `unicode_art`. The `isinstance` narrowing is
required, not incidental: excluding the `text/latex` slot outright would also
suppress sympy expressions, which render under a Sage kernel today through
that same path.

Rejected, with reasons:

- **Gate inside `_repr_latex_()` on whether a Sage backend is installed.** One
  file instead of two, but it makes `sage.structure` in passagemath-objects
  import `sage.repl` from a higher distribution, inverting the layering this
  task is otherwise careful to respect.
- **Skip the base class; hook only `HtmlFragment`, `MathJaxExpr`, and
  `table`.** Zero regression risk and genuinely narrower, but it leaves
  `QQ(1)/2` as plain text, which is the symptom, so it does not close the
  task.
- **Publish `text/html` instead of `text/latex`.** `OutputHtml` carries both
  and the Sage kernel emits both, but `text/html` outranks `text/latex` in
  JupyterLab's preference order, so it would also override richer
  representations on objects that have them. `text/latex` is the narrower
  slot.

Not settled here, and mkoeppe's call rather than ours: a Sage kernel requires
an explicit `%display latex`, while a plain kernel has no way to issue one, so
this feature is always-on by construction. Worth asking on the issue before
the PR rather than after.

## Evidence

- claim: no definition of `_repr_latex_()` on current upstream `main`
  check: `git grep -c "def _repr_latex_" eb735110258 -- src/` -> no match, exit 1
- claim: 478 files defining `_latex_()`
  check: `grep -rln "def _latex_" src/ --include=*.py --include=*.pyx | wc -l` -> 478, exit 0
- claim: the fallthrough turns on typeset output under `%display default`
  check: doctest at `src/sage/repl/display/formatter.py` `format`, `sorted(...format(Formula())[0])`
  -> against pristine code `['text/latex', 'text/plain']`, expected `['text/plain']`, 1 failure, exit 1
- claim: the guard restores plain text without breaking third-party latex
  check: same file after the edit is copied into site-packages
  -> 44 of 44 `format` doctests pass; the `Foreign()` case still gives `['text/latex', 'text/plain']`, exit 0
- claim: the `isinstance` narrowing covers real Sage objects
  check: `isinstance(obj, SageObject)` for Rational, Integer, QQ, polynomial,
  polynomial ring, matrix, vector -> True for all seven, exit 0
- claim: `MathJax().eval(obj, mode='plain')` is undelimited
  check: `MathJax().eval(QQ, mode='plain')` -> `\newcommand{\Bold}[1]{\mathbf{#1}}\Bold{Q}`, no `$`, exit 0
- claim: the unpatched stock-kernel repro discriminates
  check: run `repro.py` with the pristine wheel -> rational, polynomial, and
  `QQ` each publish only `text/plain`; the exact-payload assertion fails,
  exit 1
- claim: the hook publishes the same payload as the Sage kernel
  check: temporarily rebuild `sage.structure.sage_object` from the edited
  source and run `repro.py` -> all four bundles contain `text/latex` and
  `text/plain`; payloads are `$\displaystyle \frac{1}{2}$`,
  `$\displaystyle x^{2} + 1$`, `$\displaystyle x < 1$`, and
  `$\displaystyle \newcommand{\Bold}[1]{\mathbf{#1}}\Bold{Q}$`, exit 0;
  restore the installed extension afterward
- claim: The unpatched repro published only
  check: run the four-object repro against the restored wheel -> each bundle
  contains only `text/plain`, and the aggregate assertion fails, exit 1
- claim: A temporary live rebuild published the exact Sage-kernel payloads with both MIME types
  check: compile the edited extension with the current Cython flags, swap it
  into the test venv under a restoration trap, and run the repro -> exact
  rational, polynomial, less-than, and macro payloads pass, exit 0
- claim: HTML escaping is removed from the LaTeX payload
  check: `MathJax().eval(LessThan(), mode='plain')` returns `x &lt; 1`; the
  edited hook returns `$\displaystyle x < 1$`, matching the conversion in
  `OutputHtml.__init__`
- claim: the formatter test passes with the guard live
  check: run the formatter doctest with
  `--environment=sage.all__sagemath_modules` -> the new Sage and foreign
  object examples pass; the only two failures are the unchanged
  `_ipython_float_precision_changed` environment failures
- claim: both package-boundary commands survive tox parsing
  check: `tox c` for `pkgs/sagemath-objects/tox.ini` and
  `pkgs/sagemath-categories/tox.ini` prints each new command in full, exit 0
- claim: the diff is scoped and source-clean
  check: `source-style.sh` -> 0 errors, 0 warnings; `hygiene.sh` with
  `PM_BASE=upstream/main` -> four declared paths, clean whitespace, formatter
  compiles, no debug or lazy-import findings, exit 0
- claim: issue #2236 still needs MathJax formulas
  check: GitHub reports #2236 open and mkoeppe's latest scope comment says
  "Now what remains is mathjax for formulas"; an open-PR search for MathJax
  or `_repr_latex_` returns zero results
- claim: current upstream main was reviewed
  check: GitHub and local `upstream/main` both resolve to `eb735110258`; the
  upstream tree has 478 files defining `_latex_()` and no `_repr_latex_()`
- claim: a stock Google Colab Python kernel renders the exact formula payloads
  check: `colab-formulas.ipynb` records an executed Python 3 kernel cell with
  `text/latex` and `text/plain` for the rational, polynomial, `QQ` macro, and
  less-than payloads; `colab-formulas.png` visibly shows all four typeset,
  including a bold Q and `x < 1`
- claim: It fails against unpatched code and passes after a live rebuild
  check: the restored wheel produces only `text/plain` and exits 1; the
  temporary rebuilt extension produces both MIME types for all four cases and
  exits 0

## Log

- 2026-08-31 SHIPPED. Pushed `fix/mathjax-formulas-2236` to the fork and
  opened passagemath/passagemath PR #2767 from commit `0371bf01c2f`. Verified
  the published base, head, title, body, and commit; the PR is open and not a
  draft.
- 2026-08-31 READY. Verified the saved stock-Colab notebook and screenshot:
  the Python 3 kernel publishes both MIME types for every synthetic payload,
  and the frontend visibly renders the fraction, polynomial, `\Bold{Q}`, and
  raw less-than expression. This completes the frontend half of the
  compositional acceptance check; the local live rebuild already proves that
  the edited Sage objects publish the same strings.
- 2026-08-31 the full mechanical ship gate passes on commit `0371bf01c2f`,
  including scope, source style, negative control, public prose, evidence, and
  all eight red-team axes. The task remained `redteamed` pending the
  stock-Colab visual artifact recorded above.
- 2026-08-31 red team complete on amended commit `0371bf01c2f`. Outside
  review found that the first implementation leaked MathJax's `&lt;` HTML
  escaping into `text/latex`. The hook now reverses the same escape as Sage's
  `OutputHtml`, and the live repro includes `x < 1`. The only remaining
  acceptance blocker is visible rendering in a stock Google Colab Python
  kernel, including the `\Bold` macro; no push or PR until that artifact
  exists.
- 2026-08-31 implementation complete on `fix/mathjax-formulas-2236`: four
  declared files, one atomic commit. Exact stock-IPython payloads pass with a
  temporary live rebuild; Sage display modes and foreign IPython LaTeX hooks
  pass with the formatter edit live.
- 2026-08-31 restored the hand-copied formatter in the PassageMath-local venv
  from `scratchpad/formatter.py.orig`; its checksum now matches upstream. The
  installed `SageObject` extension also remains pristine, so future negative
  controls start from unpatched code.
- 2026-08-31 testing handoff before the restoration recorded above. Two facts
  would have produced false results at that point. First, `.venv`
  site-packages held a hand-copied `sage/repl/display/formatter.py` carrying
  the guard, so a control run in that venv was not pristine. Second, the
  installed `sage_object` remained the wheel:
  `hasattr(SageObject, '_repr_latex_')` is `False`, so `repro.py` still fails
  on all three objects with "MathJax-ready text/latex missing". The earlier
  live proof used a temporary rebuild and restored the wheel afterward.
- 2026-08-31 doctest invocation for this file:
  `python -m sage.doctest --environment=sage.all__sagemath_modules
  src/sage/repl/display/formatter.py`. The default environment fails at
  import with `ModuleNotFoundError: No module named 'sage.all_cmdline'`, and
  `--environment=sage.all__sagemath_repl` adds four spurious failures from
  `identity_matrix` being unavailable. Baseline noise in this file is two
  failures in `_ipython_float_precision_changed`, unrelated to this task and
  present in the control; do not count them as regressions.
- 2026-08-31 unblocked the formatter question and wrote the guard in
  `SageDisplayFormatter.format()`: `TEXT_LATEX`, already defined and unused in
  that module, is added to `exclude` for `SageObject` instances when
  `preferences.text != 'latex'`. Added the regression doctest to `format`.
  Ran the control first, against pristine site-packages code with the new
  docstring: the doctest failed with `['text/latex', 'text/plain']` where
  `['text/plain']` was expected, so it discriminates. Copied the edited module
  into site-packages to prove the edit live, then reran: 44 of 44 `format`
  doctests pass. The two remaining failures in the file are in
  `_ipython_float_precision_changed`, present identically in the control and
  untouched by this change.
- 2026-08-31 confirmed the `isinstance(obj, SageObject)` narrowing is not
  vacuous: Rational, Integer, the `QQ` parent, a polynomial, a polynomial
  ring, a matrix, and a vector are all `SageObject` instances, while the
  `Foreign()` doctest pins that a non-Sage object keeps its own `text/latex`.
- 2026-08-31 reproduced the missing MIME representation with IPython 9.17 and
  PassageMath 10.8.10 while blocking `sage.repl`; all three objects published
  only `text/plain`.
- 2026-08-31 checked current upstream: no open MathJax or `_repr_latex_` PR and
  no `_repr_latex_` definition in the monorepo.
- 2026-08-31 scoped generic formulas separately from the parked mixed-content
  `HtmlFragment` work for #2384.
- 2026-08-31 implementation proved the new hook live, then reproduced a Sage
  kernel regression in all three non-LaTeX text modes; paused before widening
  scope to `src/sage/repl/display/formatter.py`.
- 2026-08-31 second scoping pass on upstream `eb735110258`. Measured that a
  `_repr_latex_` on `SageObject` also fires under a Sage kernel with
  `%display default`, via the `super().format()` fallthrough in
  `SageDisplayFormatter.format()`. Added `src/sage/repl/display/formatter.py`
  to `files`, since no implementation can preserve current Sage-kernel
  behaviour without touching it.
- 2026-08-31 corrected the repro: it asserted equality with
  `MathJax().eval(obj, mode='plain')`, an undelimited body that no frontend
  typesets, so a patch could satisfy it and still not render. It now requires
  the LaTeX body plus math delimiters and prints the Sage-kernel parity
  payload. Still reproduces; still fails on unpatched.
- 2026-08-31 environment obstacle for the implement stage: in `.venv` both
  target files come from wheels, not from the tree.
  `sage.structure.sage_object` resolves to a compiled
  `sage_object.cpython-314-aarch64-linux-gnu.so` in `site-packages` and
  `sage.repl.display.formatter` to the `site-packages` copy, so tree edits
  are invisible until **passagemath-objects** and **passagemath-repl** are
  built from `pkgs/`. The recorded Fedora Asahi recipe builds only
  `sagemath-modules` and `sagemath-plot` from the tree and takes objects and
  categories as manylinux wheels, so this is a new build step, not a
  reinstall.
- 2026-08-31 scope expansion approved; resumed implementation with
  `src/sage/repl/display/formatter.py` included.

## Red team

- [x] relevance: Verified that #2236 remains open, its latest scope comment
  names MathJax formulas as the remaining work, and the stock
  **passagemath-categories** plus IPython repro fails on the restored wheel.
- [x] scope: Compared the amended commit with current `upstream/main`; all
  four changed paths are declared and cover the base hook, Sage formatter
  boundary, objects fallback, or categories-level MIME regression.
- [x] accuracy: Recounted upstream definitions, checked package dependencies
  and the remote main hash, then fixed the outside review's `&lt;` payload
  mismatch and added an exact less-than regression.
- [x] approach: Attacked a narrower per-class hook, a `sage.repl` backend
  probe, and global `text/latex` suppression; each misses formulas or breaks
  package layering and foreign-object display, so the two focused guards stay.
- [x] execution: The restored wheel fails all four repro objects, a temporary
  live rebuild passes their exact MIME payloads, and a stock Colab Python 3
  kernel visibly renders those payloads, including `<` and `\Bold`.
- [x] source-style: The source checker reports zero findings; the full tox
  command blocks were compared for alignment, semantic roles were inspected,
  and the outside review's SymPy capitalization nit was fixed.
- [x] style: Commit and three-paragraph PR drafts pass their prose budgets
  without warnings; categorical PR test claims now have matching command
  evidence instead of relying on an unqualified success statement.
- [x] wording: Narrowed the PR's “enabled whenever” claim to objects with
  `_latex_()` and no custom rich-output hook; the notebook title remains
  limited to the user-visible configuration exercised by the repro.
