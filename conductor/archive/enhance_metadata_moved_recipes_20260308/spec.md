# Specification: Enhance Metadata for Moved Recipes

## Objective
Add ingredient/cookware emojis and weight measurements (grams) to the 55 recipes recently moved from the vegetarian category.

## Rationale
Standardizing metadata across all recipes improves visual consistency and usability (especially for baking/precision cooking). Emojis help with quick ingredient identification, and weight measurements ensure accuracy.

## Scope
- 55 Markdown files in `docs/main/`, `docs/breakfast/`, `docs/lunches/`, `docs/sides/`, and `docs/tarts/` that were recently moved.

## Requirements
1.  **Emojis:** Add emoji shortcodes (e.g., `:salt:`) before each item in the "Ingredients" and "Cookware" sections.
2.  **Emoji Reference:** Use `includes/emoji.yaml`. If an item is missing, use best judgement and optionally update `emoji.yaml`.
3.  **Weights:** Add gram measurements in parentheses for volumetric quantities of major ingredients (e.g., `1 cup (240 g) all-purpose flour`).
4.  **Weight Reference:** Use `docs/reference/measuring.md` or King Arthur Baking chart.
5.  **Exceptions:** Skip gram conversions for small amounts of spices/seasonings (e.g., teaspoons).
6.  **Verification:** Run `zensical build` to ensure no broken links or linting errors.
