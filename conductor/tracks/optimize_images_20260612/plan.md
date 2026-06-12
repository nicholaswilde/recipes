# Implementation Plan: Image Optimization and WebP Conversion

## Phase 1: Script Development and Testing
- [ ] Task: Create a mock image test suite or validation checklist for the image optimization script
    - [ ] Create a test directory with dummy `.jpg` and `.png` files to test compression and format conversion
- [ ] Task: Implement image optimization and conversion script
    - [ ] Create `scripts/optimize-images.sh` to check for dependencies (`cwebp`, `oxipng`)
    - [ ] Implement JPEG to WebP conversion with `cwebp -q 80 -metadata all` and delete original JPEG
    - [ ] Implement PNG optimization with `oxipng -o 4 --strip safe`
    - [ ] Implement calculation and reporting of total space savings (bytes and percentage)
- [ ] Task: Test script on dummy directory
    - [ ] Execute `scripts/optimize-images.sh` on the test directory and verify format conversion and optimization results
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Script Development and Testing' (Protocol in workflow.md)

## Phase 2: Migration Execution and Markdown Updates
- [ ] Task: Add markdown reference update logic
    - [ ] Add regex/sed replacements in `scripts/optimize-images.sh` to find all `.jpg` image references in `docs/` markdown files and change them to `.webp`
- [ ] Task: Run migration on repository assets
    - [ ] Run `scripts/optimize-images.sh` on `docs/assets/images/` and record the space savings
- [ ] Task: Verify links and repository integrity
    - [ ] Run `task linkcheck-offline` to ensure no broken image links exist
    - [ ] Run `task lint` and `task validate` to verify overall project health
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Migration Execution and Markdown Updates' (Protocol in workflow.md)

## Phase 3: Workflow Integration
- [ ] Task: Update the recipe move workflow
    - [ ] Update `scripts/move.sh` to convert `.jpg` files to `.webp` using `cwebp` after copying, and optimize `.png` files using `oxipng`
    - [ ] Update `scripts/move.sh` to find and replace `.jpg` image links with `.webp` in the newly generated markdown file
- [ ] Task: Validate integration with a mock recipe
    - [ ] Run a test import/move using a mock `.cook` file and `.jpg` image to verify automated WebP conversion and Markdown updating
    - [ ] Run `git diff` on the test output to verify correctness
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Workflow Integration' (Protocol in workflow.md)
