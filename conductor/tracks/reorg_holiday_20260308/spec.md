# Specification: Reorganize Holiday Category

## Objective
Move recipes from the `cook/holiday` folder to functional folders and use tags for organization.

## Rationale
The `holiday` folder is a "catch-all" category containing various dish types (mains, sides, desserts). Moving them to their functional folders while using tags like `holiday`, `thanksgiving`, or `christmas` allows them to be found both for special occasions and regular meal planning.

## Scope
- `cook/holiday/` (51 recipes)

## Requirements
1. Identify the functional category for each holiday recipe (e.g., `main`, `sides`, `desserts`).
2. Move `.cook` and image files.
3. Add relevant tags (e.g., `holiday`, `thanksgiving`, `christmas`).
4. Update `zensical.toml` to reflect the new locations.
5. Verify site build.
