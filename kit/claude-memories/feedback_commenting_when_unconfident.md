---
name: Commenting on issues when diagnosis is uncertain
description: Post raw log facts without interpretation when you can't confidently diagnose a bug
type: feedback
---

When investigating a CI failure or bug that's outside our expertise, post the raw facts (failing assertion, file, line number) without a diagnosis rather than staying silent or guessing.

**Why:** Saves whoever fixes it from pulling logs themselves. Zero risk of wrong attribution. Still useful even when we don't understand the math.

**How to apply:** If we can extract the failing test, the exact assertion error, and the relevant file/line from CI logs — post that. Don't add "I think the issue is..." unless confident. Example from #2288: posted the failing cellular basis assertion and stack trace without claiming to know why.
