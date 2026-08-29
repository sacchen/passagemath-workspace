#!/usr/bin/env bash
# Path resolution for the auto pipeline. No absolute paths are hardcoded:
# this repo is public (see kit/PRIVACY.md).
#
# Override any of these by exporting them before calling a check.

SANDBOX="${PM_SANDBOX:-$HOME/foundry/sandbox/passagemath}"
REPO="${PM_REPO:-$SANDBOX/passagemath}"
WORKSPACE="${PM_WORKSPACE:-$HOME/foundry/sandbox/passagemath-workspace}"
AUTO="$WORKSPACE/kit/auto"
QUEUE="$AUTO/queue"

# Default venv. Task files override with `venv:` in frontmatter.
VENV="${PM_VENV:-$SANDBOX/.venv}"

die() { echo "FATAL: $*" >&2; exit 2; }

# Read one frontmatter key out of a task file. Handles plain scalars and the
# YAML block scalars `>`, `>-`, `|`, `|-`, whose value sits on the following
# indented lines. Folded (`>`) forms join with a space, literal (`|`) with a
# newline. Getting this wrong is silent: task_key used to return the literal
# ">-" for doctest_cmd, and negative_control.sh then ran `eval ">-"`, which
# creates a file named "-" and exits 0, reporting a passing control that never
# ran a doctest.
task_key() {
    local file="$1" key="$2"
    awk -v k="$key" '
        NR==1 && $0=="---" { infm=1; next }
        infm && $0=="---" { exit }
        infm && block {
            if ($0 ~ /^[ \t]+[^ \t]/) {
                line=$0
                sub(/^[ \t]+/, "", line)
                sub(/[ \t]+$/, "", line)
                out = (out=="" ? line : out sep line)
                next
            }
            exit
        }
        infm && $0 ~ "^"k":" {
            sub("^"k":[ \t]*", "")
            sub(/[ \t]+$/, "")
            if ($0 ~ /^[|>][-+]?$/) { block=1; sep=($0 ~ /^\|/ ? "\n" : " "); next }
            sub(/[ \t]+#.*$/, "")
            print; exit
        }
        END { if (block) print out }
    ' "$file"
}

# Read a frontmatter list key (YAML block sequence) as one path per line.
task_list() {
    local file="$1" key="$2"
    awk -v k="$key" '
        NR==1 && $0=="---" { infm=1; next }
        infm && $0=="---" { exit }
        infm && $0 ~ "^"k":" { inlist=1; next }
        inlist && $0 ~ /^[a-zA-Z_]+:/ { inlist=0 }
        inlist && $0 ~ /^[ \t]*-[ \t]+/ { sub(/^[ \t]*-[ \t]+/, ""); print }
    ' "$file"
}

site_packages() {
    local venv="${1:-$VENV}"
    "$venv/bin/python" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'
}
