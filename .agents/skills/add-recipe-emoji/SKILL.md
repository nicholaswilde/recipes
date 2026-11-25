---
name: add-recipe-emoji
description: >-
  Add emoji shortcodes from includes/emoji.yaml to a recipe markdown file's H1 title, ingredients, and cookware sections. Trigger: /add-recipe-emoji, 'add recipe emoji', 'add emoji to recipe', 'add emojis'.
---

# Add Recipe Emoji

Add missing `:shortcode:` emoji prefixes to a recipe's Markdown file (`docs/**/*.md`) across the
H1 title, `## :salt: Ingredients`, and `## :cooking: Cookware` sections using `includes/emoji.yaml`.

## Protocol

1. **Locate & Inspect Recipe**:

   Find the target Markdown file (and corresponding `.cook` file if present):

   ```bash
   rtk fd -i "<recipe-slug-or-name>" docs/ cook/
   ```

   Read the Markdown file and check for missing `:shortcode:` prefixes in:
   - The H1 title (`# :<shortcode>: <Title>`)
   - Every list item under `## :salt: Ingredients` (including items inside `=== "Tab"` blocks)
   - Every list item under `## :cooking: Cookware`

2. **Look Up & Choose Shortcodes**:

   - Always use text shortcodes (`:shortcode:`) from `includes/emoji.yaml` — never paste raw Unicode
     emoji characters.
   - Check available shortcodes and existing recipe conventions:

     ```bash
     task emoji-ing
     task emoji-cw
     rtk rg -i "<ingredient>" docs/
     ```

   - Inspect unmapped items or suggestions from `cook-docs` / repo scripts:

     ```bash
     cook-docs doctor --only emojis "<cook/path/to/Recipe.cook>"
     rtk uv run scripts/check_header_emojis.py "<docs/path/to/recipe.md>"
     rtk uv run scripts/check_recipe_emojis.py "<cook/path/to/Recipe.cook>"
     ```

     > **Note:** Review `check_recipe_emojis.py` output carefully — `includes/emoji.yaml` contains
     > legacy fallback mappings (e.g., `:apple:` for beans/olives, `:bread:` for pasta). Prefer the
     > accurate shortcode from `includes/emoji.yaml` and existing recipes (e.g., `:olive:`, `:beans:`,
     > `:cheese_wedge:`, `:bell_pepper:`, `:spaghetti:`, `:bowl_with_spoon:`, `:salt:`).

3. **Apply Emojis (Prefer `cook-docs` Re-Compile)**:

   - **`.cook`-backed non-tabbed recipes**: Add any missing ingredient/cookware mappings to
     `includes/emoji.yaml` (run `task emoji-sort`) or title/category rules to `.cookdocs.toml`
     (`[emoji.titles]` / `[emoji.categories]`), then re-compile with `cook-docs` (`merge = true`
     preserves manual notes, admonitions, and tabs):

     ```bash
     cook-docs "<cook/path/to/Recipe.cook>"
     ```

   - **Markdown-only or tabbed recipes** (where `cook-docs --merge` preserves manual `=== "Tab"`
     blocks): Edit the Markdown directly:
     - **Title**: `# :<shortcode>: <Recipe Title>`
     - **Ingredients**: `- :<shortcode>: <quantity> <unit> <ingredient>` (emoji precedes measurement;
       preserve 4-space indentation inside `=== "Tab"` blocks)
     - **Cookware**: `- :<shortcode>: <quantity> <cookware>`
   - Do not add emoji shortcodes to `.cook` source files.

4. **Verify**:

   Run header emoji check, markdown lint, and targeted spellcheck:

   ```bash
   rtk uv run scripts/check_header_emojis.py "<docs/path/to/recipe.md>"
   rtk rumdl check "<docs/path/to/recipe.md>"
   task spellcheck-file FILE="<docs/path/to/recipe.md>"
   ```
