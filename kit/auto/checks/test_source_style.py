#!/usr/bin/env python3
"""Unit tests for the diff-scoped source editorial checker."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("source_style.py")
SPEC = importlib.util.spec_from_file_location("source_style", SCRIPT)
source_style = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = source_style
SPEC.loader.exec_module(source_style)


class SourceStyleTest(unittest.TestCase):
    def git(self, repo, *args):
        return subprocess.run(
            ["git", *args], cwd=repo, check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout.strip()

    def test_parse_added_lines_tracks_new_line_numbers(self):
        diff = """diff --git a/a.pyx b/a.pyx
--- a/a.pyx
+++ b/a.pyx
@@ -4,0 +5,2 @@
+first
+second
"""
        self.assertEqual(
            source_style.parse_added_lines(diff),
            [
                source_style.AddedLine("a.pyx", 5, "first"),
                source_style.AddedLine("a.pyx", 6, "second"),
            ],
        )

    def test_source_prose_rules(self):
        lines = [
            source_style.AddedLine("src/example.pyx", 10, "Load three.js."),
            source_style.AddedLine("src/example.pyx", 11, "``passagemath-plot`` ships it."),
            source_style.AddedLine("src/example.pyx", 12, "``Graphics3d`` objects render."),
        ]
        findings = source_style.check_lines(lines)
        self.assertEqual(
            [finding.code for finding in findings],
            ["product-case", "package-markup", "class-role"],
        )
        self.assertEqual(findings[0].severity, "ERROR")
        self.assertTrue(all(f.severity == "WARN" for f in findings[1:]))

    def test_tox_alignment_warning_uses_local_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            tox = repo / "pkgs/example/tox.ini"
            tox.parent.mkdir(parents=True)
            tox.write_text(
                "commands =\n"
                "    !notest:        python -c 'first'\n"
                "    # related command\n"
                "    python -c 'second'\n",
                encoding="utf-8",
            )
            line = source_style.AddedLine("pkgs/example/tox.ini", 4, "    python -c 'second'")
            findings = source_style.check_lines([line], repo)
            self.assertEqual([f.code for f in findings], ["config-alignment"])

    def test_product_case_ignores_code_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            source = repo / "src/example.py"
            source.parent.mkdir(parents=True)
            source.write_text('library_name = "three.js"\n', encoding="utf-8")
            line = source_style.AddedLine(
                "src/example.py", 1, 'library_name = "three.js"',
            )
            self.assertEqual(source_style.check_lines([line], repo), [])

    def test_effective_diff_uses_staged_and_unstaged_corrections(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.git(repo, "init", "-b", "main")
            self.git(repo, "config", "user.name", "Pipeline Test")
            self.git(repo, "config", "user.email", "pipeline@example.invalid")
            self.git(repo, "config", "commit.gpgsign", "false")
            source = repo / "src/example.py"
            source.parent.mkdir(parents=True)
            source.write_text('"""Base documentation."""\n', encoding="utf-8")
            self.git(repo, "add", "src/example.py")
            self.git(repo, "commit", "-m", "Base")
            self.git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
            self.git(repo, "switch", "-c", "fix/example")

            source.write_text('"""Load three.js."""\n', encoding="utf-8")
            self.git(repo, "add", "src/example.py")
            self.git(repo, "commit", "-m", "Add documentation")

            source.write_text('"""Load Three.js from the staged fix."""\n', encoding="utf-8")
            self.git(repo, "add", "src/example.py")
            staged = source_style.git_added_lines(
                repo, "origin/main", ["src/example.py"],
            )
            self.assertEqual(staged[0].text, '"""Load Three.js from the staged fix."""')

            source.write_text('"""Load Three.js from the working fix."""\n', encoding="utf-8")
            working = source_style.git_added_lines(
                repo, "origin/main", ["src/example.py"],
            )
            self.assertEqual(working[0].text, '"""Load Three.js from the working fix."""')
            self.assertEqual(source_style.check_lines(working, repo), [])


if __name__ == "__main__":
    unittest.main()
