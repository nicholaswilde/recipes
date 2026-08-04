# Specification - Migrate Recipe Servings to Tabs

## Overview
This specification details the migration of recipes with multiple serving sizes or batches (currently formatted as tables or multiple recipe lists) to use Zensical Content Tabs with `Serves <X>` as the tab name. This will make the recipe site more interactive and easier to read.

## Functional Requirements
1. Scan the recipe markdown files in `docs/` for recipes that have multiple serving sizes or batch sizes.
2. For each identified recipe (such as `sides/grains-and-legumes/couscous.md` and `sides/grains-and-legumes/quinoa.md`), convert the ingredients list into Zensical content tabs.
3. The tab names must be `Serves <X>` (capitalized, e.g., `Serves 4`, `Serves 6`, `Serves 8`) where `<X>` matches the serving size.
4. Calculate and generate the ingredients lists for each tab:
   - For `couscous.md`:
     - `Serves 4`: 1 cup (180 g) couscous, 1 cup (227 g) broth/water, 2 Tbsp olive oil, etc.
     - `Serves 6`: 1.5 cups (270 g) couscous, 1.5 cups (340 g) broth/water, 3 Tbsp olive oil, etc.
     - `Serves 8`: 2 cups (360 g) couscous, 2 cups (454 g) broth/water, 4 Tbsp olive oil, etc.
   - For `quinoa.md`:
     - `Serves 4`: 1 cup (133 g) quinoa, 1.25 cups (300 g) broth/water, etc.
     - `Serves 6`: 1.5 cups (200 g) quinoa, 1.9 cups (450 g) broth/water, etc.
     - `Serves 8`: 2 cups (267 g) quinoa, 2.5 cups (600 g) broth/water, etc.
5. Format the tab blocks using `=== "Serves <X>"` syntax and 4-space indentation for the list content.
6. If any reference-style links are used inside the tabs, convert them to inline links to ensure compatibility with markdownlint.
7. Verify and lint all modified recipe files using `rumdl check` or similar linter, and ensure the site builds correctly.

## Non-Functional Requirements
- Ensure that the generated tabs render correctly in Zensical static site.
- Keep the git commits clean and follow the conventional commit format.

## Acceptance Criteria
- Recipes `sides/grains-and-legumes/couscous.md` and `sides/grains-and-legumes/quinoa.md` are migrated to use Zensical content tabs for different serves.
- The tab names are `Serves 4`, `Serves 6`, `Serves 8` respectively.
- All ingredient volumes and weights match the values in the serving table.
- The project compiles successfully and tests/linters pass without errors.

## Out of Scope
- Automated volumetric-to-gram conversion of other ingredients not specified in the serves tables.
- Adjusting instructions unless serving-specific steps are required.

