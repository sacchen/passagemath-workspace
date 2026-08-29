# Judgment — decide without asking

"Use your best judgement" is 10% of every instruction typed across 17
projects, and "continue" is another 3%. Together they are the single most
repeated thing in the transcripts. They mean: keep going, decide, do not
stall. Usually with a rider, in the user's own words: "you can ask me if
there's some decision that changes things."

This file pre-answers those decisions so the loop does not have to ask.

## Proceed without asking

- **Which task to pick.** Furthest-along unfinished task first, per `pm-next`.
- **Whether a stage is done.** The gate decides, not a feeling.
- **Whether a candidate is worth scoping.** Apply the four-part bar in
  `scope.md`. Producing nothing is a valid outcome; say so and stop.
- **Which of two fixes to write.** Take the narrower one. Record the rejected
  alternative under `## Approach`; that is what the approach axis reviews.
- **Whether to cut a sentence.** Cut it. Deleting a claim is always safe;
  compressing one is not.
- **Whether an outside finding is worth acting on.** BLOCKER after
  verification, yes. NIT if the fix is smaller than the finding. PREFERENCE,
  no. Anything asking for more words, no.
- **Whether to fix a check that is wrong.** Fix it and say so in the report.
- **Whether to run a test, a build, or a repro.** Always run it. Never write
  "you could run" or "this should pass".
- **Whether to file a second problem found along the way.** New task file at
  `state: parked`. Never a ride-along commit.

## Ask, and stop until answered

- **Anything outward.** Push, PR, issue, comment, review reply. The loop ends
  at `state: ready` regardless of how confident the gate is.
- **A claim that cannot be verified locally.** Platform behavior on Linux or
  Windows, a maintainer's intent, whether an issue is a duplicate of one you
  cannot read. Say what you would need.
- **Scope that grows past the task's `files:` list** for a reason that looks
  legitimate. Widening scope silently is how a Perfect Commit stops being one.
- **A fix whose shape contradicts a recorded decision** in `kit/AGENTS.md` or
  the memory files. Those were paid for once already.
- **Anything on the dead-end list.** Unsolicited CI rewrites, upstream
  SageMath, PEP8 or docstring sweeps, work needing Windows.

## When blocked

Do every part that does not depend on the answer. Then state the question
with the options and a recommendation, and record it on the task as
`state: blocked` with the reason. Do not stall the whole task on one unknown.

## Reporting

Say what was done and what the gate said. Do not summarize a diff the user
can read. Do not ask "shall I continue" when this file already answers it.
