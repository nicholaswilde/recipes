# Implementation Plan - Recipe Import Workflow Orchestrator

## Phase 1: Implementation & Validation

- [ ] Task: Create `scripts/import_recipe_workflow.py`
    - [ ] Implement argument parsing (`url/issue`, `category`).
    - [ ] Add subprocess execution for `scrape_to_cook.py`, `task move`, `check-recipe-emojis.py --fix`, `convert-recipe-units.py`, and `task spellcheck`.
    - [ ] Implement auto-whitelisting logic for spellchecking failures.
- [ ] Task: Update Agent Skill Documentation
    - [ ] Edit `.agents/skills/import-recipe.md` to replace the manual multi-step workflow with instructions to run `scripts/import_recipe_workflow.py`.
- [ ] Task: Write Tests
    - [ ] Write integration/unit tests for the workflow orchestrator script.
- [ ] Task: Update Scripts Registry
    - [ ] Document the orchestrator in `scripts-registry.md`.
- [ ] Task: Conductor - User Manual Verification
