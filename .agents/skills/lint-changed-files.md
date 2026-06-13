# /lint-changed-files

Run fast linting checks only on modified, staged, or untracked Markdown and YAML files in the workspace (saves context tokens).

## Description

This skill runs `task lint-changed` to automatically run `rumdl` on modified Markdown files and
`yamllint-rs` on modified YAML files, avoiding the overhead and token consumption of checking
the entire repository.

## Protocol

1. **Verify Changed Files**:
   - Check which files have been modified or staged before running the linter:

     ```bash
     task git-summary
     ```

2. **Run Linting on Changed Files**:
   - Run the changed-files linter task:

     ```bash
     task lint-changed
     ```

   - **Success**: The command exits with `0` and outputs "All changed files passed linting successfully!".
     Proceed with commits.
   - **Failure**: The linter will print the exact files and lines containing formatting/syntax issues.
     Fix them and re-run `task lint-changed`.

3. **Deploy**:
   - Stage and commit the corrected files.
