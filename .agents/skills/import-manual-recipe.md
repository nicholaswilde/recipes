---
name: import-manual-recipe
description: >-
  Import recipes from manual sources, images, PDFs, or unscrapable websites into CookLang format with strict validation. Trigger: /import-manual-recipe, 'import manual recipe'.
---

# Import Manual Recipe

Guide for importing recipes from manual sources, images, PDFs, or unscrapable websites (e.g. Serious Eats).

## Protocol

1. **Extract/Format:**
   - Image/PDF: Download and extract text (`lit parse` via `liteparse` skill).
   - Format into CookLang `.cook` file (use YAML metadata to pass strict validation).
   - **Hero Image Check**: Inspect the GitHub issue for the "Hero Image" checkbox
     (`- [X] Generate hero image` / `- [x] Generate hero image`).
     - **If checked**: Generate a hero image using the `generate-hero-image` skill (`generate_image` tool).
       Do NOT reuse original issue/source images.
     - **If unchecked**: Do not generate an AI image; only include an image if the source provides a usable
       photograph of the prepared dish.

2. **Run Orchestrator:**

   ```bash
   uv run scripts/import_manual_recipe.py <cook_file> [-i <image_path>] [-c <category>] [-n <issue_number>] [--commit]
   ```

   *Example:*

   ```bash
   uv run scripts/import_manual_recipe.py "Rolls.cook" -i "rolls.jpg" -c breads --commit
   ```

3. **Pipeline Steps (Auto):**
   - Copies `.cook` and image to `cook/<category>/`.
   - Runs `check_recipe_emojis.py --fix` so `includes/emoji.yaml` is updated before compiling.
   - Runs `move.sh` (`cook-docs doctor --check-recipes`, single-file `cook-docs` compile with emojis/weights/cross-links/merge, WebP/PNG optimization, `check_header_emojis.py --fix`, `rumdl fmt`, and nav update).
   - Spellchecks via `generate_typos_config.py` and `typos`.
   - Commits via `gh` CLI.
