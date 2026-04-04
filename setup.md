# Setup

This is for you if `onboarding.md` assumed too much — if git, virtual environments, or working in a terminal are new.

---

## VSCode and terminal

Install [VSCode](https://code.visualstudio.com/) if you haven't. Open it, then open its built-in terminal: **Terminal** menu → **New Terminal**.

A few commands you'll use constantly:

```bash
pwd          # where am I right now?
ls           # what's in this directory? (Mac)
dir          # what's in this directory? (Windows)
cd somewhere # move into a subdirectory
cd ..        # go up one level
cd ~         # go to your home directory
```

---

## Package manager

**Mac:** Install [Homebrew](https://brew.sh) by pasting this in your terminal:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

It'll ask for your password (nothing is shown while you type, that's normal). After it finishes, it may print a few lines about "Next steps" with `export PATH=...` commands — run those, then close and reopen the terminal.

```bash
brew --version   # check it worked
```

**Windows:** winget is built in on Windows 10/11. Check with `winget --version`. If it's not there, install it from the Microsoft Store ("App Installer").

---

## Git

Git tracks changes to files and lets you share them. GitHub hosts git repositories.

**Install:**

```bash
brew install git          # Mac
winget install Git.Git    # Windows (then restart terminal)
```

**One-time setup:**

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Use the same email as your GitHub account.

### Two repos

- **[passagemath/passagemath](https://github.com/passagemath/passagemath)** — the source code. This is what you fork and edit.
- **[sacchen/passagemath-workspace](https://github.com/sacchen/passagemath-workspace)** — this repo, with onboarding docs and exercises.

### Cloning and opening

Fork `passagemath/passagemath` on GitHub, then clone it via VSCode — this handles authentication automatically through a browser sign-in, no SSH keys or tokens needed.

Open the Command Palette with Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows), type **Git: Clone**, and paste your fork's URL:

```
https://github.com/YOUR_USERNAME/passagemath.git
```

VSCode will open a browser window to sign in to GitHub. After that it'll download the repo and ask if you want to open it. Say yes.

To confirm it worked, open `src/sage/plot/graphics.py` in the Explorer panel on the left — you should see Python code. If VSCode prompts you to install the Python extension, do it.

To check your remotes:

```bash
git remote -v
```

You should see `origin` pointing to your fork. To also pull in updates from the original repo, add `upstream`:

```bash
git remote add upstream https://github.com/passagemath/passagemath.git
```

### Branches

Work happens on branches, not directly on `main`. Create one before making any changes:

```bash
git checkout -b fix/short-description   # create a new branch and switch to it
git branch                              # list branches (current one has *)
git checkout main                       # switch back to main
```

### The basic workflow

```bash
git status                             # see what's changed and what branch you're on
git add src/sage/path/to/file.py       # stage a specific file
git add .                              # or stage everything in the current directory
git commit -m "describe what you did"  # save a snapshot
git push origin fix/short-description  # push to your fork on this branch
```

`git push origin fix/short-description` means: push to `origin` (your fork) on a branch called `fix/short-description`. If the branch doesn't exist on GitHub yet, it creates it. After the first push you can just run `git push`.

`git add .` stages everything in the current directory — run `git status` first to make sure you're not including something unintended.

---

## uv

[uv](https://docs.astral.sh/uv/) installs Python and manages packages.

**Install:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh     # Mac
```

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows
```

Close and reopen your terminal after installing.

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

`uv run` runs a command inside the project's virtual environment without you having to activate it:

```bash
uv run python -m sage.doctest src/sage/plot/graphics.py
```

---

## JupyterLab (for exercises)

JupyterLab is a browser-based environment for running Python interactively. It's used for the exercises in `passagemath-workspace` — it's separate from VSCode and separate from the `passagemath` source code.

If you need to install it standalone:

```bash
uv pip install jupyterlab
```

The exercises install it automatically via `uv sync`. To open one, first make sure you're in the `passagemath-workspace` directory, then:

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
