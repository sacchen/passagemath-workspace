# Adapt `sage-discrete-math` to run on passagemath

_Python + basic XML editing. No Sage or Cython knowledge needed. See [issue #2290](https://github.com/passagemath/passagemath/issues/2290)._

**Repo:** https://github.com/SageMathOER-CCC/sage-discrete-math — CC-BY, fork freely

**What it is:** an open discrete math textbook built in [PreTeXt](https://pretextbook.org/) (XML source → HTML + PDF). Code examples are embedded as `<sage>` blocks that render as live cells in the browser.

```bash
uv venv .venv && uv pip -p .venv install passagemath-combinat passagemath-graphs
uv tool install pretext   # to build/preview the book locally
```

## What we're doing

Right now the book tells students to sign up for CoCalc to run code. We want to update it so students can use Google Colab + passagemath instead — no account wall, no CoCalc-specific workflow. Along the way, a few Sage-only syntax quirks need swapping for plain Python.

There are three layers of work, roughly in order of effort.

---

## Part 1 — Update the getting-started chapter

This is three files. Start here.

**`source/getting-started/sec-sage-browser.ptx`** — the whole section is a 10-step CoCalc signup walkthrough. Replace it with Colab + passagemath instructions:

1. Go to [colab.research.google.com](https://colab.research.google.com) and open a new notebook
2. In the first cell, run: `%pip install passagemath-combinat passagemath-graphs`
3. In the next cell, try: `from sage.combinat.all import *`
4. You're ready — shift+enter runs a cell, same as everywhere else

**`source/getting-started/ch-getting-started.ptx`** — the intro paragraph says "SageMathCell, CoCalc, and a local installation." Update the framing to match the new instructions above.

**`source/getting-started/sec-intro-to-sage.ptx`** — documents `^` as an exponentiation operator and notes it's a Sage thing. Remove that and keep only `**`. In Python, `^` is bitwise XOR — it won't error, it'll just silently give the wrong answer.

---

## Part 2 — Syntax cleanup across the whole book

Run these to find what needs changing:

```bash
rg '\^' source/ -l           # ^ exponentiation — should be **
rg '^\s*!' source/ -l        # ! shell prefix — not valid Python
rg 'Set\(' source/ -l        # Sage's Set() — may need imports or stdlib swap
```

**`^` → `**`** — straightforward find-and-replace inside `<sage>` blocks. Also update any surrounding prose that mentions `^` as Sage syntax.

**`!` shell commands** — only in `sec-miscellaneous.ptx` (`!ls -la`, `!printf ...`). These are Jupyter magic, not passagemath-specific. Either swap for Python equivalents (`os.listdir()`, `subprocess.run(...)`) or drop the subsection — it's not core to discrete math.

**`Set()`** — Sage's `Set([1,2,3])` has a few methods Python's builtin `set` doesn't. Quick reference:

| Sage | Replacement |
|---|---|
| `Set([1,2,3])` | `{1, 2, 3}` (most cases) |
| `.cardinality()` | `len()` |
| `.issubset(other)` | `.issubset(other)` (same) |
| `.subsets()` | `from sage.combinat.all import Subsets` then `Subsets([1,2,3])` |

Where you need passagemath, add the import at the top of the cell rather than relying on it being pre-loaded.

**Rational division** — `5 / 3` gives `5/3` (exact fraction) in SageMath because the Sage preparser silently wraps integer literals in `Integer()`. That preparser doesn't run in Colab — passagemath is just a library there — so `5 / 3` returns `1.666...` like normal Python. This is a real behavioral difference. Where the book relies on exact rational output, update the examples to be explicit: `Integer(5) / Integer(3)` or `QQ(5) / QQ(3)`. Add the imports at the top of the cell:

```python
from sage.rings.integer import Integer
from sage.rings.rational_field import QQ
```

---

## Part 3 — What to do about the interactive cells (the open question)

The `<sage>` tags in PreTeXt source render as live cells powered by `sagecell.sagemath.org`. That server runs full SageMath, not passagemath. There's no passagemath-backed equivalent yet.

Three options — pick one or check with mkoeppe before starting Part 3:

**A. Wait for infrastructure.** PreTeXt issue [#2803](https://github.com/PreTeXtBook/pretext/issues/2803) may produce a Colab-based interactive cell option. If that lands, we can keep `<sage>` tags and just update the backend. Good if you have patience.

**B. Companion Colab notebooks (recommended for now).** Keep `<sage>` tags in the source (SageCells will still run — but note: after Part 2, cells with passagemath-specific imports won't work on `sagecell.sagemath.org`, so this is an interim state). Add a Colab notebook per chapter in a `notebooks/` folder. Each notebook has a passagemath install cell up top, then mirrors the code examples. Add a link at the start of each chapter. Students who want to experiment open the notebook; readers following along in the book see static output. This is fully unblocked.

**C. Convert `<sage>` to static code blocks.** Change `<sage><input>…</input></sage>` to `<program language="python">…</program>` everywhere. The code no longer runs in the browser — it just displays. Least effort, least interactivity. Fine if the goal is a clean passagemath edition and the Colab notebooks cover hands-on use.

---

## Checking your work

```bash
pretext build && pretext view
```

- New reader can get set up using only Colab — no CoCalc account created
- `rg '\^' source/` shows no remaining hits in code cells (hits in prose or `<m>` math tags are fine — check manually)
- All code examples run clean in `.venv` with passagemath-combinat + passagemath-graphs
