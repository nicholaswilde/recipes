# Specification: Standardize Cuisines to Meal Types

## Objective
Merge cuisine-based folders (`mexican`, `italian`, `asian`) into the functional meal-type hierarchy (`main`, `sides`, `soups-and-stews`, etc.) and use tags for cuisine identification.

## Rationale
Using both cuisines and meal types for folders causes "search friction" (e.g., should Mexican breakfast go in `mexican` or `breakfast`?). Standardizing on functional folders with tags provides a more consistent experience.

## Scope
- `cook/mexican/` (29 recipes)
- `cook/italian/` (40 recipes)
- `cook/asian/` (13 recipes)

## Requirements
1. Identify the functional category for each recipe in `cook/mexican`, `cook/italian`, and `cook/asian`.
2. Move `.cook` and image files to their target functional folders.
3. Add cuisine tags (e.g., `mexican`, `italian`, `asian`) to the `.cook` files.
4. Update `zensical.toml` to reflect the new locations.
5. Verify site build.
