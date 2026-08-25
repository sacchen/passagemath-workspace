# Setup

This is for you if `onboarding.md` assumed too much — if git, virtual environments, or working in a terminal are new.

---

## VSCode

Install [VSCode](https://code.visualstudio.com/). This is where you'll edit code, run a terminal, and manage git.

---

## Clone the repo

You need a GitHub account. Fork [passagemath/passagemath](https://github.com/passagemath/passagemath) — there's a Fork button in the top right.

Then in VSCode, open the Command Palette with Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows), type "Git: Clone", and paste your fork's URL:

```
https://github.com/YOUR_USERNAME/passagemath.git
```

VSCode will open a browser window to sign in to GitHub — follow the prompts. After that it'll download the repo and ask if you want to open it. Say yes.

To confirm it worked, open the Explorer panel (the file icon in the left sidebar) and navigate to `src/sage/plot/graphics.py`. You should see Python code.

---

## Two repos

- **[passagemath/passagemath](https://github.com/passagemath/passagemath)** — the source code. This is what you forked above.
- **[sacchen/passagemath-workspace](https://github.com/sacchen/passagemath-workspace)** — this repo, with onboarding docs and exercises.

---

## Git in VSCode

VSCode has a built-in git interface. Open it by clicking the **Source Control** icon in the Activity Bar on the left — it looks like a small branching diagram (three dots connected by lines). Or press Ctrl+Shift+G.

### Branches

Always work on a branch, not directly on `main`. In the bottom-left status bar, you'll see the current branch name (e.g. `main`) with a branch icon next to it. Click it → **Create new branch** → give it a name like `fix/repr-png-graphics`.

To switch branches, click the branch name again and pick from the list.

### Staging, committing, pushing

When you edit a file it appears under **Changes** in the Source Control panel, with an `M` (modified) or `U` (untracked) label. To stage files:
- Click **+** next to an individual file to stage just that file
- Click **+** next to the **Changes** header to stage everything at once

Once staged, files move to **Staged Changes**. Write a message in the box at the top and click **Commit** (the checkmark button).

To push: on a new branch the button says **Publish Branch** — click it to push to your fork for the first time. On subsequent commits it says **Sync Changes** — click that.

You can also do all of this from the terminal if you prefer — the GUI and the command line stay in sync.

---

## Terminal

VSCode has a built-in terminal: **Terminal** menu → **New Terminal**. You'll need it for uv and JupyterLab.

A few commands you'll use constantly:

```bash
pwd          # where am I right now?
ls           # what's in this directory? (Mac)
dir          # what's in this directory? (Windows)
cd somewhere # move into a subdirectory
cd ..        # go up one level
```

---

## Package manager

**Mac:** Install [Homebrew](https://brew.sh) by pasting this in the terminal:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Nothing is shown while you type your password — that's normal. After it finishes, run any `export PATH=...` commands it prints under "Next steps", then close and reopen the terminal.

```bash
brew --version   # check it worked
```

**Windows:** winget is built in on Windows 10/11. Check with `winget --version`. If it's not there, install it from the Microsoft Store ("App Installer").

---

## uv

[uv](https://docs.astral.sh/uv/) installs Python and manages packages.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh     # Mac
```

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows
```

Close and reopen the terminal after installing.

```bash
uv --version   # check it worked
```

**`uv`: command not found** — terminal wasn't restarted.

**`Could not find Python`** — run `uv python install`.

**Build tool errors** (`ninja`, `meson`, `cmake`) — install whatever it mentions and retry:

```bash
brew install ninja meson cmake     # Mac
winget install Ninja-build.Ninja   # Windows
```

`uv run` runs a command inside the project's virtual environment without activating it:

```bash
uv run python -m sage.doctest src/sage/plot/graphics.py
```

---

## JupyterLab (for exercises)

JupyterLab is used for the exercises in `passagemath-workspace` — separate from VSCode and separate from the passagemath source code.

In the terminal, navigate to `passagemath-workspace` (clone it the same way you cloned passagemath if you haven't), then:

```bash
cd exercises/importerror-fix-pattern
uv sync
uv run jupyter lab
```

This opens a browser tab. Click the `.ipynb` file to open the notebook.

**Browser didn't open** — copy the URL from the terminal (looks like `http://127.0.0.1:8888/lab?token=...`) and paste it in a browser.

---

## Next

Read through [onboarding.md](onboarding.md) — it covers the passagemath project, how to find work, and how to make a PR.
