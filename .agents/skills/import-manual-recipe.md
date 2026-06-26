# Import Manual Recipe

This skill guides the import of recipes from manual sources, images, PDFs, or websites that cannot be automatically scraped due to blocking (e.g. Serious Eats).

## Description

This skill utilizes the manual recipe import orchestrator script (`import_manual_recipe.py`) to compile the `.cook` recipe file, process the optional hero image, auto-map missing emojis, convert volumetric units, spellcheck the generated Markdown, whitelist proper nouns, and commit changes using structured conventional commits.

## Protocol

1. **Extract/Format the Recipe Text:**
   - If the recipe is from an image or PDF, download the file and use the `liteparse` skill (e.g., `lit parse <path>`) to extract and organize the text content.
   - Format the recipe into CookLang syntax and save it as a `.cook` file (e.g. `Golden Milk.cook`).

2. **Run the Manual Import Orchestrator:**
   Invoke the unified manual import orchestrator script, specifying the `.cook` file path and optional category, image path, or issue number:

   ```bash
   uv run scripts/import_manual_recipe.py <cook_file> [-i <image_path>] [-c <category>] [-n <issue_number>] [--commit]
   ```

   *Parameters:*
   - `<cook_file>` (Mandatory): Path to the locally created `.cook` file.
   - `-i`, `--image` (Optional): Path to the downloaded recipe hero image.
   - `-c`, `--category` (Optional): The destination recipe category (e.g., `breads`, `breakfast`, `desserts`, `sides`, `sauces-and-dressings`). If omitted in an interactive terminal, the script prompts you with a list of categories.
   - `-n`, `--issue` (Optional): GitHub issue number to reference in the commit (e.g. `123` for `#123`).
   - `--commit` (Optional): Flag to automatically stage and commit files without prompt.

   *Example:*
   To import a manually created recipe `Classic Dinner Rolls.cook` with an image `rolls.jpg` to the `breads` category:

   ```bash
   uv run scripts/import_manual_recipe.py "Classic Dinner Rolls.cook" -i "rolls.jpg" -c breads
   ```

3. **Under the Hood Pipeline:**
   The orchestrator will:
   - Copy the `.cook` and image files to their correct staging folder under `cook/`.
   - Run `move.sh` to generate the Markdown file in `docs/` and convert the image to WebP.
   - Run `check-recipe-emojis.py --fix` to verify emojis in `includes/emoji.yaml` (using keyword heuristics and fuzzy similarity matching).
   - Run `convert-recipe-units.py` to annotate volumetric units with weights and prepend ingredient emojis.
   - Run `generate_typos_config.py` and spellcheck the single file using `typos`, whitelisting and sorting proper nouns via `whitelist_typos.py`.
   - Search relevant GitHub issues using the `gh` CLI (if available) and perform a conventional git commit.
