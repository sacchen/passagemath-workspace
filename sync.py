# /// script
# dependencies = ["sh"]
# ///
import sh
import os
import sys
from datetime import datetime

# configuration
# using absolute paths to avoid any shell ambiguity
OBSIDIAN_SRC = os.path.expanduser(
    "~/foundry/sandbox/passagemath-obsidian/passagemath-public"
)
REPO_ROOT = os.path.expanduser("~/foundry/sandbox/passagemath-workspace")
LOG_DEST = os.path.join(REPO_ROOT, "logs")


def sync():
    # 1. source validation
    if not os.path.exists(OBSIDIAN_SRC):
        print(f"error: source {OBSIDIAN_SRC} not found. is the obsidian folder moved?")
        sys.exit(1)

    os.chdir(REPO_ROOT)

    # 2. remote sync (pull first to avoid push rejection)
    print("reaping remote updates...")
    try:
        sh.git.pull("origin", "main", "--rebase")
    except sh.ErrorReturnCode as e:
        print(
            f"pull failed (conflict?). fix manually in {REPO_ROOT}.\n{e.stderr.decode()}"
        )
        sys.exit(1)

    # 3. mirror obsidian -> logs/
    print(f"mirroring: {OBSIDIAN_SRC} -> {LOG_DEST}")
    os.makedirs(LOG_DEST, exist_ok=True)
    sh.rsync(
        "-av",
        "--delete",
        "--exclude",
        ".obsidian/",
        "--exclude",
        ".DS_Store",
        f"{OBSIDIAN_SRC}/",
        f"{LOG_DEST}/",
    )

    # 4. stage all (kit/, logs/, README, sync.py)
    sh.git.add("-A")

    # 5. atomic check & push
    try:
        # git diff-index --quiet HEAD returns 0 if no changes
        sh.git("diff-index", "--quiet", "HEAD", "--")
        print("nothing new to reap.")
    except sh.ErrorReturnCode_1:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        sh.git.commit("-m", f"reap: {ts}")
        sh.git.push("origin", "main")
        print(f"success: workspace pushed at {ts}")


if __name__ == "__main__":
    sync()
