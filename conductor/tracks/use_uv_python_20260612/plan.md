# Implementation Plan: Use `uv` for Python Scripts Execution

## Phase 1: Environment and Script Auditing [checkpoint: 7671e22]

- [x] Task: Audit all Python invocations in the repository d0e61ff
    - [x] Search `Taskfile.yaml`, `scripts/*.sh`, and `docs/**/*.md` for `python3` to locate all target lines
- [x] Task: Conductor - Verification 'Phase 1: Environment and Script Auditing' (Protocol in workflow.md) 7671e22

## Phase 2: Taskfile and Script Migration [checkpoint: bbe34a5]

- [x] Task: Update `Taskfile.yaml` to use `uv run` 538b159
    - [x] Update tasks like `validate` and `spellcheck` in `Taskfile.yaml` to run via `uv run`
- [x] Task: Update utility shell scripts to use `uv run` 9dc44b9
    - [x] Add check for the `uv` binary in scripts (e.g. `move.sh`) and fail cleanly if missing
    - [x] Replace `python3` with `uv run` inside shell scripts
- [x] Task: Validate modified scripts and Taskfile 6f6320f
    - [x] Run `task validate` and `task spellcheck-file` using the new `uv run` setup to ensure it works
- [x] Task: Conductor - Verification 'Phase 2: Taskfile and Script Migration' (Protocol in workflow.md) bbe34a5

## Phase 3: Documentation and Verification

- [ ] Task: Update developer documentation
    - [ ] Replace any raw `python3` commands with `uv run` in `docs/` and skills documentation
- [ ] Task: Verify full repository status
    - [ ] Run `task lint` and verify no syntax/link check errors exist
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Documentation and Verification' (Protocol in workflow.md)
