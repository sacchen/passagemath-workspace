#!/usr/bin/env python3
"""Check that the eight red-team axes are recorded with substance.

    redteam_record.py kit/auto/queue/SLUG.md

The gate used to accept any line matching `- [x] <axis>:`, which made the
record itself the definition of the work: eight lines reading "checked" pass a
grep. This check reads what each axis line actually says.

It cannot tell whether the attack happened. It can only tell whether the line
is a record of one, so a line that survives this is still only as good as the
pass behind it. See playbooks/redteam.md, which is where the work is defined.
"""

import argparse
import pathlib
import re
import sys

AXES = [
    "relevance", "scope", "accuracy", "approach",
    "execution", "source-style", "style", "wording",
]

# Calibrated against the axis records already in the queue, whose thinnest
# honest line is 55 chars, 8 words, 5 substantive. That leaves no margin on
# words: a real but terser record would fail here and have to be rewritten.
# Erring tight is the deliberate choice, because the failure this check exists
# for is an axis that was never worked, not one described too briefly.
MIN_CHARS = 40
MIN_WORDS = 8
MIN_SUBSTANTIVE = 4

# Words that say a pass happened without saying what it found. A line built
# only out of these is a checkbox, not a record.
FILLER = {
    "a", "all", "an", "and", "any", "anything", "appears", "applicable", "are",
    "as", "at", "axis", "been", "both", "but", "by", "check", "checked",
    "checks", "clean", "confirmed", "correct", "did", "do", "does", "done",
    "everything", "expected", "few", "fine", "for", "found", "from", "good",
    "great", "had", "has", "have", "here", "in", "is", "issue", "issues", "it",
    "its", "just", "lgtm", "look", "looked", "looks", "me", "my", "n/a", "na",
    "needed", "nil", "no", "none", "not", "nothing", "of", "ok", "okay", "on",
    "or", "pass", "passed", "passes", "passing", "problem", "problems", "ran",
    "review", "reviewed", "reviews", "right", "seems", "solid", "sound",
    "still", "survives", "that", "the", "them", "there", "these", "this",
    "to", "unchanged", "verified", "verify", "was", "were", "with", "yes",
}

AXIS_RE = re.compile(
    r"^\s*-?\s*\[(?P<box>[ xX])\]\s*(?P<axis>[a-z-]+)\s*:(?P<rest>.*)$"
)
WORD_RE = re.compile(r"[A-Za-z0-9_#./`()-]+")


def blocks(path):
    """Map each axis to (checked, text), joining indented continuation lines.

    Only the `## Red team` section counts, when the file has one. Scanning the
    whole file would let a later axis-shaped line anywhere on the task, in the
    log or under Evidence, silently replace the real record.
    """
    text = pathlib.Path(path).read_text(encoding="utf-8")
    heading = re.search(r"^##+\s+Red team\s*$", text, re.MULTILINE | re.IGNORECASE)
    if heading:
        text = text[heading.end():]
        stop = re.search(r"^##+\s+", text, re.MULTILINE)
        if stop:
            text = text[:stop.start()]

    out = {}
    current = None
    for line in text.splitlines():
        match = AXIS_RE.match(line)
        if match:
            axis = match.group("axis").lower()
            current = axis if axis in AXES else None
            if current:
                out[current] = [
                    match.group("box").lower() == "x",
                    match.group("rest").strip(),
                ]
            continue
        if current is None:
            continue
        if line.strip() and line[:1].isspace():
            out[current][1] = (out[current][1] + " " + line.strip()).strip()
        else:
            current = None
    return {k: tuple(v) for k, v in out.items()}


def judge(text):
    """Return a failure reason, or None if the text reads as a real record."""
    text = " ".join(text.split())
    if not text:
        return "empty"
    words = WORD_RE.findall(text)
    substantive = [w for w in words if w.lower().strip(".,;:") not in FILLER]
    if len(text) < MIN_CHARS or len(words) < MIN_WORDS:
        return (
            f"too short to be a record ({len(text)} chars, {len(words)} words; "
            f"need {MIN_CHARS} and {MIN_WORDS}): {text!r}"
        )
    if len(substantive) < MIN_SUBSTANTIVE:
        return (
            f"says a pass happened but not what it found ({len(substantive)} "
            f"substantive words): {text!r}"
        )
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task")
    args = parser.parse_args()

    recorded = blocks(args.task)
    rc = 0
    for axis in AXES:
        entry = recorded.get(axis)
        if entry is None:
            print(f"FAIL  {axis}: no line on the task file")
            rc = 1
            continue
        checked, text = entry
        if not checked:
            print(f"FAIL  {axis}: still '[ ]', the axis has not been worked")
            rc = 1
            continue
        reason = judge(text)
        if reason:
            print(f"FAIL  {axis}: {reason}")
            rc = 1
        else:
            print(f"ok    {axis}")

    if rc:
        print()
        print("      Each axis needs what was attacked, what survived, and what")
        print("      changed. See playbooks/redteam.md; the line is the receipt,")
        print("      not the work. Padding it to pass this check is the same bug.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
