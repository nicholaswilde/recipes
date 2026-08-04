# /import-recipe `args`

Import a recipe from a URL or a GitHub issue number.

## Description

This skill imports a recipe from a specified source (a URL or a GitHub issue number) into the project's
repository following the established recipe import workflow.

## Protocol

1. **Use the Import Recipe Orchestrator:**
   Run the unified import orchestrator script with the target URL or GitHub issue number (and optional category override):

   ```bash
   uv run scripts/import_recipe_workflow.py <URL_or_issue_number> [category]
   ```

2. **Under the Hood / Manual Exceptions:**
   - The workflow script automatically scrapes the recipe, compiles the `.cook` file, relocates it, matches emojis, converts volumetric units, runs the spellchecker, and whitelists proper nouns.
   - **Image/PDF or Unscrapable Sources:** If the recipe is from an image, a PDF, or a website that blocks scraping (e.g. Serious Eats), first extract the text (using `lit parse` from the `liteparse` skill if needed), create the `.cook` file, and then run the manual orchestrator script:

     ```bash
     uv run scripts/import_manual_recipe.py <cook_file> [-i <image_path>] [-c <category>] [-n <issue_number>] [--commit]
     ```

   - **PDF-specific Automation:** If the source is a PDF, you can automate downloading, text parsing, and hero image cropping into a single step using the PDF import workflow:

     ```bash
     uv run python3 scripts/import_pdf_workflow.py <PDF_URL_or_path> [-c <category>] [-n <issue_number>] [--commit]
     ```

     This will extract raw text into the `.cook` draft file and auto-crop the hero image for you to finalize.

   - **Spellcheck Validation:** When validating spellings, prefer the focused file spellchecker (e.g., `task spellcheck-file FILE="docs/{category}/{recipe-name}.md"`) instead of checking the whole project.

3. **Commit Changes:**
   - If not committed automatically by the manual orchestrator, stage and commit files using:

     ```bash
     task commit FILES="cook/{category}/{Recipe Name}.cook"
     ```

## GitHub CLI (`gh`) Guidelines

When using the GitHub CLI (`gh`) to view issues, check workflow runs, or run other commands inside sandbox or
non-interactive terminals, always disable the interactive pager by piping the output to `cat` (e.g.,
`gh run list --limit 5 | cat` or `gh issue view 1253 | cat`). This prevents the command from hanging or warning
about a non-functional terminal.
