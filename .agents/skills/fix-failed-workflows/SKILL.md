---
name: fix-failed-workflows
description: >-
  Diagnose and resolve failed GitHub Actions workflow runs (Documentation, spellcheck,
  link-check, zensical build, TOML decode errors, CookLang validation, and linting).
---

# Fix Failed Workflow Runs Skill

Use this skill when a GitHub Actions CI workflow run has failed, or when the user provides a failed run ID to diagnose and fix.

## Workflow

### 1. Identify and Inspect the Failed Run

List recent runs to find the failed run ID if not provided:

```bash
rtk gh run list --limit 10 | cat
```

Inspect the failure summary:

```bash
rtk gh run view <run-id> | cat
```

Retrieve the failed log directly:

```bash
rtk gh run view <run-id> --log-failed | cat
```

If deeper context is needed for a specific job:

```bash
rtk gh run view <run-id> --log --job=<job-id> | cat
```

---

### 2. Diagnose & Apply Target Fix

#### A. TOML Syntax / Structure Errors in `zensical.toml`
* **Symptom**: `tomli._parser.TOMLDecodeError` during `zensical build` (e.g. `Expected newline or end of document after a statement`).
* **Root cause**: Mismatched brackets, orphaned `] },` blocks, or missing category object wrapper `{ "Category" = [` inside `[[project.nav]]`.
* **Fix protocol**:
  1. Inspect the specified line in `zensical.toml`.
  2. Verify proper table/array nesting in `[[project.nav]]`.
  3. Validate TOML syntax:
     ```bash
     python3 -c "import tomllib; tomllib.loads(open('zensical.toml').read())"
     ```
  4. Run configuration and build checks:
     ```bash
     task validate
     task build
     ```

#### B. Zensical Build Warnings / Unresolved References
* **Symptom**: Unresolved reference warnings or unused link definitions causing build failure.
* **Fix protocol**:
  1. Run automatic fixer:
     ```bash
     uv run scripts/zensical_fix.py
     ```
  2. Re-test build:
     ```bash
     task build
     ```

#### C. Spellcheck / Typos Failures
* **Symptom**: `typos` step in `spellcheck` workflow fails on unrecognized terms.
* **Fix protocol**:
  1. If valid word/name, append to `dictionary.txt`.
  2. Sort dictionary:
     ```bash
     task sort
     ```
  3. Regenerate typos configuration:
     ```bash
     uv run scripts/generate_typos_config.py
     ```
  4. Validate target file:
     ```bash
     task spellcheck-file FILE="<path/to/file>"
     ```

#### D. Link Check Failures
* **Symptom**: `lychee` step in `link-check` workflow fails on broken relative or dead external links.
* **Fix protocol**:
  1. Run relative link fixer:
     ```bash
     uv run scripts/fix_broken_links.py
     ```
  2. For dead external URLs, locate and update or remove the link.
  3. Validate locally:
     ```bash
     task linkcheck
     ```

#### E. CookLang Recipe Validation Errors
* **Symptom**: `cook doctor validate` fails during recipe processing.
* **Fix protocol**:
  1. Run validator:
     ```bash
     task validate-cook FILE="<path/to/file.cook>"
     ```
  2. Ensure standard CookLang formatting: inline ingredients (`@ingredient{quantity%unit}`), proper timer syntax (`~{duration%unit}` without hyphens inside timer), and valid metadata.

#### F. Markdown / YAML Linting
* **Symptom**: `rumdl` or `yamllint-rs` failures.
* **Fix protocol**:
  1. Fix markdown formatting:
     ```bash
     task markdownlint-fix
     ```
  2. Correct YAML indentation manually per `.yamllint`.

---

### 3. Stage, Commit, Push, and Verify

1. Stage fixed files:
   ```bash
   rtk git add <files>
   ```
2. Commit with conventional commit message:
   ```bash
   rtk git commit -m "fix: resolve CI workflow failures (<short summary>)"
   ```
3. Push to remote:
   ```bash
   rtk git push origin main
   ```
4. Monitor new run until successful:
   ```bash
   rtk gh run list --limit 5 | cat
   ```
