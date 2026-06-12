# /linkcheck-fix

Perform a fast offline link check and automatically resolve and fix any broken local markdown links and image paths.

## Description

This skill leverages `lychee` in offline mode to identify broken local references (file paths, images,
cross-references) across all recipes, and uses the dynamic link auto-fixer script to resolve them instantly.

## Protocol

1. **Perform Offline Link Check**:
   - Run the offline link check task to find any broken local references:

     ```bash
     task linkcheck-offline
     ```

   - If the task finishes with `exit status 0` and `0 Errors`, all local links and image paths are verified as correct.
   - If the task reports errors, proceed to step 2 to fix them.

2. **Run the Link Auto-Fixer Script**:
   - Execute the dynamic python script that scans the repository, builds a complete directory structure map,
     and automatically corrects any broken relative references:

     ```bash
     uv run scripts/fix_broken_links.py
     ```

   - The script will automatically:
     - Re-calculate and fix incorrect relative directory paths based on current file nesting depth.
     - Match and fix document/image link targets with incorrect file extensions (e.g., `.png` vs `.jpg`).
     - Perform smart fallback matching for image names that differ slightly on disk.

3. **Verify and Deploy**:
   - Run the offline checker once more to confirm all errors are fully resolved:

     ```bash
     task linkcheck-offline
     ```

   - Stage, commit, and push any modified recipe files following conventional commit standards.
