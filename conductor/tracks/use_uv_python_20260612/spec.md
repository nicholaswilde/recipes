# Specification: Use `uv` for Python Scripts Execution

## Overview
This track replaces direct `python3` invocations in task definitions, utility scripts, and developer documentation with `uv run` (or `uv run python`) to leverage the fast, project-wide managed Python virtual environment and lockfile (`uv.lock`).

## Functional Requirements
- **Executable Script & Task Updates:**
  - Replace direct calls to `python3` with `uv run` in `Taskfile.yaml` (e.g. `task validate`, `task spellcheck-file`).
  - Replace `python3` invocations inside utility shell scripts (e.g. in `scripts/*.sh` like `move.sh`, etc.) with `uv run`.
- **Dependency & Environment Verification:**
  - In bash/utility scripts, verify the presence of the `uv` command. If `uv` is not found, exit gracefully with an informative error message instructing the user to install `uv`.
- **Documentation Updates:**
  - Scan all `.md` files in the repository (specifically in `docs/` and root developer documentation) and replace instructions calling `python3 script.py` with `uv run script.py`.

## Non-Functional Requirements
- Ensure that `uv run` correctly resolves package imports (e.g. `tomllib`, `yaml`) using the existing virtual environment.
- Maintain compatibility with standard Unix shell environments.

## Acceptance Criteria
- All commands in `Taskfile.yaml` that execute Python code run successfully using `uv run`.
- All utility shell scripts calling Python scripts execute successfully via `uv run`.
- Missing `uv` installations fail with a clean message instead of shell error.
- All documentation files accurately instruct developers to use `uv run`.
- `task lint` and `task validate` run successfully with zero errors.

## Out of Scope
- Rewriting the Python scripts themselves unless necessary for compatibility.
- Modifying workflows that do not involve Python script execution.
