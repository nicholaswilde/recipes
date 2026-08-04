# Implementation Plan - Convert Multi-Serving Recipes to Zensical Tabs

This track converts identified recipes to use Content Tabs for their multiple ingredients sections.

## Phase 1: High Priority & Foundation [checkpoint: ff2fa37]
- [x] Convert `docs/desserts/martha-stewarts-new-york-style-cheesecake.md` to use tabs (9 Inch vs 10 Inch) (d38acad)
- [x] Convert `docs/ingredients/post-baking-glazes/royal-icing.md` to use tabs (Fresh vs Powdered Egg Whites) (25aebc3)
- [x] Establish a clear pattern/standard for tab implementation (e.g., indentation, header nesting) (f8840e9)

## Phase 2: Breads & Breakfast [checkpoint: 2a0ba16]
- [x] Convert identified recipes in `docs/breads/` (30 files) (2a0ba16)
- [x] Convert identified recipes in `docs/breakfast/` (11 files) (2a0ba16)

## Phase 3: Cookies, Bars & Desserts [checkpoint: 0095e12]
- [x] Convert identified recipes in `docs/cookies-and-bars/` (18 files) (0095e12)
- [x] Convert identified recipes in `docs/desserts/` (36 files) (0095e12)

## Phase 4: Main, Lunches & Others [checkpoint: 6d649ef]
- [x] Convert identified recipes in `docs/main/`, `docs/lunches/`, `docs/ingredients/` (6d649ef)
- [x] Convert identified recipes in `docs/sides/` and `docs/soups-and-stews/` (6d649ef)

## Phase 5: Verification & Cleanup [checkpoint: fddcae4]
- [x] Run `zensical build` and verify all converted pages render correctly. (fddcae4)
- [x] Perform a final scan to ensure no recipes with multiple "Ingredients" headers were missed. (fddcae4)
