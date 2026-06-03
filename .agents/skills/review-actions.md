# Review Actions & Fix Failures Skill

Monitor GitHub Actions workflow runs, diagnose failure logs, and resolve issues (linting, spellcheck, link check, or build failures).

## Description
This skill outlines how to list workflow runs, inspect detailed job logs, and apply automated or manual fixes for typical repository failures. All `gh` commands must be piped to `cat` to bypass interactive pagination.

---

## Protocol

### 1. Monitor Workflow Status
Run the following command to check the status of the 10 most recent workflow runs:
```bash
gh run list --limit 10 | cat
```

If a run shows `failed`, retrieve its detailed job list using the run ID:
```bash
gh run view <run-id> | cat
```

To fetch the full logs for a specific failed job:
```bash
gh run view --log --job=<job-id> | cat
```

---

### 2. Diagnose & Resolve Common Failures

Based on the job logs, apply the corresponding fix protocol:

#### A. Markdown / YAML Linting Failures
* **Diagnostic**: Log shows lint warnings from `rumdl` or `yamllint-rs`.
* **Fix**:
  - Run markdown autofix:
    ```bash
    task markdownlint-fix
    ```
  - For YAML files, inspect [.yamllint](file:///home/nicholas/git/nicholaswilde/recipes/.yamllint) and correct indentation or formatting manually.

#### B. Spellcheck (Typos) Failures
* **Diagnostic**: Log shows typos detected by the spellchecker action.
* **Fix**:
  - If they are valid words/terms that need whitelisting, append them to the end of [dictionary.txt](file:///home/nicholas/git/nicholaswilde/recipes/dictionary.txt).
  - Sort the dictionary:
    ```bash
    task sort
    ```
  - Regenerate configuration:
    ```bash
    python3 scripts/generate_typos_config.py
    ```
  - Commit the updated `dictionary.txt` and `_typos.toml`.

#### C. Link Check Failures
* **Diagnostic**: Lychee outputs broken links or missing local assets.
* **Fix**:
  - Run the relative link fixer script to automatically resolve pathing errors:
    ```bash
    python3 scripts/fix_broken_links.py
    ```
  - For external URLs that are permanently down or invalid, locate the file and update or remove the link.

#### D. Zensical Build Failures
* **Diagnostic**: Log outputs compilation or configuration reference warnings (e.g. unused links, brackets).
* **Fix**:
  - Run the zensical automatic fixer script:
    ```bash
    python3 scripts/zensical_fix.py
    ```

---

### 3. Stage and Verify Fixes
* Push the staged fixes to `main`:
  ```bash
  git add -A
  git commit -m "fix: resolve CI workflow failures"
  git push origin main
  ```
* Re-run the monitor command to ensure the new push triggers a green `success` status:
  ```bash
  gh run list --limit 5 | cat
  ```
