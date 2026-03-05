# Passagemath Agent Kit (Developer Infrastructure)

This repository contains the **Developer Kit** used to optimize agentic workflows for contributing to the [passagemath](https://github.com/passagemath/passagemath) monorepo.

## 🤖 The Multi-Agent Orchestration (Roles & Quota Management)

Contributing to a complex math-oriented monorepo requires high precision and strategic context usage. This kit employs a **Role-Based Chain of Command** to ensure correctness and efficient subscription quota management.

| Agent/Model | Identity | Primary Domain | When to Delegate/Switch |
| --- | --- | --- | --- |
| **Gemini CLI** | **The Scout** | Repo-wide search, log forensics, finding "Neglected" patterns. | **Delegate implementation** once files are identified. |
| **Claude Code** | **The Architect** | High-logic refactoring, complex Python/Cython logic. | **Switch to Copilot** for unit tests or boilerplate. |
| **Copilot (Sonnet 4.6)** | **The Draftsman** | Standard feature implementation, fixing "Tractable" bugs. | **Switch to Gemini** if context is missing across the monorepo. |
| **Copilot (GPT-5 mini)** | **The Polisher** | Documentation, docstrings, `uv` config updates. | **Switch to Sonnet** if logic changes are required. |

## 📐 The S.N.T. Leverage Framework

We prioritize contributions based on their **High-Leverage Potential**:

1.  **SCALE**: Infrastructure/dependency depth (e.g., `.m4` templates for 100+ modular packages).
2.  **NEGLECTED**: "Modularization Blind Spots" (e.g., silent `ImportError` masks resulting in runtime `NameError`).
3.  **TRACTABLE**: Surgical fixes with minimal review burden and clear reproduction scripts.

## 🛠️ Usage Instructions

To use this kit without polluting the main `passagemath` codebase:

1.  Clone this kit into a separate directory: `~/foundry/passagemath-agent-kit`.
2.  In your `passagemath` working directory, symlink the files:
    ```bash
    ln -s ~/foundry/passagemath-agent-kit/AGENTS.md .
    ```
3.  Add `AGENTS.md` and `AGENT_STATE.md` to your **global gitignore** (`~/.gitignore_global`) to ensure they never appear in Pull Requests.

---
*Created by [sacchen](https://github.com/sacchen)*
