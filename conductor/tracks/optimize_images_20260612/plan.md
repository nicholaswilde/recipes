# Implementation Plan: Image Optimization and WebP Conversion

## Phase 1: Script Development and Testing [checkpoint: 5cb0001]
- [x] Task: Create a mock image test suite or validation checklist for the image optimization script (99d9d50)
    - [x] Create a test directory with dummy `.jpg` and `.png` files to test compression and format conversion (99d9d50)
- [x] Task: Implement image optimization and conversion script (f793958)
    - [x] Create `scripts/optimize-images.sh` to check for dependencies (`cwebp`, `oxipng`) (f793958)
    - [x] Implement optional category parameter parsing and category-specific directory/file filtering (f793958)
    - [x] Implement JPEG to WebP conversion with `cwebp -q 80 -metadata all` and delete original JPEG (f793958)
    - [x] Implement PNG optimization with `oxipng -o 4 --strip safe` (f793958)
    - [x] Implement calculation and reporting of total space savings (bytes and percentage) for the current run (f793958)
- [x] Task: Test script on dummy directory (274ce78)
    - [x] Execute `scripts/optimize-images.sh` on the test directory and verify format conversion and optimization results (274ce78)
    - [x] Test specifying a category and verify only that category's images and markdown references are affected (274ce78)
- [x] Task: Conductor - User Manual Verification 'Phase 1: Script Development and Testing' (Protocol in workflow.md) (5cb0001)

## Phase 2: Migration Execution and Markdown Updates
- [x] Task: Add markdown reference update logic (bdb9a87)
    - [x] Add regex/sed replacements in `scripts/optimize-images.sh` to find all `.jpg` image references in target category markdown files and change them to `.webp` (bdb9a87)
- [~] Task: Run migration on repository assets in stages
    - [~] Execute `scripts/optimize-images.sh` for one category at a time (e.g. `lunches`, `breads`, `breakfast`, `desserts`, etc.)
    - [~] Verify image conversions and markdown reference changes stage-by-stage
    - [~] Execute `scripts/optimize-images.sh` with no arguments to catch any remaining images not covered in category stages
- [~] Task: Verify links and repository integrity
    - [~] Run `task linkcheck-offline` to ensure no broken image links exist
    - [~] Run `task lint` and `task validate` to verify overall project health
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Migration Execution and Markdown Updates' (Protocol in workflow.md)

## Phase 3: Workflow Integration
- [ ] Task: Update the recipe move workflow
    - [ ] Update `scripts/move.sh` to convert `.jpg` files to `.webp` using `cwebp` after copying, and optimize `.png` files using `oxipng`
    - [ ] Update `scripts/move.sh` to find and replace `.jpg` image links with `.webp` in the newly generated markdown file
- [ ] Task: Validate integration with a mock recipe
    - [ ] Run a test import/move using a mock `.cook` file and `.jpg` image to verify automated WebP conversion and Markdown updating
    - [ ] Run `git diff` on the test output to verify correctness
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Workflow Integration' (Protocol in workflow.md)
