# Specification - Triage Recipe Backlog

## Overview

Import and process recipe issues #1378 and #1379 using the new unified `scripts/import_recipe_workflow.py` script.

## Functional Requirements

1. **Import Issue #1378 (Ginger and Garlic Green Beans):**
   - Run orchestrator script.
   - Resolve any missing emojis or spelling dictionary entries.
2. **Import Issue #1379 (Green Beans with Lime and Red Onions):**
   - Run orchestrator script.
   - Resolve any missing emojis or spelling dictionary entries.
3. **Verify Build:**
   - Verify `zensical build` compiles successfully and both new recipes are fully integrated and linked in
     the navigation menu.

## Acceptance Criteria

- Recipes are successfully imported under `docs/sides/`.
- Site builds successfully without spelling or link errors.
