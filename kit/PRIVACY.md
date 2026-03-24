# Privacy guidelines for kit/

This repo is public and mkoeppe forks and reads it. Treat everything in `kit/` as potentially visible to the passagemath maintainer team.

## Before pushing

**Strip or anonymize:**
- Local absolute paths (use `~/...` or omit entirely)
- Local usernames embedded in paths
- Real first names attached to GitHub handles unless the person has made that connection public themselves

**Reconsider before publishing:**
- AI assistant memory files (`claude-memories/`) — written for a private context; review each file before pushing. Psychological/strategic self-profiles are not for public consumption even if the content is benign.
- Notes that characterize a specific person's behavior, reading habits, or motivations — even if flattering
- Course enrollment specifics (credits, hours/week, start dates) — low risk but unnecessary

**Fine to publish:**
- GitHub handles and public PR/issue numbers — already public
- Public figures' full names (e.g. mkoeppe) — already public
- Technical workflow notes, feedback on past mistakes, architectural decisions
- Candid accounts of public errors (e.g. a wrong comment on a GitHub issue) — good epistemic modeling

## claude-memories/ specifically

These files are exported from Claude Code's persistent memory. Before each push:
1. Grep for `/Users/` — should be zero hits
2. Check for real names paired with pseudonymous handles
3. Review `user_profile.md` — most likely to contain private framing; keep it to public-facing contributor context only
