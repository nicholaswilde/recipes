# Adjust Recipe Metadata

This skill automates the adjustment of recipe metadata, tags, and frontmatter.

## Description

This skill enables developers to add/remove tags and modify other frontmatter metadata keys (e.g., `comments`,
`hero`, etc.) dynamically on recipe markdown files.

## Protocol

1. **Invoke the script**:

   Run the `adjust_recipe_metadata.py` script:

   ```bash
   uv run python3 scripts/adjust_recipe_metadata.py <recipe_path> [options]
   ```

   **Available Options**:
   - `--add-tags <tag1,tag2,...>`: Add a comma-separated list of tags to the recipe.
   - `--remove-tags <tag1,tag2,...>`: Remove a comma-separated list of tags from the recipe.
   - `--set-metadata <key=value,key2=value2,...>`: Set comma-separated key=value metadata fields in the frontmatter.

   **Examples**:
   - Add tags `healthy` and `quick`:

     ```bash
     uv run python3 scripts/adjust_recipe_metadata.py docs/breakfast/overnight-oats.md --add-tags "healthy,quick"
     ```

   - Disable comments and update the hero image path:

     ```bash
     uv run python3 scripts/adjust_recipe_metadata.py docs/breakfast/overnight-oats.md --set-metadata "comments=false,hero=assets/images/new-hero.webp"
     ```

2. **Verify and Lint**:

   - Verify that the frontmatter in the updated file is formatted correctly.
   - Run `rumdl check <recipe_path>` to ensure markdownlint rules pass.
   - Run `task lint-changed` and `task validate`.
   - Run `task build` to ensure the site compiles correctly.

3. **Commit the changes**:

   Commit the changes following standard commit guidelines:

   ```bash
   git add <recipe_path>
   git commit -m "docs(recipes): Adjust metadata for <recipe_name>"
   ```
