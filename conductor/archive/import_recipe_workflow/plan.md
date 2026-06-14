# Implementation Plan - Recipe Import Workflow Orchestrator

## Phase 1: Implementation & Validation [checkpoint: e313d2f]

- [x] Task: Create `scripts/import_recipe_workflow.py` (be8ae71)
    - [x] Implement argument parsing (`url/issue`, `category`).
    - [x] Add subprocess execution for `scrape_to_cook.py`, `task move`, `check-recipe-emojis.py --fix`, `convert-recipe-units.py`, and `task spellcheck`.
    - [x] Implement auto-whitelisting logic for spellchecking failures.
- [x] Task: Update Agent Skill Documentation (0a8a0e9)
    - [x] Edit `.agents/skills/import-recipe.md` to replace the manual multi-step workflow with instructions to run `scripts/import_recipe_workflow.py`.
- [x] Task: Write Tests (be8ae71)
    - [x] Write integration/unit tests for the workflow orchestrator script.
- [x] Task: Update Scripts Registry (0a8a0e9)
    - [x] Document the orchestrator in `scripts-registry.md`.
- [x] Task: Conductor - User Manual Verification (e313d2f)
