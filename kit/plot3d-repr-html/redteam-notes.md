# Red team pass — findings applied

Drafts attacked for relevance, accuracy, style, wording. Seven claims were
wrong or unverified on first draft; all corrected before committing.

## Accuracy defects found and fixed

1. **"#2698 shipped last week."** `7631f4ddf1` is dated 2026-08-28, the same
   day. Changed to "changes what #2698 shipped."
2. **"Two lines in the old method needed sage.repl."** Two *places*, four
   lines: the `get_display_manager` import plus the `threejs_scripts()` call,
   and the `OutputSceneThreejs` import plus the return.
3. **"~180-line body."** Measured: 143 lines, `base.pyx:561-703`.
4. **`base.pyx:1790` for `show()`.** That number came from a pre-#2698 tree.
   On this branch `display_immediately` is at `base.pyx:1991`.
5. **"display_manager.py holds at 86."** Before-count was never measured.
   Reworded to a claim about the after state only.
6. **Truncated AttributeError.** The control run prints
   `'sage.plot.plot3d.shapes.Sphere'`, not `'Sphere'`. Quoted verbatim.
7. **Tox comment justified the ungated check with "threejs is a required
   dependency."** True (`jupyter-threejs-sage`, `m4/sage_spkg_versions.m4:383`)
   but not the reason: the online tag reads only
   `sage/ext_data/threejs/threejs-version.txt`, which `passagemath-plot`
   grafts in its own MANIFEST. Comment rewritten to the real reason.

## Omissions found

8. **Payload cost went unmentioned.** Every plain-kernel cell now carries both
   representations: 113493 bytes of escaped HTML plus a 30660-byte PNG for
   `sphere()`. Added, with the `Graphics` precedent (`image/png` +
   `image/svg+xml` since #2351) so it reads as consistent rather than new.
9. **"Does this change the Sage kernel?" went unanswered.**
   `SageDisplayFormatter.format()` returns the rich-output bundle and reaches
   IPython's formatters only when that bundle is plain text alone
   (`formatter.py:198-201`). Added.

## Style

No em dashes, no personal pronouns, no AI-speak in either draft (grep-checked).
Summary line 68 characters.

## Verification log

- `sage/plot/plot3d/base.pyx`: 406 -> 416 doctests, all pass.
- `sage/plot`: 2742 doctests, all pass.
- `sage/features/threejs.py`: 7 -> 9, pass.
  `sage/repl/rich_output/display_manager.py`: 86, pass.
- `sage/repl/rich_output/backend_ipython.py`: 3 failures in
  `BackendIPython.install`, present on the pristine tree too. Unrelated.
- Guard is not decoration: the tox one-liner run against the pristine `.so`
  fails with `AttributeError: 'sage.plot.plot3d.shapes.Sphere' object has no
  attribute '_repr_html_'`.
- Blocked-import venv (`sys.modules["sage.repl"] = None`), stock IPython
  `DisplayFormatter`: `['image/png', 'text/plain']` ->
  `['image/png', 'text/html', 'text/plain']`.
- `gyroid-threejs-colab-style.png`: `_repr_html_()` output of a 60-point
  gyroid, screenshotted by headless Chrome, `sage.repl` blocked, three.js from
  jsdelivr. The scene renders.

## Not done

Nothing pushed, nothing posted. Branch `feat/graphics3d-repr-html` is committed
locally at `79022f8b21` on top of `origin/main`.

---

# Second pass: Codex review

Four findings, all valid. Code unchanged; claims and evidence corrected.

10. **`save('.html')` without `online=True` still needs sage.repl.** Confirmed:
    with `sys.modules["sage.repl"] = None`, `save(f, online=True)` writes 91257
    bytes and plain `save(f)` raises `ModuleNotFoundError`. Not a regression;
    on the pristine build *both* forms raise, because `_rich_repr_threejs()`
    needed sage.repl for the script tag and the container. Making plain
    `save()` repl-free would mean flipping the `online` default, changing what
    every existing `save('foo.html')` embeds. Out of scope, so both drafts now
    state the limit. The `.html` save doctest already passes `online=True`,
    which is the tested path.
11. **"2742 in sage/plot, all pass" was environment-specific.** True under
    `--environment=sage_plot3d_env`, false under
    `--environment=sage.all__sagemath_plot`, where `sage/plot/histogram.py`
    has 3 failures. Those are recorded in
    `pkgs/sagemath-plot/known-test-failures.json` as
    `{"failed": true, "ntests": 39}`, so they are baseline, not caused here.
    The aggregate is dropped; the drafts cite only the 416 in `base.pyx`.
12. **Headless Chrome did not meet the evidence bar.** Replaced. A notebook
    now executes on the stock `python3` kernel through `nbconvert --execute`;
    its first cell asserts `IPython.core.formatters.DisplayFormatter`, and the
    gyroid cell output carries `['image/png', 'text/html', 'text/plain']`
    (128596 / 10767295 / 17 bytes). `plain-kernel-notebook.png` is that
    notebook rendered. Colab itself is still unreached.
13. **"Artifacts not present."** They are, at
    `passagemath-workspace/kit/plot3d-repr-html/`, not under the
    `passagemath/passagemath` checkout.

Both drafts were also cut for length against the style guide: commit 46 to 22
lines, PR body 51 to 35.

---

# Third pass: Codex on the full artifact set

Eight findings. Seven fixed, one answered with evidence and deliberately not
acted on. No code changed; the implementation survived on every technical
claim. Commit reamended to `23afe7bc99`.

14. **[P2] Unsandboxed iframe. Not acted on, and now with a concrete reason.**
    Tested rather than argued: a sphere page in an iframe with
    `sandbox="allow-scripts"` and one without screenshot byte-identically
    (sha256 `60d1645e2463b616...`), and nothing under
    `src/sage/ext_data/threejs` touches localStorage, sessionStorage, cookies,
    `parent`, `top`, or `postMessage`. So the sandbox looks free, but it is
    not: `threejs_template.html:507-525` defines `saveAsPNG()` and
    `saveAsHTML()`, both `a.download` plus `a.click()`, which a sandbox blocks
    without `allow-downloads`. Adding `sandbox` to the newest of three
    identical wrappers would harden one path while silently breaking two
    viewer menu items, and leave the other two wrappers exposed anyway. The
    PR body now states the exposure, that it is inherited rather than
    introduced, and why sandboxing is one change across all three.
15. **[P2] "imports nothing from `sage.repl`" was false.** Correct: the
    `online=False` branch of `_render_html_()` imports the display manager at
    `base.pyx:631`, and the body contradicted itself two paragraphs later.
    Sentence removed; the limitation is now stated once, in the paragraph that
    introduces the method.
16. **[P3] #2351 attribution wrong.** Verified: `_repr_svg_` is commit
    `7a2b957867`, merged by `e84c20adb2` from `sacchen/feat/plot-repr-svg`,
    which is PR #2366. #2351 is PNG only. Both drafts corrected.
17. **[P3] "Its docstring moves with it" overstated.** True only of the TESTS
    markers; the header, INPUT, OUTPUT and EXAMPLES were rewritten and
    `_rich_repr_threejs()` got a fresh wrapper docstring. Diff-mechanics
    paragraph now says exactly that.
18. **[P3] Prompt's pristine-control recipe was false-green.** `git stash` on
    a clean tree with the change committed rebuilds the patched source.
    Replaced with the worktree/archive recipe Codex actually used.
19. **[P3] "Every venv here has passagemath-repl" was false.**
    `.venv-explore` does not. Narrowed, with the instruction to check
    `find_spec` rather than assume either way.
20. **[P3] Paragraph limits exceeded.** Commit was four body paragraphs, now
    three. PR body was seven blocks, now opener plus three plus the
    diff-mechanics callout the guide allows separately.
21. **[P3] Notebook artifact carried no outputs.** Correct, and deliberate:
    executed it is 10.9 MB of escaped Three.js. Renamed to
    `plain-kernel-gyroid-REPRODUCER.ipynb` so its role is unambiguous, with
    `plain-kernel-evidence.txt` recording the measured bundle and the exact
    command to regenerate.

On Codex's untested item: #2698 did promise this as a separate PR. Its body
ends "`_repr_html_()` is left out. `_rich_repr_threejs()` imports `sage.repl`
for the script tag and to wrap the HTML, so the raw HTML would need extracting
first. Better as its own PR." Retrievable with `gh pr view 2698 --json body`.

---

# Fourth pass: cross-session ledger review

Two findings. One wording defect fixed; one "unrun" item re-run against the
real base and recorded reproducibly. Commit reamended to `38a7ac5a54`.

22. **"a container that ships only in passagemath-repl" was unestablished.**
    Correct, and the reviewer's own self-correction is right: the evidence is
    not "two manifests graft sage/repl". It is that
    `pkgs/sagemath-repl/MANIFEST.in:6` grafts `sage/repl` explicitly while
    `pkgs/sagemath-standard-no-symbolics/MANIFEST.in:7` grafts all of `sage`
    with its `prune sage/repl` commented out at line 86, and no uncommented
    `prune sage/repl` exists in any manifest. Verified here. That leaves the
    absolute claim unsupported, and it contradicts
    [[passagemath-modular-boundary-testing]], which records the opposite.
    Not settled, and not worth settling, because the claim the change depends
    on is narrower: `pkgs/sagemath-plot/pyproject.toml.m4` lists
    `SPKG_INSTALL_REQUIRES_sagemath_repl` only in the `test` extra at line 45,
    never in `dependencies` at line 23. Reworded to "absent from a plain
    passagemath-plot install, which does not depend on passagemath-repl".
    The memory file needs revisiting separately.
23. **"Never verified: 406 to 416, and the AttributeError control."** Both had
    been run, but against a `.so` built from `96020c74ac` and a `git stash`
    control taken while the change was still uncommitted, neither of which a
    reader can reproduce from the repo as it stands. Re-run against a real
    `origin/main` worktree (`bf492a075b`), rebuilding `base.pyx` from that
    tree's `src` and installing that tree's `threejs.py` and
    `display_manager.py`:

      pristine  base.pyx 406, threejs.py 7, display_manager.py 86, all pass
                tox guard, extracted from tox.ini with shlex and run verbatim:
                exit 1, AttributeError: 'sage.plot.plot3d.shapes.Sphere'
                object has no attribute '_repr_html_'
      patched   base.pyx 416, threejs.py 9, display_manager.py 86, all pass
                tox guard: exit 0

    The guard is a real negative control, not decoration. Worktree removed;
    the venv holds the patched build.

Also adopted: "never needed a backend" softened to "needs no backend" in both
drafts, same absolute-claim shape as finding 22.
