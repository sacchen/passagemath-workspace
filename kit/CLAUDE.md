# Project directives

> Full agent context is in `AGENTS.md` (`/Users/goddess/foundry/sandbox/passagemath/AGENTS.md`) — read it at the start of any session.

## Search tooling

- Use the `Grep` tool (not `Bash` + `rg`) for content search.
- Use the `Glob` tool (not `Bash` + `fd`/`find`) for file discovery.
- When `rg` or `fd` must be used in `Bash` (piped processing or features
  the dedicated tools don't expose), pass `--no-heading` for
  machine-readable output.

## Environment

- Prefer `uv` for all Python environment management. Never suggest `pip`
  as a primary tool.
