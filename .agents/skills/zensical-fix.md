# /zensical-fix

Validate the Zensical project and automatically fix issues found during validation and build.

## Description
This skill leverages the `zensical_fix.py` helper script to automatically run Zensical configuration validation and clean builds, parse output warnings (such as unresolved reference links or unused link definitions), and correct them instantly across recipe markdown files.

## Protocol
1. **Run the Zensical Auto-Fixer Script**:
   - Execute the python script in the repository root to automatically run validation and build steps and resolve any common issues:
     ```bash
     uv run scripts/zensical_fix.py
     ```
   - The script will:
     - Run `task validate` to verify that `zensical.toml` has no syntax issues.
     - Run `zensical build --clean` to gather all build warnings/errors.
     - Parse the build output and strip ANSI color sequences.
     - Automatically clean up unused link definitions by removing the definition line.
     - Automatically resolve unresolved link references (e.g. escaping `[ml]`/`[g]` to `\[ml\]`/`\[g\]` and turning unresolved target references like `[vegetable broth][1]` into clean plain text like `vegetable broth`).
     - Re-run `zensical build --clean` to verify that the build succeeds with exit code 0.

2. **Verify and Deploy**:
   - Verify that `git status` lists only the expected changes.
   - Run a clean build manually if needed to confirm zero warnings:
     ```bash
     zensical build --clean
     ```
   - Stage, commit, and push any modified recipe files following conventional commit standards.
