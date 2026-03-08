# Product Guidelines

## Prose Style and Tone

- **Voice:** Casual, friendly, and encouraging.
- **Clarity:** While the tone is personal, instructions must remain clear and unambiguous.
- **Narrative:** Briefly sharing the "why" or a small personal anecdote in the front matter or comments section is encouraged to maintain the personal feel of the collection.

## Visual Identity

- **Primary Imagery:** Every recipe should ideally feature a high-quality, appetizing photograph of the finished dish.
- **Placeholders:** If a custom photograph is unavailable, use clean, relevant placeholders (e.g., generated via the Recipes MCP server or similar tools).
- **Optimization:** All images must include `loading="lazy"` to ensure optimal performance.

## Content Formatting

- **Instructions:** Always use numbered steps. Each step should focus on a concise set of actions.
- **Ingredients:** Prefix each ingredient with its corresponding emoji shortcode from `includes/emoji.yaml`.
- **Measurements:**
    - Use standard unit abbreviations (e.g., `Tbsp` for tablespoon, `tsp` for teaspoon).
    - Provide volumetric to weight conversions (grams) in parentheses for major ingredients (e.g., `2 cups (240 g) all-purpose flour`).
- **Callouts:** Use `!!! tip` for additional advice, variations, or "pro-tips" that enhance the recipe.
- **Metadata:** Every recipe must include relevant tags and source information in the front matter.

## Technical Standards

- **Linting:** Adhere to `markdownlint` and `yamllint` configurations.
- **Spelling:** All content must pass the project's spellcheck process.
- **Links:** Verify all external links using the link-check tool.

## Cooklang Specification

Recipes in this project are written using the [Cooklang](https://cooklang.org/docs/spec/) specification. Here is a quick reference for creating `.cook` files:

- **Metadata:** Defined at the top of the file using `>> key: value`. Common keys include `source`, `serves`, `total time`, `time required`, `image`, and `tags`.

    ```cook
    >> source: https://example.com/recipe
    >> serves: 4
    >> total time: 30 minutes
    ```

- **Ingredients:** Use `@` followed by the ingredient name. If there is a quantity, use `{}`.
    - Simple: `@salt{}`
    - With quantity: `@water{1%cup}`
    - With quantity (no unit): `@eggs{2}`
    - Multi-word ingredient: `@ground beef{1%lb}`
- **Cookware:** Use `#` followed by the cookware name.
    - Simple: `#pan{}`
    - Multi-word: `#frying pan{}`
- **Timer:** Use `~` followed by the duration in `{}`.
    - Example: `~{25%minutes}`
- **Comments:** Use `[-` and `-]` for block comments or `--` for line comments.
    - Example: `[- This is a comment -]`
- **Steps:** Write instructions as natural text. Ingredients, cookware, and timers are embedded directly within the sentences.
