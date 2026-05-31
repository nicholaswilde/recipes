# /import-recipe `args`

Import a recipe from a URL or a GitHub issue number.

## Description

This skill imports a recipe from a specified source (a URL or a GitHub issue number) into the project's
repository following the established recipe import workflow.

## Protocol

1. **Parse Arguments:**
   - The command takes one argument: `args`.
   - If `args` is a URL, fetch the recipe from that URL.
   - If `args` is a number (e.g., `#123` or `123`), treat it as a GitHub issue number in this repository and
     fetch/read its content.
2. **Extract Data:**
   - Extract the recipe title, ingredients, and instructions from the source.
   - **Image/PDF Sources:** If the recipe is provided via an image or PDF (e.g., in a GitHub issue via an image
     or file link), download the file and use the `liteparse` skill (`lit parse <file_path>`) to extract the text.
     Use the extracted text to create the recipe.
3. **Create .cook File:**
   - Determine the correct category (e.g., `asian`, `beverages`, `breakfast`, etc.) based on the recipe content.
   - Create `cook/{category}/{Recipe Name}.cook`.
   - Use only the name for the title (e.g., `Paprikash`). If it exists, append the author.
   - Units: Use `Tbsp` for tablespoons and `tsp` for teaspoons.
   - Time Ranges: Format as `shortest to ~{longest%unit}` (e.g., `7 to ~{8%minutes}`).
   - Check `cook/config/ignored_ingredients.yaml` before tagging ingredients with `@`.
4. **Handle Image:**
   - Download the image from the source or use a placeholder if unavailable.
   - Name it `{Recipe Name}.jpg` and place it in the same directory as the `.cook` file.
5. **Run Move Task:**
   - Execute `FILES=cook/{category}/{Recipe Name}.cook task move`.
   - This converts the `.cook` file to Markdown and generates a `zensical.toml` mapping.
6. **Update zensical.toml:**
   - Insert the generated mapping entry into the correct category section of `zensical.toml`.
7. **Post-Process Markdown:**
   - Locate the generated Markdown file in `docs/{category}/{Recipe Name}.md`.
   - **Emojis:** Add emoji shortcodes from `includes/emoji.yaml` to each ingredient. Update `includes/emoji.yaml`
     if an emoji is missing.
   - **Tags:** Add relevant tags to the front matter.
   - **Conversions:** Convert volumetric measurements to grams (e.g., `2 cups (240 g)`) using
     `docs/reference/measuring.md`. Reference the King Arthur Baking chart if missing, and update
     `docs/reference/measuring.md`.
   - **Additional References:** If there is a "Pancake Princess" link in the source issue, include that link as
     an additional reference in the `## :link: Source` section of the Markdown recipe page.
