---
name: add-ingredient-weight
description: >-
  Add a volume-to-weight conversion entry for an ingredient to docs/reference/measuring.md in sorted order and verify table integrity. Trigger: /add-ingredient-weight, 'add ingredient weight', 'add measuring weight', 'add volume to weight'.
---

# Add Ingredient Weight

Add or update a volume-to-weight conversion row in `docs/reference/measuring.md` under
`## :scales: Ingredient Weight Chart`.

## Protocol

1. **Check Existing Entries**:

   Search `docs/reference/measuring.md` for the ingredient or synonyms:

    ```bash
    rtk rg -i "<ingredient>" docs/reference/measuring.md
    ```

    - If an identical entry exists, confirm weight matches and skip duplicate insertion.
    - If preparation differs (e.g. `chopped` vs `sliced`), keep distinct entries or update the target row as requested.

2. **Determine Standard Weight & Formatting**:

    - Use the user-provided volume/gram weight, or verify against the King Arthur Baking Ingredient Weight Chart
      (`<https://www.kingarthurbaking.com/learn/ingredient-weight-chart>`) or USDA data when unspecified.
    - Format the row to match the 4-column table schema:

      ```markdown
      | <Ingredient> | <Volume> | <Grams> | <Ounces> |
      ```

    - Use `Ingredient (prep)` style when preparation matters (e.g. `Green onions (chopped)`).
    - Compute `<Ounces>` from `<Grams>` (`grams / 28.3495`), rounded to standard fractional ounces used in the table
      (e.g. `1-1/2`, `2-1/4`, `3-1/2`, `4`, or `-` for tiny tsp amounts).

3. **Insert in Alphabetical Order**:

    - Insert the row in case-insensitive alphabetical order by the first column inside
      `## :scales: Ingredient Weight Chart` in `docs/reference/measuring.md`.
    - Maintain strict sorting; `scripts/sync_weights_yaml.py` and `scripts/test_measuring_table.py` depend on
      table structure and order.

4. **Sync `includes/weights.yaml` & Verify**:

   Regenerate `includes/weights.yaml` for `cook-docs` and run table sort tests, YAML/Markdown lint, and spellcheck:

    ```bash
    task sync-weights
    rtk uv run python3 scripts/test_measuring_table.py
    rtk typos --format brief docs/reference/measuring.md
    rtk rumdl check docs/reference/measuring.md
    yamllint-rs includes/weights.yaml
    ```
