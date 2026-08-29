#!/usr/bin/env python3
"""End-to-end test for a passing contribution-pipeline gate."""

import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


CHECKS = Path(__file__).resolve().parent
GATE = CHECKS / "gate.sh"


class GateTest(unittest.TestCase):
    def git(self, repo, *args):
        return subprocess.run(
            ["git", *args], cwd=repo, check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout.strip()

    def test_complete_eight_axis_task_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            workspace = root / "workspace"
            queue = workspace / "kit/auto/queue"
            artifacts = workspace / "kit/auto/artifacts/editorial-fixture"
            repo.mkdir()
            queue.mkdir(parents=True)
            artifacts.mkdir(parents=True)

            self.git(repo, "init", "-b", "main")
            self.git(repo, "config", "user.name", "Pipeline Test")
            self.git(repo, "config", "user.email", "pipeline@example.invalid")
            self.git(repo, "config", "commit.gpgsign", "false")
            document = repo / "docs/example.rst"
            document.parent.mkdir(parents=True)
            document.write_text("Base documentation.\n", encoding="utf-8")
            self.git(repo, "add", "docs/example.rst")
            self.git(repo, "commit", "-m", "Base")
            self.git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
            self.git(repo, "switch", "-c", "fix/editorial-fixture")

            document.write_text(
                "Base documentation.\n\nThree.js renders the scene.\n",
                encoding="utf-8",
            )
            commit_message = textwrap.dedent("""\
                Document Three.js rendering

                Add the rendering note.

                Fixes #1
                """)
            self.git(repo, "add", "docs/example.rst")
            message_file = root / "commit.txt"
            message_file.write_text(commit_message, encoding="utf-8")
            self.git(repo, "commit", "-F", str(message_file))

            task = queue / "editorial-fixture.md"
            task.write_text(textwrap.dedent("""\
                ---
                slug: editorial-fixture
                state: redteamed
                issue: 1
                pr:
                branch: fix/editorial-fixture
                venv: .venv
                tier: beginner
                snt: tractable
                files:
                  - docs/example.rst
                doctest_cmd: true
                repro:
                repro_status: reproduced
                expected_failure: old documentation
                negative_control: fail-on-unpatched
                ---

                # Editorial fixture

                ## Evidence

                ## Red team

                - [x] relevance: documentation path checked
                - [x] scope: one declared file checked
                - [x] accuracy: public claims checked
                - [x] approach: narrower edit checked
                - [x] execution: effective diff checked
                - [x] source-style: checker clean and local block checked
                - [x] style: public drafts checked
                - [x] wording: scope checked
                """), encoding="utf-8")
            (artifacts / "commit.txt").write_text(
                commit_message, encoding="utf-8",
            )
            (artifacts / "pr-body.md").write_text(
                "Closes #1.\n\nDocument Three.js rendering.\n",
                encoding="utf-8",
            )

            env = os.environ.copy()
            env.update({
                "PM_REPO": str(repo),
                "PM_WORKSPACE": str(workspace),
                "PM_BASE": "origin/main",
                "PM_VENV": str(root / "unused-venv"),
            })
            result = subprocess.run(
                ["bash", str(GATE), str(task)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("GATE PASS  editorial-fixture is ready", result.stdout)


if __name__ == "__main__":
    unittest.main()
