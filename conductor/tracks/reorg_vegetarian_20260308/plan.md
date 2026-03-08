# Implementation Plan: Reorganize Vegetarian Category

## Steps
1. **Audit Recipes:** List all recipes in `cook/vegetarian` and determine their functional target (e.g., `main`, `sides`).
2. **Batch Move:** Move `.cook` and image files.
3. **Update Metadata:** Update the `.cook` files with the `vegetarian` tag.
4. **Update Navigation:** Update the `[[project.nav]]` section in `zensical.toml`.
5. **Validation:** Run `task spellcheck` and verify the build.

## Target Mapping (Initial Proposal)
- `Black Bean Burgers` -> `main`
- `California Veggie Wraps` -> `lunches`
- `Cauliflower Green Bean Mac & Cheese` -> `main`
- ... (and so on)
