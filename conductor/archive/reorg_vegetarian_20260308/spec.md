# Specification: Reorganize Vegetarian Category

## Objective
Move recipes from the `cook/vegetarian` folder to their respective functional folders (e.g., `cook/main`, `cook/sides`, `cook/soups-and-stews`) and add a `vegetarian` tag to their metadata.

## Rationale
The current structure mixes dietary choices with dish types, leading to navigation friction and inconsistent categorization. By using tags for dietary information, recipes can be categorized by their primary dish type while still being filterable by diet.

## Scope
- All recipes in `cook/vegetarian/`
- Navigation in `zensical.toml`
- Markdown files in `docs/vegetarian/`

## Requirements
1. Identify the functional category for each recipe in `cook/vegetarian`.
2. Move `.cook` files to the appropriate target folder.
3. Move corresponding images (`.jpg`, `.png`).
4. Add `>> tags: vegetarian` (or append to existing tags) in the `.cook` files.
5. Update `zensical.toml` to reflect the new locations.
6. Verify Markdown generation and site build.
