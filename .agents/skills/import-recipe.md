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
   - The script will automatically scrape the recipe, compile the `.cook` file, move it to the correct destination under `docs/`, map missing emojis, convert volumetric units, run spellcheck, and interactive/auto-whitelist any proper nouns.
   - **Image/PDF Sources:** If the recipe is provided via an image or PDF in a GitHub issue, first download the file, run `lit parse <file_path>` (via the `liteparse` skill) to extract the text, format it into a `.cook` file in the correct category under `cook/`, and then run the remaining steps starting from `task move`.
    - Run the global spellcheck task (`task spellcheck`) and fix any issues before concluding.

## GitHub CLI (`gh`) Guidelines

When using the GitHub CLI (`gh`) to view issues, check workflow runs, or run other commands inside sandbox or
non-interactive terminals, always disable the interactive pager by piping the output to `cat` (e.g.,
`gh run list --limit 5 | cat` or `gh issue view 1253 | cat`). This prevents the command from hanging or warning
about a non-functional terminal.
