---
name: GitHub PR body formatting
description: How to format PR bodies correctly for GitHub Markdown — no hard line wraps within paragraphs
type: feedback
---

**Always use `--body-file <tmpfile>` instead of `--body`** — the shell interprets backticks in `--body` strings as command substitutions, silently deleting all inline code. Write the body to a temp file with the Write tool, then pass `--body-file /tmp/....md`.

Write each paragraph as a single unbroken line. GitHub Markdown treats a single newline as a line break, so wrapping prose at 80 chars creates visible mid-sentence breaks in the rendered PR.

**Why:** GitHub does not collapse single newlines in paragraph text the way some Markdown renderers do. A hard wrap at column 80 renders as a `<br>` in the output.

**How to apply:** In any `gh pr create` or `gh pr edit --body` heredoc, keep each paragraph on one line no matter how long. Only use newlines to separate paragraphs (blank line between them) or for literal code blocks (4-space indent or fences). The shell heredoc will preserve the single long line correctly.

Example — wrong (causes mid-sentence breaks):
```
After #2282 replaced the module-level `try/except ImportError` with
`lazy_import(...)`, every instance failed to pickle.
```

Example — correct:
```
After #2282 replaced the module-level `try/except ImportError` with `lazy_import(...)`, every instance failed to pickle.
```
