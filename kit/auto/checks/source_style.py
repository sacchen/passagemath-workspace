#!/usr/bin/env python3
"""Review added source lines for maintainer-facing editorial conventions.

The check is diff-scoped: it never reports pre-existing text. Deterministic
terminology errors fail; contextual markup and alignment questions warn and
must be resolved in the task's ``source-style`` red-team entry.

Usage: source_style.py TASK [--repo REPO] [--base REV]
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import io
from pathlib import Path
import re
import subprocess
import sys
import tokenize


DOC_SUFFIXES = {".py", ".pyx", ".pxd", ".rst"}
PACKAGE_LITERAL = re.compile(r"``(passagemath-[a-z0-9_.-]+(?:\[[^`]+\])?)``")
CLASS_LITERAL = re.compile(r"``([A-Z][A-Za-z0-9_]*)``\s+(objects?|instances?)\b")
LOWER_THREEJS = re.compile(r"(?<![A-Za-z])three\.js\b")
FACTOR_COMMAND = re.compile(r"^ {4}[^#\s][^:]*:\s{2,}\S")
PLAIN_COMMAND = re.compile(r"^ {4}(?![#\s!{])\S")
TRIPLE_STRING = re.compile(r"(?is)^[rubf]*(?:'''|\"\"\")")


@dataclass(frozen=True)
class AddedLine:
    path: str
    number: int
    text: str


@dataclass(frozen=True)
class Finding:
    severity: str
    path: str
    number: int
    code: str
    message: str


def task_files(path: Path) -> list[str]:
    """Return the ``files`` frontmatter sequence from a task file."""
    lines = path.read_text(encoding="utf-8").splitlines()
    in_frontmatter = False
    in_files = False
    result = []
    for line in lines:
        if line == "---":
            if in_frontmatter:
                break
            in_frontmatter = True
            continue
        if not in_frontmatter:
            continue
        if line.startswith("files:"):
            in_files = True
            continue
        if in_files and re.match(r"^[A-Za-z_][A-Za-z0-9_]*:", line):
            break
        if in_files:
            match = re.match(r"^\s+-\s+(.+?)\s*$", line)
            if match:
                result.append(match.group(1))
    return result


def parse_added_lines(diff: str) -> list[AddedLine]:
    """Parse added lines and their new-file line numbers from a git diff."""
    path = None
    new_line = None
    result = []
    for raw in diff.splitlines():
        if raw.startswith("+++ b/"):
            path = raw[6:]
            continue
        if raw.startswith("@@ "):
            match = re.search(r"\+(\d+)(?:,(\d+))?", raw)
            new_line = int(match.group(1)) if match else None
            continue
        if path is None or new_line is None:
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            result.append(AddedLine(path, new_line, raw[1:]))
            new_line += 1
        elif raw.startswith(" "):
            new_line += 1
        elif raw.startswith("-"):
            continue
    return result


def git_added_lines(repo: Path, base: str, files: list[str]) -> list[AddedLine]:
    """Collect effective added lines, including staged and unstaged fixes."""
    command = [
        "git", "diff", "--unified=0", "--no-color", base, "--", *files,
    ]
    proc = subprocess.run(
        command,
        cwd=repo,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip() or "git diff failed")
    return parse_added_lines(proc.stdout)


def nearby_factor_command(repo: Path, line: AddedLine) -> bool:
    """Whether a four-space tox command follows a nearby factored command."""
    if Path(line.path).name != "tox.ini" or not PLAIN_COMMAND.match(line.text):
        return False
    full_path = repo / line.path
    if not full_path.exists():
        return False
    rows = full_path.read_text(encoding="utf-8").splitlines()
    start = max(0, line.number - 13)
    return any(FACTOR_COMMAND.match(row) for row in rows[start : line.number - 1])


def source_prose_lines(repo: Path, path: str) -> set[int] | None:
    """Return prose line numbers, or ``None`` when the whole file is prose."""
    suffix = Path(path).suffix
    if suffix == ".rst":
        return None
    full_path = repo / path
    if not full_path.exists():
        return set()
    source = full_path.read_text(encoding="utf-8")
    result = set()
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for token in tokens:
            if token.type == tokenize.COMMENT:
                result.add(token.start[0])
            elif token.type == tokenize.STRING and TRIPLE_STRING.match(token.string):
                result.update(range(token.start[0], token.end[0] + 1))
    except (IndentationError, tokenize.TokenError):
        # A Cython construct unknown to Python's tokenizer must not silently
        # disable review. Falling back to all lines trades noise for coverage.
        return set(range(1, len(source.splitlines()) + 1))
    return result


def check_lines(lines: list[AddedLine], repo: Path | None = None) -> list[Finding]:
    """Return findings for added source lines."""
    findings = []
    prose_cache: dict[str, set[int] | None] = {}
    for line in lines:
        suffix = Path(line.path).suffix
        is_prose = suffix in DOC_SUFFIXES
        if is_prose and repo is not None:
            if line.path not in prose_cache:
                prose_cache[line.path] = source_prose_lines(repo, line.path)
            prose_lines = prose_cache[line.path]
            is_prose = prose_lines is None or line.number in prose_lines
        if is_prose:
            if LOWER_THREEJS.search(line.text):
                findings.append(Finding(
                    "ERROR", line.path, line.number, "product-case",
                    "use the project spelling 'Three.js' in source prose",
                ))
            package = PACKAGE_LITERAL.search(line.text)
            if package:
                findings.append(Finding(
                    "WARN", line.path, line.number, "package-markup",
                    f"{package.group(1)!r} is double-backticked; use prose "
                    "emphasis for a distribution name unless this is literal "
                    "requirement syntax",
                ))
            class_name = CLASS_LITERAL.search(line.text)
            if class_name:
                findings.append(Finding(
                    "WARN", line.path, line.number, "class-role",
                    f"{class_name.group(1)!r} names a class; consider a :class: Sphinx role",
                ))
        if repo is not None and nearby_factor_command(repo, line):
            findings.append(Finding(
                "WARN", line.path, line.number, "config-alignment",
                "unconditional tox command follows a factored command; compare "
                "the executable-column alignment of the local block",
            ))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task", type=Path)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--base", default="origin/main")
    args = parser.parse_args()

    files = task_files(args.task)
    if not files:
        print(f"ERROR  {args.task}:0  [task-files] task declares no files", file=sys.stderr)
        return 2
    try:
        lines = git_added_lines(args.repo, args.base, files)
    except RuntimeError as error:
        print(f"ERROR  [git-diff] {error}", file=sys.stderr)
        return 2

    findings = check_lines(lines, args.repo)
    for finding in findings:
        print(
            f"{finding.severity}  {finding.path}:{finding.number}  "
            f"[{finding.code}] {finding.message}"
        )
    errors = sum(finding.severity == "ERROR" for finding in findings)
    warnings = len(findings) - errors
    print(f"---- source diff: {errors} error(s), {warnings} warning(s)")
    if warnings:
        print("     resolve each warning in the task's source-style red-team entry")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
