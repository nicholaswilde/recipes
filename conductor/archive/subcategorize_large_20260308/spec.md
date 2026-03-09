# Specification: Sub-categorize Large Folders

## Objective
Divide the oversized `sides` (112 recipes) and `sauces-and-dressings` (118 recipes) folders into more manageable sub-categories.

## Rationale
Large folders make navigation difficult for users as they have to scroll through dozens of unrelated recipes. Sub-categorizing these by type (e.g., `potatoes`, `salads`, `vinaigrettes`, `dips`) will improve searchability and structure.

## Scope
- `cook/sides/` (112 recipes)
- `cook/sauces-and-dressings/` (118 recipes)

## Requirements
1. Determine appropriate sub-categories for both folders.
2. Create sub-folders and move `.cook` and image files.
3. Update `zensical.toml` with the new hierarchical navigation.
4. Update `docs/` Markdown paths.
5. Verify site build.

## Proposed Sub-categories
- **Sides:** `potatoes`, `vegetables`, `grains-and-legumes`, `salads`, `snacks`.
- **Sauces & Dressings:** `mother-sauces`, `vinaigrettes`, `salsas`, `dips-and-spreads`, `sweet-sauces`.
