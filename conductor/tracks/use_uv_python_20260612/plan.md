# Implementation Plan: Use `uv` for Python Scripts Execution

## Phase 1: Environment and Script Auditing
- [ ] Task: Audit all Python invocations in the repository
    - [ ] Search `Taskfile.yaml`, `scripts/*.sh`, and `docs/**/*.md` for `python3` to locate all target lines
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Environment and Script Auditing' (Protocol in workflow.md)

## Phase 2: Taskfile and Script Migration
- [ ] Task: Update `Taskfile.yaml` to use `uv run`
    - [ ] Update tasks `validate`, `spellcheck`, `spellcheck-file`, and others in `Taskfile.yaml` to run via `uv run`
- [ ] Task: Update utility shell scripts to use `uv run`
    - [ ] In `scripts/move.sh` and other shell scripts, add a check for the `uv` binary and print a clean installation error if missing
    - [ ] Replace `python3` with `uv run` inside shell scripts
- [ ] Task: Validate modified scripts and Taskfile
    - [ ] Run `task validate` and `task spellcheck-file FILE=docs/lunches/creamy-chickpea-eggless-egg-salad-sandwich.md` using the new `uv run` setup to ensure it works
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Taskfile and Script Migration' (Protocol in workflow.md)

## Phase 3: Documentation and Verification
- [ ] Task: Update developer documentation
    - [ ] Replace any raw `python3` commands with `uv run` in `docs/` and root `.md` files (like `.agents/skills/`, etc.)
- [ ] Task: Verify full repository status
    - [ ] Run `task lint` and verify no syntax/link check errors exist
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Documentation and Verification' (Protocol in workflow.md)
