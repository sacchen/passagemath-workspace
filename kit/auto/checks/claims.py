#!/usr/bin/env python3
"""Accuracy gate: no categorical or numeric claim ships without evidence.

Every sentence in the draft that makes a countable or categorical claim must
be covered by a `claim:` line in the task file's `## Evidence` section. This
is the mechanical form of the rule in
kit/claude-memories/feedback_categorical_claims.md: the public correction on
"none of the 12 passagemath-pkg-* repos implement _rich_repr_()" happened
because a claim shipped ahead of an exhaustive search.

Usage:  claims.py --task kit/auto/queue/SLUG.md DRAFT...
        claims.py --list DRAFT...        # just show what would need evidence

Evidence section format:

    ## Evidence

    - claim: 117 tests pass
      check: `sage -t --optional=sage ...` -> 117 passed, exit 0
"""
import argparse
import re
import sys

CATEGORICAL = [
    "none", "no other", "nothing", "all", "every", "always", "never",
    "only", "any ", "exhaustive", "entire", "fully", "completely",
    "the first", "unique", "no remaining", "each of", "in all",
    "everywhere", "universally", "guaranteed",
]

COUNT = re.compile(
    r"\b\d[\d,]*\s+(tests?|files?|failures?|packages?|repos(?:itories)?|hits?|"
    r"cases?|methods?|lines?|functions?|modules?|instances?|occurrences?|"
    r"callers?|doctests?|commits?|prs?|issues?)\b",
    re.I,
)

RESULT = re.compile(
    r"\b(passes|passed|fails|failed|exit code|exits? \d|no regressions?|"
    r"green|clean run|reproduces|verified)\b",
    re.I,
)

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n")


def strip_code(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"^(    |\t).*$", " ", text, flags=re.M)
    return re.sub(r"`[^`]*`", " ", text)


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def flagged_sentences(text):
    out = []
    for raw in SENT_SPLIT.split(strip_code(text)):
        s = raw.strip()
        if len(s) < 8:
            continue
        reasons = []
        low = " " + norm(s) + " "
        for w in CATEGORICAL:
            if re.search(r"\b" + re.escape(w).replace(r"\ ", r"\s+"), low):
                reasons.append(f"categorical {w.strip()!r}")
        if COUNT.search(s):
            reasons.append("count")
        if RESULT.search(s):
            reasons.append("test result")
        if reasons:
            out.append((s, sorted(set(reasons))))
    return out


def evidence_claims(task_path):
    with open(task_path, encoding="utf-8") as fh:
        body = fh.read()
    m = re.search(r"^##\s+Evidence\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S)
    if not m:
        return None
    claims = []
    for line in m.group(1).splitlines():
        cm = re.match(r"\s*-\s*claim:\s*(.+?)\s*$", line)
        if cm and cm.group(1) not in ("<substring that appears in the prose>",):
            claims.append(norm(cm.group(1)))
    return claims


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("drafts", nargs="+")
    ap.add_argument("--task")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if not args.list and not args.task:
        ap.error("--task is required unless --list is given")

    claims = None
    if args.task:
        claims = evidence_claims(args.task)
        if claims is None:
            print(f"ERROR  {args.task}: no '## Evidence' section")
            return 1

    uncovered_total = 0
    for path in args.drafts:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        flags = flagged_sentences(text)
        uncovered = []
        for sent, reasons in flags:
            if args.list:
                print(f"CLAIM  {path}  ({', '.join(reasons)})  {sent}")
                continue
            if any(c and c in norm(sent) for c in claims):
                continue
            uncovered.append((sent, reasons))
        for sent, reasons in uncovered:
            print(f"ERROR  {path}  [unevidenced: {', '.join(reasons)}]  {sent}")
        if not args.list:
            print(f"---- {path}: {len(flags)} claim(s), {len(uncovered)} unevidenced")
        uncovered_total += len(uncovered)

    return 1 if uncovered_total else 0


if __name__ == "__main__":
    sys.exit(main())
