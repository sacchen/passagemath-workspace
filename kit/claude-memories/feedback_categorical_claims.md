---
name: Verify completeness before categorical claims
description: Never assert "none X" or "all X" from a search until the search is confirmed exhaustive
type: feedback
---

Don't make categorical claims ("none of the repos implement X") until the search that produced the result is confirmed complete.

**Why:** Told mkoeppe "none of the 12 passagemath-pkg-* repos implement `_rich_repr_()`" in a public issue comment. An agent scraped the GitHub org page and got 12 repos (paginated, incomplete). `passagemath-pkg-slabbe` was missed. mkoeppe corrected us publicly.

**How to apply:**
- For org-wide code searches: use `gh search code "pattern" --owner org --limit 100` — not agent web scraping
- Before asserting "none" or "all": verify the search tool returned a complete result set (check total count, check for pagination)
- When uncertain: hedge ("of the repos I was able to find") or verify before posting
- This applies to any enumeration claim, not just GitHub searches
