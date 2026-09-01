#!/usr/bin/env python3
"""Tests for the red-team record check."""

from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


CHECK = Path(__file__).resolve().parent / "redteam_record.py"

REAL = textwrap.dedent("""\
    ## Red team

    - [x] relevance: pip install passagemath-plot with no passagemath-repl,
      evaluating sphere() in a cell, produces a static PNG and never the viewer.
    - [x] scope: git diff --name-only returns exactly the paths on files:, and
      git diff --stat -w matches, so no reformatting is riding along.
    - [x] accuracy: recounted the line totals; the drafts said 406 and measured
      430 to 440, corrected in commit.txt and pr-body.md.
    - [x] approach: the rejected alternative keeps the page inside
      _rich_repr_threejs() and unwraps html.get_str() at the call site.
    - [x] execution: negative_control.sh reports fail-on-unpatched, so the added
      doctest discriminates rather than decorating the change.
    - [x] source-style: source-style.sh raised two distribution-name warnings,
      both resolved against the local configuration block above them.
    - [x] style: rewrote pr-body.md after the first pass read as a pile of
      background the maintainer already has.
    - [x] wording: the title said "always" and now names the configuration in
      which the viewer is absent.
    """)


def run(text):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
        handle.write(text)
        path = handle.name
    try:
        return subprocess.run(
            [sys.executable, str(CHECK), path],
            check=False, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
    finally:
        Path(path).unlink()


class RedteamRecordTest(unittest.TestCase):
    def test_substantive_record_passes(self):
        result = run(REAL)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_boilerplate_is_rejected(self):
        for line in [
            "- [x] relevance: looks good",
            "- [x] relevance: n/a",
            "- [x] relevance: no issues found",
            "- [x] relevance: reviewed the diff and it all looks fine to me",
            "- [x] relevance: verified against the code, nothing to change here",
        ]:
            with self.subTest(line=line):
                text = REAL.replace(
                    "- [x] relevance: pip install passagemath-plot with no "
                    "passagemath-repl,\n  evaluating sphere() in a cell, "
                    "produces a static PNG and never the viewer.\n",
                    line + "\n",
                )
                result = run(text)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("FAIL  relevance", result.stdout)

    def test_empty_axis_is_rejected(self):
        result = run(REAL.replace("- [x] wording: the title said", "- [x] wording:\nx the title said"))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("FAIL  wording: empty", result.stdout)

    def test_unchecked_box_is_rejected(self):
        result = run(REAL.replace("- [x] scope:", "- [ ] scope:"))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("has not been worked", result.stdout)

    def test_missing_axis_is_rejected(self):
        result = run(REAL.replace("- [x] approach:", "- [x] aproach:"))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("no line on the task file", result.stdout)

    def test_axis_shaped_line_outside_the_section_does_not_count(self):
        stray = REAL + textwrap.dedent("""\
            ## Log

            - [x] scope: ok
            """)
        result = run(stray)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_continuation_lines_count_toward_the_record(self):
        wrapped = REAL.replace(
            "- [x] style: rewrote pr-body.md after the first pass read as a pile of\n"
            "  background the maintainer already has.\n",
            "- [x] style: rewrote pr-body.md\n"
            "  after the first pass read as a pile of background the maintainer\n"
            "  already has, then cut the second paragraph whole.\n",
        )
        result = run(wrapped)
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
