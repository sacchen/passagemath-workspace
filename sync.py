# /// script
# dependencies = []
# ///
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# configuration
SRC = Path.home() / "foundry/sandbox/passagemath-obsidian/passagemath-public"
REPO = Path.home() / "foundry/sandbox/passagemath-workspace"
LOGS = REPO / "logs"


def run(*args, **kwargs):
    """streams output and ensures errors are visible."""
    kwargs.setdefault("check", True)
    return subprocess.run(args, **kwargs)


def sync(dry_run=False):
    if not SRC.exists() or not REPO.exists():
        sys.exit("fatal: missing paths. verify SRC and REPO.")

    os.chdir(REPO)

    # 1. sync remote with native autostash
    # handles dirty trees safely without manual index mutation
    print("pulling remote updates...")
    run("git", "pull", "origin", "main", "--rebase", "--autostash")

    # 2. mirror obsidian -> workspace logs/
    LOGS.mkdir(exist_ok=True)
    print(f"mirroring: {SRC} -> {LOGS}")

    rsync_cmd = [
        "rsync",
        "-av",
        "--delete",
        "--exclude",
        ".obsidian/",
        "--exclude",
        ".DS_Store",
    ]
    if dry_run:
        rsync_cmd.append("-n")
    rsync_cmd.extend([f"{SRC}/", f"{LOGS}/"])
    run(*rsync_cmd)

    if dry_run:
        print("\ndry run complete.")
        return

    # 3. isolate automation to logs/
    run("git", "add", "logs/")

    # 4. commit & push ONLY if logs/ changed in the index
    status = run(
        "git", "diff-index", "--cached", "--quiet", "HEAD", "--", "logs/", check=False
    )

    if status.returncode == 0:
        print("logs clean. nothing to push.")
        return

    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    run("git", "commit", "-m", f"log sync: {ts}")
    run("git", "push", "origin", "main")
    print(f"success: research stream pushed @ {ts}")


if __name__ == "__main__":
    sync(dry_run="--dry-run" in sys.argv)
