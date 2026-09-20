# /find-duplicate-issues

Scan GitHub issues and local recipe repositories to detect duplicate issues,
cross-issue duplicates, and recipes that have already been imported into the codebase.

## Description

This skill runs [`scripts/find_duplicate_issues.py`](file:///home/nicholas/git/nicholaswilde/recipes/scripts/find_duplicate_issues.py)
to perform a multi-dimensional scan across:

1. **Open Issue <-> Open Issue Duplicates**: Identifies multiple open issues tracking
   the exact same recipe URL, video ID, or near-identical dish title.
2. **Open Issue <-> Closed Issue Duplicates**: Identifies open issues that re-request recipes
   already closed or resolved in a previous issue.
3. **Open Issue <-> Local Codebase Matches**: Cross-references open issue URLs and titles
   against all existing recipes in `docs/` and `cook/`.
4. **Shared Roundup Grouping**: Discovers issues that reference multi-recipe articles
   (e.g., "Top 10 Muffins", "Best Dinners") while distinguishing them from single-recipe duplicates.

## Protocol

### 1. Perform Dry Run Scan

Run a full scan across open issues, closed issues, and local recipes:

```bash
uv run scripts/find_duplicate_issues.py
```

*Or via Taskfile:*

```bash
task find-duplicate-issues
```

### 2. Specialized Scans

- **Scan only issue-to-issue duplicates (ignore codebase check):**

  ```bash
  uv run scripts/find_duplicate_issues.py --mode issues
  ```

- **Scan only already-imported recipes:**

  ```bash
  uv run scripts/find_duplicate_issues.py --mode imported
  ```

- **Output structured JSON (for agent/automated processing):**

  ```bash
  uv run scripts/find_duplicate_issues.py --json
  ```

### 3. Automatically Close Exact Duplicates

To automatically close verified exact duplicates on GitHub:

```bash
uv run scripts/find_duplicate_issues.py --close
```

### 4. Manual Review and Closure

For high-similarity title matches or close matches that require human judgment:

1. Review the paired issues:

   ```bash
   rtk gh issue view <issue-number> | cat
   ```

2. Close confirmed duplicates:

   ```bash
   rtk gh issue close <duplicate-number> --duplicate-of <primary-number> | cat
   ```

   *Or if already imported into codebase:*

   ```bash
   rtk gh issue close <issue-number> -c "Closed as duplicate. Recipe already imported: <path>" | cat
   ```
