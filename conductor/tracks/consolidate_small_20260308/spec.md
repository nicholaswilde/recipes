# Specification: Consolidate Small/Overlapping Categories

## Objective
Merge small categories (`indonesian`, `dutch`, `custards`, `tarts`, `pressurecooker`) into broader, more established categories.

## Rationale
Some folders contain only a few recipes, which creates unnecessary depth in the navigation and makes the project structure feel fragmented. Consolidating these improves discoverability and simplifies maintenance.

## Scope
- `cook/indonesian/` (5 recipes) -> `cook/asian/`
- `cook/dutch/` (1 recipe) -> `cook/sides/` or `cook/main/`
- `cook/custards/` (4 recipes) & `cook/tarts/` (3 recipes) -> `cook/desserts/`
- `cook/pressurecooker/` (5 recipes) -> `cook/ingredients/` or `cook/sides/` + `pressure-cooker` tag.

## Requirements
1. Move `.cook` and image files to their new parent folders.
2. Update `zensical.toml` to reflect the new navigation.
3. For `pressurecooker` recipes, add `>> tags: pressure-cooker`.
4. Update Markdown paths in `docs/`.
5. Verify site build.
