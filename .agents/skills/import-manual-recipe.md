# Import Manual Recipe

Guide for importing recipes from manual sources, images, PDFs, or unscrapable websites (e.g. Serious Eats).

## Protocol

1. **Extract/Format:**
   - Image/PDF: Download and extract text (`lit parse` via `liteparse` skill).
   - Format into CookLang `.cook` file (use YAML metadata to pass strict validation).
   - Generate a hero image using the `generate-hero-image` skill (do NOT reuse original issue/source images).

2. **Run Orchestrator:**
   ```bash
   uv run scripts/import_manual_recipe.py <cook_file> [-i <generated_image_path>] [-c <category>] [-n <issue_number>] [--commit]
   ```
   *Example:*
   ```bash
   uv run scripts/import_manual_recipe.py "Rolls.cook" -i "rolls.jpg" -c breads --commit
   ```

3. **Pipeline Steps (Auto):**
   - Copies `.cook` and image to `cook/<category>/`.
   - Runs `move.sh` to compile Markdown in `docs/`, WebP image, and `cook doctor validate`.
   - Runs `check_recipe_emojis.py --fix`.
   - Runs `convert_recipe_units.py` (weights/emojis).
   - Spellchecks via `generate_typos_config.py` and `typos`.
   - Commits via `gh` CLI.
