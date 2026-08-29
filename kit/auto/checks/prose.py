#!/usr/bin/env python3
"""Style and wording gate for commits, PR bodies, and issues.

Encodes ~/.claude/commit-pr-style.md as checks. Code blocks are exempt.

Usage:  prose.py [--commit] FILE...
        --commit  also check the summary line (<=72 chars, imperative, blank line 2)

Exit 0 when no ERROR fires. WARN never fails the gate; it is for the
red-team read, where a human or agent decides case by case.
"""
import argparse
import re
import sys

AI_SPEak = [
    "comprehensive", "robust", "seamless", "seamlessly", "significantly",
    "leverage", "leverages", "delve", "crucial", "streamline", "streamlined",
    "elegant", "powerful", "effortless", "cutting-edge", "best-in-class",
    "holistic", "underscore", "underscores", "pivotal", "myriad",
    "it is important to note", "it's important to note", "it is worth noting",
    "it's worth noting", "in today's", "dive into", "unlock", "empower",
    "elevate", "game-changer", "meticulous", "meticulously", "intricate",
]

FILLER = [
    "simply", "just", "very", "really", "basically", "essentially",
    "actually", "quite", "fairly", "somewhat", "in order to", "note that",
    "please note", "as we can see", "obviously", "clearly", "of course",
]

PRONOUNS = ["we", "us", "our", "ours", "my", "mine", "me", "i'm", "i've", "we've", "we'll"]

VAGUE_TIMING = [
    "always", "never", "immediately", "instantly", "every time",
    "in all cases", "guaranteed",
]


# Signposting: sentences that narrate the document instead of stating a fact.
# Every one of these was cut by hand in a past session. Sources, in order:
# "two things not to undo", "worth knowing if you edit this later",
# "there is a bug in the way first", "the first commit fixes a separate bug
# that gets in the way", "two choices in there are intentional",
# "it needs the same treatment as this PR first".
SIGNPOST = [
    r"worth (knowing|noting|mentioning|calling out)",
    r"\b(two|three|four) (things|choices|points|notes|caveats)\b",
    r"\bnot to undo\b",
    r"\bgets? in the way\b",
    r"\b(is|are|was|were) intentional\b",
    r"\bon purpose\b",
    r"\bkeep in mind\b",
    r"\bas (mentioned|noted|described|discussed) (above|below|earlier)\b",
    r"\bsee (below|above)\b",
    r"\bthis (section|document|writeup|write-up|paragraph|PR body|commit message)\b",
    r"\bfirst,.*\bsecond,",
    r"\btl;?dr\b",
    r"\bin summary\b",
    r"\bto summarize\b",
    r"\bthe following\b",
    r"\bbefore (we|you) (get|dive|move)",
    r"\bneeds the same treatment\b",
]

# Bare demonstratives and pronouns with no noun to attach to. Codex flagged
# "so it works" for an ambiguous antecedent; the fix is to name the thing.
ANTECEDENT = [
    r"^(This|That|These|Those|It)\s+(is|are|was|were|means|makes|lets|allows|gives|keeps|breaks|fixes|works|happens|causes)\b",
    r"\bso it works\b",
    r"\bthat part\b",
    r"\bthe (thing|piece|bit|step) (that|which)\b",
]

# Structural budgets. From the sessions: "one short paragraph for commit and
# three short paragraphs for PR body", "max 5 short paragraphs" for an issue,
# "short paragraphs instead of with headings".
BUDGET = {
    "commit":  dict(paras=3, sentences=4, headings=0, code=1, bullets=True),
    "pr":      dict(paras=4, sentences=4, headings=0, code=1, bullets=True),
    "issue":   dict(paras=5, sentences=4, headings=0, code=1, bullets=True),
    "comment": dict(paras=2, sentences=3, headings=0, code=1, bullets=True),
}

FOOTER = re.compile(r"(generated with|\N{ROBOT FACE}|claude code|ai-generated)", re.I)
COAUTHOR = re.compile(r"^co-authored-by:", re.I)

# Trailers and the opening reference are not body paragraphs.
TRAILER = re.compile(
    r"^\s*((Fixes|Closes|Refs?|See|Signed-off-by|Co-Authored-By|Reviewed-by)[:# ])", re.I
)

# "Call out diff mechanics that would otherwise mislead review" is allowed on
# top of the three paragraphs, so it does not count against the budget.
CALLOUT = re.compile(r"^\s*(Diff mechanics|Review note|Note for review)\b", re.I)


def strip_code(lines):
    """Yield (lineno, text, is_code) with fenced and indented blocks marked."""
    fence = None
    for i, raw in enumerate(lines, 1):
        text = raw.rstrip("\n")
        m = re.match(r"^\s*(```+|~~~+)", text)
        if m:
            tok = m.group(1)[:3]
            if fence is None:
                fence = tok
                yield i, text, True
                continue
            if tok == fence:
                fence = None
                yield i, text, True
                continue
        if fence is not None:
            yield i, text, True
        elif re.match(r"^(    |\t)\S", text):
            yield i, text, True
        else:
            yield i, text, False


def mask_inline_code(text):
    return re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), text)


def word_hits(text, words):
    hits = []
    for w in words:
        pat = r"\b" + re.escape(w).replace(r"\ ", r"\s+") + r"\b"
        if re.search(pat, text, re.I):
            hits.append(w)
    return hits


def check(path, commit_mode, kind=None):
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()

    findings = []

    def err(ln, code, msg):
        findings.append(("ERROR", ln, code, msg))

    def warn(ln, code, msg):
        findings.append(("WARN", ln, code, msg))

    rows = list(strip_code(lines))
    prose = [(ln, mask_inline_code(t)) for ln, t, code in rows if not code]

    for ln, text in prose:
        if not text.strip():
            continue

        if re.search(r"\w\s*[—–]\s*\w|\w[—–]\w", text):
            err(ln, "em-dash", "em/en dash; rewrite as two sentences or a comma")

        if re.search(r"\bI\b", text):
            err(ln, "pronoun", "personal pronoun 'I'")
        for w in word_hits(text, PRONOUNS):
            err(ln, "pronoun", f"personal pronoun {w!r}")

        for w in word_hits(text, AI_SPEak):
            err(ln, "ai-speak", f"AI speak {w!r}")

        for w in word_hits(text, FILLER):
            warn(ln, "filler", f"filler {w!r} adds no checkable content")

        for w in word_hits(text, VAGUE_TIMING):
            warn(ln, "overstated", f"{w!r} overstates timing or scope; is it literally true?")

        for pat in SIGNPOST:
            if re.search(pat, text, re.I):
                err(ln, "signpost", "signposting; state the fact and drop the narration")
                break

        for pat in ANTECEDENT:
            if re.search(pat, text.strip()):
                warn(ln, "antecedent", "bare demonstrative or pronoun; name the function, field, or file")
                break

        if re.search(r"\bMatthias\b", text):
            err(ln, "public-name", "use 'mkoeppe', not a first name, in public content")

        if FOOTER.search(text):
            err(ln, "footer", "no generated-by or banner footers")

        if COAUTHOR.match(text.strip()):
            if commit_mode:
                warn(ln, "coauthor", "Co-Authored-By is a case-by-case call, not automatic")
            else:
                err(ln, "footer", "no trailers in a PR body or issue")

        if "\\`" in lines[ln - 1]:
            err(ln, "escaped-backtick", "escaped backtick; pass bodies with --body-file, never --body")

        if re.search(r"[ \t]+$", lines[ln - 1].rstrip("\n")):
            err(ln, "trailing-ws", "trailing whitespace")

    # GitHub renders a single newline as <br>. A prose line that stops short
    # of the margin with prose following it is a hard wrap. Commit messages
    # are exempt: git convention wraps them at 72 and git renders them in a
    # <pre> block, so the canonical commit 73e8519f77 is wrapped on purpose.
    for idx, (ln, text) in enumerate([] if commit_mode else prose[:-1]):
        nxt_ln, nxt = prose[idx + 1]
        if nxt_ln != ln + 1:
            continue
        if not text.strip() or not nxt.strip():
            continue
        if re.match(r"^\s*([-*+]|\d+\.|>|#)", text) or re.match(r"^\s*([-*+]|\d+\.|>|#)", nxt):
            continue
        if len(text.rstrip()) < 72 and not text.rstrip().endswith(("|", ":")):
            err(ln, "hard-wrap", "hard-wrapped paragraph; GitHub renders this as <br>")

    if commit_mode and lines:
        subject = lines[0].rstrip("\n")
        if len(subject) > 72:
            err(1, "subject-length", f"summary line is {len(subject)} chars, limit 72")
        if len(lines) > 1 and lines[1].strip():
            err(2, "subject-blank", "line 2 of a commit message must be blank")
        if re.match(r"^(Added|Fixed|Updated|Changed|Removed|Adds|Fixes|Updates)\b", subject):
            warn(1, "imperative", "summary line should be imperative: 'Fix', not 'Fixed'/'Fixes'")
        body = "".join(lines[1:])
        if re.search(r"\b(Fixes|Closes) #\d+", body):
            pass
        elif re.search(r"^Refs?:", body, re.M):
            warn(1, "issue-link",
                 "Refs: rather than 'Fixes #N'. Correct when the issue is a meta-issue "
                 "this change does not close; wrong if it does close one")
        else:
            err(1, "issue-link", "commit body needs 'Fixes #NNNN', or 'Refs:' for a meta-issue")


    if kind:
        b = BUDGET[kind]
        body_rows = rows[2:] if kind == "commit" else rows
        paras, cur, fences = [], [], 0
        in_callout = False
        for ln, text, is_code in body_rows:
            if not text.strip():
                in_callout = False
            if re.match(r"^\s*(```+|~~~+)", text):
                fences += 1
            if is_code:
                continue
            if text.strip():
                if TRAILER.match(text) and len(text.strip()) < 90:
                    continue
                if CALLOUT.match(text):
                    in_callout = True
                if in_callout:
                    continue
                cur.append((ln, text))
            elif cur:
                paras.append(cur); cur = []
        if cur:
            paras.append(cur)

        if len(paras) > b["paras"]:
            err(paras[b["paras"]][0][0], "budget-paras",
                f"{len(paras)} paragraphs; a {kind} gets at most {b['paras']}. "
                f"Cut a whole claim, do not compress the survivors")
        for para in paras:
            first_ln = para[0][0]
            joined = " ".join(t for _, t in para)
            if re.match(r"^\s*#{1,6}\s", joined):
                err(first_ln, "budget-heading", "no headings; use short paragraphs")
            if re.match(r"^\s*([-*+]|\d+\.)\s", para[0][1]) and b["bullets"]:
                warn(first_ln, "budget-bullets", "a bullet list in prose usually means the paragraph was not written")
            n = len([x for x in re.split(r"(?<=[.!?])\s+", joined) if len(x.strip()) > 3])
            if n > b["sentences"]:
                warn(first_ln, "budget-sentences",
                     f"{n} sentences in one paragraph; aim for {b['sentences']} or fewer")
        if fences // 2 > b["code"]:
            err(1, "budget-code", f"{fences // 2} code blocks; a {kind} gets at most {b['code']}")

    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--kind", choices=sorted(BUDGET),
                    help="apply the structural budget for this document kind")
    args = ap.parse_args()

    failed = False
    for path in args.files:
        kind = args.kind or ("commit" if args.commit else None)
        findings = check(path, args.commit or kind == "commit", kind)
        errors = [f for f in findings if f[0] == "ERROR"]
        for sev, ln, code, msg in findings:
            print(f"{sev}  {path}:{ln}  [{code}] {msg}")
        if errors:
            failed = True
        print(f"---- {path}: {len(errors)} error(s), "
              f"{len(findings) - len(errors)} warning(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
