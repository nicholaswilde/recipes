# Specification - Auto-Emoji Mapper Script Option

## Overview
Enhance `scripts/check_recipe_emojis.py` with an auto-fixing mechanism (e.g. via a `--fix` CLI flag) to automatically append missing ingredients and cookware terms to `includes/emoji.yaml` under the most appropriate emoji groups, avoiding manual YAML edits.

## Functional Requirements
1. **Detection:** Runs the existing check logic to find missing ingredients or cookware terms.
2. **Auto-Mapping Logic:**
   - For each missing term, calculate substring or edit-distance similarity against existing mapped terms in `includes/emoji.yaml`.
   - If a high-confidence match is found (e.g., "almond flakes" matching "almonds"), suggest mapping it to the same emoji group (`chestnut`).
   - If no similar term is found, fallback to mapping to a generic category group or prompt/log an easy fallback.
3. **YAML Insertion:**
   - Automatically parse, insert the new term, and write it back to `includes/emoji.yaml` preserving formatting, comments, and structure.
4. **Command CLI:**
   - Invoked via:
     ```bash
     uv run scripts/check_recipe_emojis.py --fix <recipe_path.cook>
     ```

## Acceptance Criteria
- Running the script with `--fix` successfully maps all missing terms in `includes/emoji.yaml`.
- The modified YAML file is valid and sorted correctly.
