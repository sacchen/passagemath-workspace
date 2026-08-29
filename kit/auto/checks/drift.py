#!/usr/bin/env python3
"""Catch the accuracy damage that shortening does.

The pattern this exists for, from a real session: a PR body was cut down
twice for length, and the external review came back with "the shortening
reintroduced several accuracy problems" -- "viewer dispatch" had become too
broad, "will not be installed" had become unnecessarily absolute, "so it
works" had lost its antecedent. Each revision was shorter and each was less
true.

Cutting words is safe. Cutting *qualifiers* is not. A claim may be deleted
whole, but a claim that survives must not get broader than its evidence.

Usage:  drift.py OLD NEW
        drift.py --save DIR FILE     # snapshot a revision before editing

Exit 1 when a surviving sentence broadened.
"""
import argparse
import difflib
import os
import re
import shutil
import sys
import time

ABSOLUTE = [
    "all", "every", "always", "never", "any", "none", "no other", "nothing",
    "cannot", "can't", "will not", "won't", "must", "entire", "fully",
    "completely", "everywhere", "universally", "guaranteed", "impossible",
    "unaffected", "identical", "only",
]

# Clauses that scope a claim. Losing one makes the claim bigger.
QUALIFIER = [
    r"\bwhen\b", r"\bif\b", r"\bunless\b", r"\bwhile\b", r"\bunder\b",
    r"\bwith(out)?\b", r"\bfor\b", r"\bin (a|an|the) [a-z-]+ (install|environment|venv|config|kernel|build)",
    r"\bon (macos|linux|windows|python \d)", r"\bexcept\b", r"\bapart from\b",
    r"\bat least\b", r"\bup to\b", r"\bso far\b", r"\bobserved\b", r"\btested\b",
]

SENT = re.compile(r"(?<=[.!?])\s+")


def strip_code(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"^(    |\t).*$", " ", text, flags=re.M)
    return text


def sentences(text):
    out = []
    for para in strip_code(text).split("\n\n"):
        flat = re.sub(r"\s+", " ", para).strip()
        if not flat:
            continue
        for s in SENT.split(flat):
            s = s.strip()
            if len(s) > 12:
                out.append(s)
    return out


def bare(s):
    """Sentence with inline code spans removed, for wording comparisons."""
    return re.sub(r"`[^`]*`", " CODE ", s)


def has(patterns, s, word_list=False):
    found = []
    for p in patterns:
        pat = r"\b" + re.escape(p) + r"\b" if word_list else p
        if re.search(pat, s, re.I):
            found.append(p)
    return found


def idents(s):
    return set(re.findall(r"`[^`]+`", s)) | set(re.findall(r"\b\d[\d,.]*\b", s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new", nargs="?")
    ap.add_argument("--save", metavar="DIR")
    args = ap.parse_args()

    if args.save:
        os.makedirs(args.save, exist_ok=True)
        base = os.path.basename(args.old)
        dest = os.path.join(args.save, f"{base}.{time.strftime('%Y%m%dT%H%M%S')}")
        shutil.copy2(args.old, dest)
        print(f"saved {dest}")
        return 0

    if not args.new:
        ap.error("NEW is required unless --save is given")

    old = sentences(open(args.old, encoding="utf-8").read())
    new = sentences(open(args.new, encoding="utf-8").read())
    old_set = set(old)

    findings = 0
    kept = dropped = 0

    for s in new:
        if s in old_set:
            kept += 1
            continue
        match = difflib.get_close_matches(s, old, n=1, cutoff=0.45)
        if not match:
            print(f"NEW    unmatched sentence, verify it against the evidence ledger:\n       {s}")
            findings += 1
            continue
        o = match[0]
        problems = []

        gained = set(has(ABSOLUTE, bare(s), True)) - set(has(ABSOLUTE, bare(o), True))
        if gained:
            problems.append(f"gained absolute {sorted(gained)}")

        lost_q = set(has(QUALIFIER, bare(o))) - set(has(QUALIFIER, bare(s)))
        if lost_q:
            problems.append(f"lost qualifier {sorted(x.replace(chr(92)+'b','') for x in lost_q)}")

        lost_id = idents(o) - idents(s)
        if lost_id:
            problems.append(f"lost specifics {sorted(lost_id)}")

        if problems:
            print(f"BROADENED  {'; '.join(problems)}")
            print(f"       was: {o}")
            print(f"       now: {s}")
            findings += 1
        kept += 1

    for o in old:
        if o not in set(new) and not difflib.get_close_matches(o, new, n=1, cutoff=0.45):
            dropped += 1

    print(f"---- {kept} sentence(s) carried over, {dropped} dropped whole, "
          f"{findings} need re-verification")
    if findings:
        print("     A dropped claim is fine. A surviving claim that got broader is not.")
        print("     Re-check each against the task's ## Evidence section, or put the")
        print("     qualifier back.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
