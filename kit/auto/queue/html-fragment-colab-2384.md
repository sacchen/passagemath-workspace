---
slug: html-fragment-colab-2384
state: parked
issue: 2384
pr:
branch: fix/html-fragment-repr-html-2384
venv: .venv
tier: intermediate
snt: tractable
files:
  - src/sage/misc/html.py
doctest_cmd: >-
  ../.venv/bin/python -m sage.doctest --environment
  sage.all__sagemath_categories src/sage/misc/html.py
repro: kit/auto/artifacts/html-fragment-colab-2384/repro.py
repro_status: reproduced
expected_failure: >-
  The unpatched object publishes only text/plain; the experimental patch
  publishes the same text/html payload as IPython.display.HTML(raw_latex),
  which issue #2384 reports does not render in Colab.
negative_control: fail-on-unpatched
---

# Render LP dictionary output in Colab

## Pause point

This task is deliberately parked. Do not ship the saved experimental patch
as a fix for #2384. It proves that `HtmlFragment._repr_html_()` makes plain
IPython publish `text/html`, but red-team review found that the result is
byte-for-byte equivalent to the workaround that the issue already reports as
non-rendering.

The PassageMath checkout was left on branch
`fix/html-fragment-repr-html-2384` with one uncommitted modification to
`src/sage/misc/html.py`. A copy of that diff is saved as
`kit/auto/artifacts/html-fragment-colab-2384/experimental.patch`.

## Symptom

With `passagemath-polyhedra` in Google Colab,
`LPAbstractDictionary.run_dual_simplex_method()` and
`run_simplex_method()` return an `HtmlFragment`, but Colab shows its embedded
LaTeX as raw text instead of rendering the dictionary tables. The output
contains `\\begin{equation*}` blocks and prose containing `$...$` math.

Issue: https://github.com/passagemath/passagemath/issues/2384

## Root cause status

The local cause of the plain-text fallback is understood:

1. The simplex methods assemble their transcript in
   `src/sage/numerical/interactive_simplex_method.py` and return an
   `HtmlFragment`.
2. Sage's rich-output manager knows how to package this as `OutputHtml`.
3. Plain IPython does not consult `_rich_repr_()`, and `HtmlFragment` has no
   standard IPython representation hook, so only `text/plain` is published.

That is not yet the complete Colab rendering cause. Adding `_repr_html_()`
publishes the raw string as `text/html`, but the issue says
`display(HTML(raw_latex))` also fails. The saved experiment produces exactly
the same payload and metadata as that workaround.

## Rejected approach

Do not merge the saved global `HtmlFragment._repr_html_()` change under
#2384 without a successful target-frontend test. Its `<b>test</b>` doctest
checks generic HTML MIME publication, not MathJax rendering of the LP
transcript in Colab.

Also do not add `_repr_latex_()` globally to `HtmlFragment`: the class holds
arbitrary real HTML as well as MathJax-bearing fragments, so treating every
instance as LaTeX would break its abstraction.

## Resume checklist

1. Open a real Google Colab notebook using its stock Python kernel.
2. Install `passagemath-polyhedra` and construct the exact LP from #2384.
3. Save the returned `HtmlFragment` as `result` and test this representation
   matrix independently:
   - `display(HTML(str(result)))` (known reported failure)
   - `display(Latex(str(result)))` (`text/latex`; first candidate)
   - an HTML payload with explicit MathJax delimiters/wrappers
   - any Colab-native MIME representation discovered from the first two
4. Record which MIME type and exact payload visually render both equation
   tables and intervening prose. Save a screenshot or notebook output.
5. Implement the narrowest representation that works:
   - Prefer a dedicated math-aware fragment/result type if `text/latex`
     works.
   - If transformed HTML works, decide whether the conversion belongs in a
     reusable MathJax-fragment abstraction or only in the simplex output.
   - Do not infer frontend support from Sage backend capabilities.
6. Replace the generic regression proof with the exact LP result. Preserve
   separate controls for ordinary HTML and `BackendSimple`.
7. Re-run an unpatched negative control, the patched doctest, source-style,
   and the real Colab rendering check before moving this task out of
   `parked`.

## Evidence

- claim: The unpatched `HtmlFragment` publishes only `text/plain` in plain IPython.
  check: `DisplayFormatter().format(HtmlFragment('<b>test</b>'))` -> MIME keys `['text/plain']` in IPython 9.10 and 9.11.
- claim: The experimental patch publishes `text/html` while retaining `text/plain`.
  check: dynamic `_repr_html_ = lambda self: str(self)` -> MIME keys `['text/html', 'text/plain']`.
- claim: The experimental patch is equivalent to the workaround reported as failing.
  check: `kit/auto/artifacts/html-fragment-colab-2384/repro.py` -> payload equality `True`, metadata equality `True`, identical MIME keys.
- claim: The exact LP result contains equation environments.
  check: the repro prints `contains_equation: True` and result type `sage.misc.html.HtmlFragment`.
- claim: The doctest discriminates against unpatched code.
  check: running the modified source doctest against the restored installed package -> 72 tests, 3 expected failures (`AttributeError`, `AttributeError`, `KeyError`).
- claim: The experimental patch passes its local doctests when installed temporarily.
  check: temporarily copy modified `html.py` into `.venv` site-packages, run the declared command, then restore -> 72 tests passed.
- claim: Sage's non-target simple backend is unchanged.
  check: `HtmlFragment('<b>test</b>')._rich_repr_(BackendSimple)` -> `OutputPlainText` before and after the experiment.
- claim: The saved source diff has no whitespace errors.
  check: `git diff --check` -> exit 0.
- claim: The saved source diff passes the kit's scope and source-editorial checks.
  check: `hygiene.sh` -> all checks passed; `source-style.sh` -> 0 errors, 0 warnings.

The checkout-level `uv run ruff check src/sage/misc/html.py` was not completed:
the repository's uv build environment lacks `mesonpy`. This is an environment
gap, not a successful lint result.

## Log

- 2026-08-29 scoped a generic `HtmlFragment._repr_html_()` experiment.
- 2026-08-29 verified unpatched formatter behavior, patched MIME behavior,
  the exact LP result, the patched doctest, and `BackendSimple`.
- 2026-08-29 red team found the patched payload identical to
  `IPython.display.HTML(raw_latex)`, which #2384 reports does not render.
- 2026-08-29 kit hygiene and source-style checks passed for the experimental
  PassageMath diff.
- 2026-08-29 parked pending a real Colab representation matrix.

## Red team

- [x] relevance: blocked shipment because MIME publication alone does not establish visible rendering for #2384.
- [x] scope: the experiment touches only `src/sage/misc/html.py`, but a correct fix may belong at the simplex or math-fragment layer.
- [x] accuracy: reproduced the exact LP type and payload and compared complete formatter MIME bundles and metadata.
- [x] approach: rejected a global HTML hook as the issue fix until its output works in the target frontend.
- [x] execution: negative control and patched doctest discriminate; actual Colab rendering remains deliberately unclaimed.
- [x] source-style: the experimental docstring is structurally valid, but its frontend claim is broader than the evidence.
- [x] style: no unrelated cleanup or formatting changes are present.
- [x] wording: future issue and PR prose must say “in Colab” only after a real Colab validation.
