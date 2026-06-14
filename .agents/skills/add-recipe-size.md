# Add Recipe Size Tab

This skill automates adding additional serving sizes or batch sizes (e.g. half, double, or specific serves count)
to a recipe file by creating a new Zensical tab.

## Description

This skill converts plain ingredients lists to Zensical content tabs if they aren't already tabbed, and appends a
new scaled ingredients list as a new tab (e.g., `=== "Double"` or `=== "Half"`). It automatically parses the
original serving size from the metadata table at the top, removes the `Serves` column from that table, and
scales all quantities by the specified factor.

## Protocol

1. **Invoke the script**:

   Run the `add_recipe_size.py` script:

   ```bash
   uv run python3 scripts/add_recipe_size.py <recipe_path> <scale_factor> "<tab_name>"
   ```

   *Example*:
   To double the recipe in `docs/main/my-recipe.md` and add it as a "Double" tab:

   ```bash
   uv run python3 scripts/add_recipe_size.py docs/main/my-recipe.md 2 "Double"
   ```

2. **Verify and Lint**:

   - Check the modified file structure to ensure the tabs block is indented by exactly 4 spaces.
   - Run `rumdl check <recipe_path>` to ensure markdownlint rules pass.
   - Verify that the `Serves` column was removed from the top metadata table (leaving only `Total Time` or other
     columns) to avoid duplication.
   - Run `task lint-changed` and `task validate`.
   - Run `task build` to ensure the site compiles correctly.

3. **Commit the changes**:

   Commit the recipe and script changes following standard commit guidelines:

   ```bash
   git add <recipe_path>
   git commit -m "docs(recipes): Add <tab_name> size tab to <recipe_name>"
   ```
