# Specification - Taskfile Shortcuts

## Overview

Add task shortcuts `import-recipe` and `whitelist-typo` to `Taskfile.yaml` to make running
`scripts/import_recipe_workflow.py` and `scripts/whitelist_typos.py` simpler and more convenient.

## Functional Requirements

1. **import-recipe Task:**
   - Command: `uv run scripts/import_recipe_workflow.py {{shellQuote .URL}} {{shellQuote .CATEGORY}}`
   - Accepts arguments `URL` and `CATEGORY`.
2. **whitelist-typo Task:**
   - Command: `uv run scripts/whitelist_typos.py {{.WORDS}}`
   - Accepts words as arguments.

## Acceptance Criteria

- Running `task import-recipe URL="1378" CATEGORY="sides"` runs the unified orchestrator script correctly.
- Running `task whitelist-typo WORDS="myword"` runs the whitelist typos script correctly.
