# Implementation Plan: Audit and Update Recipe Metadata

This plan outlines the steps to audit and update all existing recipes to comply with the project's Product Guidelines.

## Phase 1: Preparation and Inventory
Goal: Identify the scope of work and ensure tooling is ready.

- [x] Task: Create a comprehensive list of all recipes currently in the collection d0a543b
- [ ] Task: Audit `includes/emoji.yaml` to ensure common ingredients have mappings
- [ ] Task: Conductor - User Manual Verification 'Preparation and Inventory' (Protocol in workflow.md)

## Phase 2: Metadata and Image Audit
Goal: Ensure basic metadata and performance optimizations are in place.

- [ ] Task: Bulk audit Markdown front matter for missing `tags` or `source`
- [ ] Task: Ensure all recipe images in Markdown have `loading="lazy"` attribute
- [ ] Task: Conductor - User Manual Verification 'Metadata and Image Audit' (Protocol in workflow.md)

## Phase 3: Formatting and Emoji Standardization
Goal: Standardize units in `.cook` files and emojis in `.md` files.

- [ ] Task: Standardize units in `.cook` files (`Tbsp`, `tsp`)
- [ ] Task: Update Markdown ingredient lists to use emoji shortcodes from `includes/emoji.yaml`
- [ ] Task: Conductor - User Manual Verification 'Formatting and Emoji Standardization' (Protocol in workflow.md)

## Phase 4: Volumetric to Weight Conversions
Goal: Add gram conversions to all recipes.

- [ ] Task: Identify recipes requiring gram conversions (focusing on baking and major staples)
- [ ] Task: Add gram conversions to Markdown files using `docs/reference/measuring.md`
- [ ] Task: Update `docs/reference/measuring.md` if new conversions are found during the process
- [ ] Task: Conductor - User Manual Verification 'Volumetric to Weight Conversions' (Protocol in workflow.md)

## Phase 5: Final Validation and Cleanup
Goal: Ensure the entire collection passes all quality gates.

- [ ] Task: Run project-wide linting (`task lint`)
- [ ] Task: Run project-wide spellcheck (`task spellcheck`)
- [ ] Task: Run project-wide link check (`task linkcheck`)
- [ ] Task: Verify the full site build (`task docs:build`)
- [ ] Task: Conductor - User Manual Verification 'Final Validation and Cleanup' (Protocol in workflow.md)
