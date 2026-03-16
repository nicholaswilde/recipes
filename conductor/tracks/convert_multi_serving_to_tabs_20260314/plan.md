# Implementation Plan - Convert Multi-Serving Recipes to Zensical Tabs

This track converts identified recipes to use Content Tabs for their multiple ingredients sections.

## Phase 1: High Priority & Foundation
- [ ] Convert `docs/desserts/martha-stewarts-new-york-style-cheesecake.md` to use tabs (9 Inch vs 10 Inch)
- [ ] Convert `docs/ingredients/post-baking-glazes/royal-icing.md` to use tabs (Fresh vs Powdered Egg Whites)
- [ ] Establish a clear pattern/standard for tab implementation (e.g., indentation, header nesting)

## Phase 2: Breads & Breakfast
- [ ] Convert identified recipes in `docs/breads/` (30 files)
- [ ] Convert identified recipes in `docs/breakfast/` (11 files)

## Phase 3: Cookies, Bars & Desserts
- [ ] Convert identified recipes in `docs/cookies-and-bars/` (18 files)
- [ ] Convert identified recipes in `docs/desserts/` (36 files)

## Phase 4: Main, Lunches & Others
- [ ] Convert identified recipes in `docs/main/`, `docs/lunches/`, `docs/ingredients/`
- [ ] Convert identified recipes in `docs/sides/` and `docs/soups-and-stews/`

## Phase 5: Verification & Cleanup
- [ ] Run `zensical build` and verify all converted pages render correctly.
- [ ] Perform a final scan to ensure no recipes with multiple "Ingredients" headers were missed.
