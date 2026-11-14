---
name: check-ingredient-weight
description: >-
  Look up and calculate the weight in grams of an ingredient for a given volume (defaulting to 1 cup or table reference volume) using docs/reference/measuring.md. Trigger: /check-ingredient-weight, 'check ingredient weight', 'ingredient weight', 'how many grams'.
---

# Check Ingredient Weight

Look up or compute the weight in grams for an ingredient at a specified volume, defaulting to a standard reference
volume (`1 cup`) when no volume is provided.

## Protocol

1. **Parse Ingredient and Volume**:

   Extract the target `<ingredient>` and optional `<qty> <unit>` (e.g., `2 cups`, `0.33 cup`, `2 Tbsp`).

    - If no volume is provided, default to `1 cup` (and report the chart's native reference volume if listed in
      another unit such as `1/2 cup` or `1 Tbsp`).

2. **Query `docs/reference/measuring.md`**:

   Search the Ingredient Weight Chart for the ingredient or synonyms:

    ```bash
    rtk rg -i "<ingredient>" docs/reference/measuring.md
    ```

    - Select the exact matching row (distinguishing prep/form, e.g. `grated cheddar` vs `cheddar cheese powder`,
      `Green onions (chopped)` vs `Scallions (sliced)`).
    - Scale the matched row's grams proportionally to the requested volume (`1 cup = 16 Tbsp = 48 tsp = 8 fl oz`),
      rounding to the nearest whole gram. (Avoid blind fuzzy matching via `find_best_key`, which can match wrong
      variants like cheese powder or dried onion.)

3. **Fallback Lookup When Missing**:

    - If no matching entry exists in `docs/reference/measuring.md`, check the King Arthur Baking Ingredient Weight Chart
      (`<https://www.kingarthurbaking.com/learn/ingredient-weight-chart>`), USDA reference data, or the `recipes` MCP
      `convert_ingredients` tool.
    - Clearly cite the external source and offer to record the conversion in `docs/reference/measuring.md` via
      `add-ingredient-weight`.

4. **Report Result**:

   Return `<volume> <ingredient> = <grams> g` along with the matched reference row or external source.
