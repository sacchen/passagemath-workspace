---
name: Verify Gemini's code before committing
description: Gemini has made implementation errors that look correct on the surface; always verify before committing
type: feedback
---

Always verify Gemini's generated code against the actual codebase before committing.

**Why:** Gemini made `lazy_import('', 'sympy')` — syntactically valid Python but semantically broken (empty string as module name). Also claimed padic_extension_leaves.py and multi_polynomial_ideal.py were "false positives" when they were true bugs (Gemini confused which version of the file it was reading).

**How to apply:**
- `py_compile` every changed file
- For `lazy_import` calls: verify the module name is a real importable module, not empty string
- When Gemini says "verified by code reading" — re-read the relevant lines yourself
- Check `git diff main --check` for trailing whitespace before committing (Gemini introduced a trailing space on a blank line in multi_polynomial_ideal.py)
