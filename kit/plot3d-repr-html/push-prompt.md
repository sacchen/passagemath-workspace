# Prompt: push and open the PR for Graphics3d._repr_html_()

Delivery, not authorship. The branch is finished and reviewed. Do not touch
the code, do not rewrite the drafts, do not open or comment on anything else.

## State

- Repo `~/foundry/sandbox/passagemath/passagemath`, branch
  `feat/graphics3d-repr-html`, commit `38a7ac5a54`, one commit ahead of
  `origin/main`, tree clean, 4 files, +161/-26.
- Push to `fork` (`git@github.com:sacchen/passagemath.git`). Never to `origin`.
- The branch is ALREADY on the fork, pushed as a backup on 2026-08-29. It is
  only a branch: no pull request exists anywhere, and nothing upstream was
  touched.
- Drafts and evidence: `~/foundry/sandbox/passagemath-workspace/kit/plot3d-repr-html/`

## Pre-flight

Stop and report if any of these fails.

1. `git status --porcelain` is empty.
2. `git log --oneline origin/main..HEAD` is exactly `38a7ac5a54`.
3. `git fetch origin`, then confirm the branch is still one ahead. If
   `origin/main` moved, rebase, never merge, and say so.
4. `git ls-remote --heads fork feat/graphics3d-repr-html` returns a SHA (the
   backup). Confirm it is the same work: `git fetch fork` then compare
   `git rev-parse fork/feat/graphics3d-repr-html^{tree}` against
   `git rev-parse HEAD^{tree}`. Equal trees mean the push below is a no-op.
   If yours is a newer amend of the same change, the push needs
   `--force-with-lease`. If the fork holds content you do not have, stop.

## Push and open

```
git push fork feat/graphics3d-repr-html   # add --force-with-lease if amended
gh pr create --base main --head sacchen:feat/graphics3d-repr-html \
  --title "plot3d: add Graphics3d._repr_html_() for interactive 3D in notebooks" \
  --body-file ~/foundry/sandbox/passagemath-workspace/kit/plot3d-repr-html/pr-body.md
```

Title is the commit summary verbatim. Body is `pr-body.md` verbatim. No bare
`--force`, and no `-u`: the local branch tracks `origin/main` on purpose, which
is what makes the one-commit-ahead checks above work. No footers or
generated-by lines.

## The screenshot

The body's evidence paragraph promises a screenshot that is not in it. `gh`
cannot upload images, so after the PR exists, give the user the URL and ask
them to drag `plain-kernel-notebook.png` into the description in the browser.

Do not work around this by committing the PNG, pushing a scratch branch, or
making a gist. If the user declines, edit only the sentence beginning "The
screenshot is a notebook" to describe the measurement without promising an
image.

## Do not

- Push to `origin`, or bare-force-push, amend, or rebase without saying so.
- Edit any source file. Report a suspected bug rather than fixing it here.
- Rewrite the body for style. Every number in it is measured; if you think a
  claim is wrong, verify it and report.
- Link the PR as closing #2236. It refs the issue and leaves it open, because
  the LaTeX half is unaddressed.
- Start the follow-up `show()` work.

## After

Report the PR number, the URL, and what CI is doing at first glance. Then
stop. Do not babysit CI.

Measured numbers behind the body are in `redteam-notes.md`; how to reproduce
them is in `redteam-prompt.md` and `plain-kernel-evidence.txt`.
