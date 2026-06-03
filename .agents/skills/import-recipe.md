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
   - Execute `FILES="cook/{category}/{Recipe Name}.cook" task move`.
   - This converts the `.cook` file to Markdown, copies/converts the recipe image, runs the `lychee` link checker, and automatically inserts the navigation mapping entry into the correct category section of `zensical.toml` in alphabetical order using the `add-recipe-nav.py` script.
6. **Post-Process Markdown:**
   - Locate the generated Markdown file in `docs/{category}/{Recipe Name}.md`.
   - **Emojis:** Run `python3 scripts/check-recipe-emojis.py "cook/{category}/{Recipe Name}.cook"` to verify that all ingredients and cookware are mapped in `includes/emoji.yaml`. Add emoji shortcodes from `includes/emoji.yaml` to each ingredient. Update `includes/emoji.yaml` if any emojis are reported missing.
   - **Tags:** Add relevant tags to the front matter.
   - **Conversions:** Run `python3 scripts/convert-recipe-units.py "docs/{category}/{recipe-name-slug}.md"` to automatically convert volumetric measurements to grams and add emojis using the data from `docs/reference/measuring.md` and `includes/emoji.yaml`. Update `docs/reference/measuring.md` if any conversions are missing or incorrect.
   - **Additional References:** If there is a "Pancake Princess" link in the source issue, include that link as
     an additional reference in the `## :link: Source` section of the Markdown recipe page.
7. **Spellcheck and Whitelist:**
    - Run the focused spellcheck on the newly generated Markdown recipe file:
      ```bash
      task spellcheck-file FILE="docs/{category}/{recipe-name-slug}.md"
      ```
    - If any valid new words (e.g. proper nouns, technical cooking terms, or unique ingredient names) are flagged as typos by the spellchecker:
      - Append them to the end of `dictionary.txt` in the root directory.
      - Run the sort task (`task sort`) to clean and organize the dictionary.
      - Re-run `task spellcheck-file` to automatically regenerate the `_typos.toml` configuration and verify that the file is clean.

## GitHub CLI (`gh`) Guidelines

When using the GitHub CLI (`gh`) to view issues, check workflow runs, or run other commands inside sandbox or non-interactive terminals, always disable the interactive pager by piping the output to `cat` (e.g., `gh run list --limit 5 | cat` or `gh issue view 1253 | cat`). This prevents the command from hanging or warning about a non-functional terminal.
