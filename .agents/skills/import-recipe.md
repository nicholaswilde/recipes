# /import-recipe `args`

Import recipe from URL or GitHub issue.

## Protocol

1. **Auto Import:**
   ```bash
   uv run scripts/import_recipe_workflow.py <URL_or_issue_number> [category]
   ```
   (Scrapes, compiles, formats, spellchecks, commits automatically)

2. **Manual Exceptions (Image/PDF/Unscrapable):**
   - Extract text (`lit parse` via `liteparse` skill).
   - Draft `.cook` file (use YAML frontmatter to pass strict validation).
   - Run manual orchestrator:
     ```bash
     uv run scripts/import_manual_recipe.py <cook_file> [-i <image_path>] [-c <category>] [-n <issue_number>] [--commit]
     ```

3. **PDF Automation:**
   ```bash
   uv run python3 scripts/import_pdf_workflow.py <PDF_URL_or_path> [-c <category>] [-n <issue_number>] [--commit]
   ```

4. **Validation:**
   - Prefer file-specific spellcheck: `task spellcheck-file FILE="docs/{category}/{recipe-name}.md"`
   - Validate CookLang syntax: `task validate-cook FILE="cook/{category}/{Recipe Name}.cook"`

5. **Commit (If manual):**
   ```bash
   task commit FILES="cook/{category}/{Recipe Name}.cook"
   ```

## RTK & GitHub CLI Guidelines

- Prefix `gh` commands with `rtk` and pipe to `cat` (e.g., `rtk gh issue view <num> | cat`).
- Prefix git commands with `rtk` (e.g., `rtk git status`).
- Prevents interactive pager hangs and saves tokens.
