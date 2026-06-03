# /resolve-duplicate-issues

Scan open duplicate-labeled issues on GitHub and automatically close them if the corresponding recipe has already been imported into the codebase.

## Description
This skill leverages [scripts/find_duplicate_issues.py](file:///home/nicholas/git/nicholaswilde/recipes/scripts/find_duplicate_issues.py) to parse issues on GitHub with the `duplicate` label, index all existing recipes in the local `docs/` folder, and cross-reference them via source URLs and title keyword matching.

## Protocol

### 1. Perform Dry Run Check
Scan open duplicate issues and list matches without closing them:
```bash
python3 scripts/find_duplicate_issues.py
```

---

### 2. Auto-Close Exact Matches
To automatically close the exact URL matches on GitHub with a comment pointing to the existing recipe path:
```bash
python3 scripts/find_duplicate_issues.py --close
```

---

### 3. Review and Close Keyword Matches Manually
Review the close matches section printed by the script. For any verified duplicate, close it using the GitHub CLI:
```bash
gh issue close <issue-number> -c "Closed as duplicate. Existing recipe: <relative-path-to-recipe>"
```
*(Example: `gh issue close 1285 -c "Closed as duplicate. Existing recipe: docs/beverages/hot-chocolate.md"`)*
