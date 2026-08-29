# Red-team prompt: Graphics3d._repr_html_()

You are red-teaming a feature commit and its two drafts for passagemath before
they are pushed upstream. Your job is to break the work: find factual errors,
unsound reasoning, untested paths, behavior regressions, and writing problems.
Assume the author is wrong until the evidence in front of you says otherwise.
Reproduce every claim yourself; do not trust the author's transcripts or the
notes in `redteam-notes.md`. Report findings only: do not fix, amend, commit,
push, or file anything.

## What the change is for

Plain Python kernels (Colab, marimo, JupyterLite, VS Code) use stock IPython,
which looks for `_repr_html_()`. `Graphics3d` had only `_rich_repr_()`, so 3D
plots printed `Graphics3d Object`. #2351 fixed 2D, #2698 added a Tachyon
`_repr_png_()` for 3D. This is the third: the interactive Three.js scene.

## The claims under attack

1. **Extraction is behavior-preserving.** The 143-line body of
   `_rich_repr_threejs()` moved into `_render_html_(**kwds)` unchanged except
   for two lines becoming seven where the script tag is chosen, and two
   becoming one at the return. For any object and any kwds, the page bytes are
   identical to what `origin/main` produced.
2. **`_repr_html_()` works with `sage.repl` absent** and returns an
   `<iframe srcdoc>` carrying the escaped document with a CDN script tag.
3. **`_repr_html_()` forces `online=True`**, overriding an `online=False`
   saved on the object, and that is the right call rather than a bug.
4. **`Threejs.cdn_scripts()` is byte-identical** to the string the old inline
   branch of `DisplayManager.threejs_scripts()` built, so no consumer of
   `threejs_scripts(online=True)` sees a change. Two consumers exist:
   `backend_ipython.py:583` and `backend_marimo.py:244`.
5. **`save('foo.html')` writes the same bytes as before.** It went from
   `OutputSceneThreejs(...).html.save_as(filename)` to
   `open(filename, 'wb').write(page.encode('utf-8'))`.
6. **`save('foo.html')` still needs passagemath-repl unless called with
   `online=True`, and that is not a regression** (the author claims both forms
   raise on `origin/main`).
7. **The Sage kernel never consults `_repr_html_()`**, because
   `SageDisplayFormatter.format()` returns the rich-output bundle and reaches
   IPython's formatters only when that bundle is plain text alone
   (`src/sage/repl/display/formatter.py:198-201`).
8. **The mimetype bundle changed as stated**: a plain kernel goes from
   `['image/png', 'text/plain']` to
   `['image/png', 'text/html', 'text/plain']`, and HTML-capable frontends will
   now show the scene where #2698 gave them a PNG.
9. **The tox guard is meaningful**, not decoration: it fails on an unpatched
   build. It is correctly left ungated, unlike the `_repr_png_()` check beside
   it which is gated on `!notest:` and on the Tachyon executable.
10. **Doctest counts**: `plot3d/base.pyx` 406 to 416, all passing;
    `sage/features/threejs.py` 7 to 9.
11. **The drafts are accurate and meet the style guide**
    (`~/.claude/commit-pr-style.md`): commit is imperative summary at most 72
    chars plus short paragraphs; PR body is opener, at most three short
    paragraphs, a diff-mechanics callout, evidence with numbers; no personal
    pronouns, no em dashes, no AI speak, every claim checkable.

## Artifacts

- Repo: `~/foundry/sandbox/passagemath/passagemath`, branch
  `feat/graphics3d-repr-html`, commit `a600d6387d`, one ahead of
  `origin/main`. Four files, +161/-26.
- Drafts and evidence live in
  `~/foundry/sandbox/passagemath-workspace/kit/plot3d-repr-html/`,
  NOT under the source checkout. A previous reviewer reported them missing by
  looking in the wrong root.
  - `commit-message.txt`, `pr-body.md`: the drafts under attack.
  - `redteam-notes.md`: two prior review passes. Treat as claims, not facts.
  - `plain-kernel-notebook.png`, `plain-kernel-gyroid.ipynb`,
    `make-plain-kernel-notebook.py`: the evidence artifact and its generator.
- `kit/plot3d-repr/rebuild.sh <venv> <dotted.module>`: rebuilds one .pyx into
  a venv.

## Environment facts (verify, then rely on)

- Venv: `~/foundry/sandbox/passagemath/.venv-plot3d` (Python
  3.12). It currently holds the PATCHED build of `sage.plot.plot3d.base` plus
  patched copies of `sage/features/threejs.py` and
  `sage/repl/rich_output/display_manager.py` in site-packages.
- **`sage -t` reads docstrings from the repo file but imports code from
  site-packages.** Editing repo source alone gives false-green doctests. The
  change under review is COMMITTED and the tree is clean, so `git stash` does
  nothing and rebuilding after it just reinstalls the patched code. For a real
  pristine control, extract `origin/main` into a temporary tree
  (`git worktree add` or `git archive origin/main | tar -x -C <tmp>`), run
  `rebuild.sh` against that `src` directory, copy the pristine
  `sage/features/threejs.py` and `sage/repl/rich_output/display_manager.py`
  into site-packages, test, then restore the patched build byte-for-byte.
  Always run a control; never compare against "all tests passed" from the
  shipped wheel.
- **The venvs you are likely to reach for all have `passagemath-repl`
  installed** (`.venv`, `.venv311`, `.venv-plot3d`, `.venv-plot3d-notachyon`;
  `.venv-explore` does not, but lacks the rest of the plot stack). Check with
  `importlib.util.find_spec("sage.repl")` rather than assuming either way, and
  test no-repl claims with `sys.modules["sage.repl"] = None` set before the
  first import.
- **Doctest results depend on the environment module.**
  `--environment=sage_plot3d_env` (a local shim that imports
  `sage.all__sagemath_symbolics` then `sage.all__sagemath_plot`) and
  `--environment=sage.all__sagemath_plot` (what tox and CI use) disagree.
  Under the latter, `sage/plot/histogram.py` has 3 failures; they are recorded
  in `pkgs/sagemath-plot/known-test-failures.json` as
  `{"failed": true, "ntests": 39}`. Establish which environment any count you
  check or dispute was measured in before calling it wrong.
- Leave the repo on `feat/graphics3d-repr-html` with a clean tree and the venv
  holding the patched build when done.

## Minimum attack surface

- **Prove or break claim 1 by diffing output, not by reading.** Render a set of
  objects (sphere, an animation with 2+ frames, a thick line, a `mesh=True`
  dodecahedron, a `page_title` with markup, a `viewpoint`, a bad `projection`,
  a bad `theme`, `axes_labels_style` as dict and as list) on `origin/main` and
  on the branch, and compare bytes. Hunt for a kwds combination where they
  differ, especially around `options.setdefault('online', False)`.
- **Attack the double escaping.** `_render_html_()` HTML-escapes `page_title`
  into the document; `_repr_html_()` then escapes the whole document into
  `srcdoc`. Confirm a browser unescaping `srcdoc` gets back exactly the
  document, and that a hostile `page_title` cannot break out of the attribute
  or inject into the parent page. Try quotes, `</iframe>`, backslashes,
  non-ASCII, lone surrogates.
- **Attack claim 3.** Find a real setup where forcing the CDN is the wrong
  answer: an air-gapped JupyterLab with the `threejs-sage` nbextension
  installed, a locked-down corporate network, a JupyterLite build. Decide
  whether silently overriding a user's explicit `online=False` is defensible or
  should raise, warn, or fall back.
- **Attack claim 5 on encoding.** The old path went through `OutputBuffer`;
  the new one encodes utf-8 by hand. Check a non-ASCII `page_title` round-trips
  identically, and that no newline translation or BOM was introduced.
- **Attack claim 9.** Run the tox one-liner verbatim against a pristine build
  and confirm it fails. Check its shell quoting parses under `shlex` the way
  tox will. Then ask whether it would still pass in an install with no
  `threejs-sage` package at all, since the author claims it needs only
  `sage/ext_data/threejs`, and check that `graft sage/ext_data/threejs` in
  `pkgs/sagemath-plot/MANIFEST.in` actually ships `threejs-version.txt`.
- **Attack claim 7 empirically**, not by reading the source. The author could
  not construct a working `SageDisplayFormatter` in this venv and fell back to
  reading `formatter.py`. Find a way to actually exercise it, or report the
  claim as untested.
- **Hunt for callers the author missed.** `_rich_repr_threejs`,
  `threejs_scripts`, `html.save_as`, and anything reaching
  `OutputSceneThreejs` across the whole tree, including `.rst` docs and other
  `pkgs/*`.
- **Attack the drafts line by line.** Every number (143, 406, 416, 7, 9, two
  becoming seven, two becoming one), every file:line reference
  (`base.pyx:1989-1991`, `formatter.py:198-201`), every attribution (#2351
  paired png and svg; #2698 said this was better as its own PR), and every
  style constraint. Does the commit overclaim? Does the diff contain anything
  the message does not admit to?
- **Ask what is missing.** Should `_repr_html_()` and `_render_html_()` appear
  in the class docstring's `.. automethod::` list? Should the iframe carry a
  `sandbox` attribute or a fixed height at all? Is a third copy of the iframe
  markup the right call against moving it somewhere all three backends reach?

## Report format

Rank findings by severity (behavior regression > correctness > untested claim >
factual error in a draft > wording). For each: the claim attacked, the evidence
(commands run and their actual output), and whether the finding is CONFIRMED or
SUSPECTED. Close with the claims that survived attack, and the claims that could
not be tested in this environment, stated as such. An empty findings list is an
acceptable outcome; an unverified "looks good" is not.
