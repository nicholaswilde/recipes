# Specification - Recipe Import Workflow Orchestrator

## Overview
Develop a Python orchestrator `scripts/import_recipe_workflow.py` that aggregates all single recipe import utilities (scraping, moving, emoji verification & auto-fixing, unit conversion, spellchecking, and whitelisting) into a single CLI command execution to reduce agent token usage. Update the agent import recipe skill to instruct agents to run this orchestrator.

## Functional Requirements
1. **CLI Interface:** Accept target recipe URL or GitHub issue number, and target category as input.
2. **Orchestrated Workflow:**
   - **Step 1:** Run `scripts/scrape_to_cook.py` to extract recipe content and download the image.
   - **Step 2:** Run `task move` to compile the `.cook` file, move the image, and insert navigation.
   - **Step 3:** Run `scripts/check-recipe-emojis.py --fix` to verify and auto-add missing emojis.
   - **Step 4:** Run `scripts/convert-recipe-units.py` to convert volumetric measurements to weight and add emojis.
   - **Step 5:** Run `task spellcheck` to check for spelling errors. If spelling errors exist, prompt/detect proper nouns and run `scripts/whitelist_typos.py` to whitelist them automatically.
3. **Agent Skill Update:**
   - Modify the `/import-recipe` skill ([import-recipe.md](file:///.agents/skills/import-recipe.md)) to instruct agents to use `scripts/import_recipe_workflow.py` instead of running each step manually, significantly reducing the prompt token size and trajectory step count.

## Acceptance Criteria
- Running `uv run scripts/import_recipe_workflow.py <URL_or_issue> <category>` successfully performs the entire import process.
- The `.agents/skills/import-recipe.md` file is updated to document the new simplified workflow.
