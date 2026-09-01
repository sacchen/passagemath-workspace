#!/usr/bin/env python3
"""Tests for path resolution in env.sh.

The pipeline is unusable if these are wrong: every check sources env.sh, so a
bad default is not one broken check but seven.
"""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ENV = Path(__file__).resolve().parent / "env.sh"


def resolve(cwd, env=None, script=ENV):
    """Source a copy of env.sh and report what it resolved."""
    result = subprocess.run(
        ["bash", "-c", f'. "{script}"; echo "$WORKSPACE"; echo "$REPO"'],
        cwd=cwd, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
    )
    workspace, repo = result.stdout.strip().splitlines()
    return workspace, repo


class EnvTest(unittest.TestCase):
    def checkout(self, root, name="passagemath-workspace"):
        """Lay out a workspace the way a real clone is laid out."""
        checks = root / name / "kit/auto/checks"
        checks.mkdir(parents=True)
        shutil.copy(ENV, checks / "env.sh")
        return checks / "env.sh"

    def test_workspace_derives_from_the_env_file_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            script = self.checkout(root)
            workspace, _ = resolve(tmp, script=script)
            self.assertEqual(workspace, str(root / "passagemath-workspace"))

    def test_workspace_is_independent_of_the_working_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            script = self.checkout(root)
            elsewhere = root / "elsewhere"
            elsewhere.mkdir()
            self.assertEqual(
                resolve(root, script=script)[0],
                resolve(elsewhere, script=script)[0],
            )

    def test_repo_prefers_a_clone_that_actually_holds_src_sage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            script = self.checkout(root)
            (root / "passagemath/src/sage").mkdir(parents=True)
            _, repo = resolve(tmp, script=script)
            self.assertEqual(repo, str(root / "passagemath"))

    def test_pm_overrides_win(self):
        import os
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            script = self.checkout(root)
            env = os.environ.copy()
            env.update({
                "PM_WORKSPACE": "/somewhere/else",
                "PM_REPO": "/somewhere/else/repo",
            })
            workspace, repo = resolve(tmp, env=env, script=script)
            self.assertEqual(workspace, "/somewhere/else")
            self.assertEqual(repo, "/somewhere/else/repo")


if __name__ == "__main__":
    unittest.main()
