# /recipe-tab-conversion

Convert recipe ingredients and/or instructions sections containing multiple components, serving sizes,
or alternative options to use Zensical Content Tabs.

## Description

This skill converts recipes with multiple ingredients headers (e.g., Bread and Glaze, or 9 Inch and 10 Inch)
to use content tabs powered by `pymdownx.tabbed`. This saves vertical layout space and ensures a clean,
responsive presentation.

## Protocol

1. **Identify Multi-Serving/Multi-Component Recipes**:
   - Locate recipes with multiple ingredients headers (e.g. `## :salt: Ingredients - Dough`, `## :salt: Ingredients - Glaze`):

     ```bash
     uv run scripts/identify_multi_serving.py
     ```

2. **Run Automated Tab Conversion**:
   - Convert a single recipe file's ingredients to tabs:

     ```bash
     uv run python3 scripts/convert_file.py docs/path/to/recipe.md
     ```

   - Alternatively, batch convert all recipes in a specific category:

     ```bash
     uv run python3 scripts/batch_convert.py <category_filter>
     ```

3. **Verify Compliance with style guide**:
   - Open the recipe file and verify the tabbed ingredients section:
     - The syntax is `=== "Tab Label"` with 4-space indentation for content.
     - Tab labels are concise and capitalized (e.g. `"Bread"` or `"Glaze"`, or `"9 Inch"` or `"10 Inch"`).
     - Nested headers (if any) are `###` (H3) and indented by 4 spaces.
     - If the recipe has matching multi-section instructions, they should also use matching tabs
       (e.g. `=== "Fresh Egg Whites"` and `=== "Powdered Egg Whites"` under both ingredients and instructions).
     - Refer to [Markdown Style Guide](../../conductor/code_styleguides/markdown.md) for full formatting rules.

4. **Lint and Validate**:
   - Verify that the modified recipe compiles and passes all checks:

     ```bash
     task lint-changed
     task build
     ```

5. **Commit and Push**:
   - Commit the changes and push to origin:

     ```bash
     git add docs/path/to/recipe.md
     git commit -m "docs(recipes): Convert <Recipe Name> to use content tabs"
     git push
     ```
