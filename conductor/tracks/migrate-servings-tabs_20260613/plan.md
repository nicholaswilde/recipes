# Implementation Plan - Migrate Recipe Servings to Tabs

## Phase 1: Migration of Candidate Recipes

- [x] Task: Migrate `sides/grains-and-legumes/couscous.md` to Zensical tabs [72620c3]
    - [x] Convert ingredients to "Serves 4", "Serves 6", and "Serves 8" tabs and remove second servings table
    - [x] Verify that all units and ingredients map correctly to the ratios in the servings table
    - [x] Check for reference-style links inside the tabs and convert them to inline links if needed
- [x] Task: Migrate `sides/grains-and-legumes/quinoa.md` to Zensical tabs [c9362f6]
    - [x] Convert ingredients to "Serves 4", "Serves 6", and "Serves 8" tabs and remove second servings table
    - [x] Verify that all units and ingredients map correctly to the ratios in the servings table
    - [x] Check for reference-style links inside the tabs and convert them to inline links if needed
- [x] Task: Quality Assurance and Verification
    - [x] Run `rumdl check` on `couscous.md` and `quinoa.md`
    - [x] Run `task lint` and `task validate` to check configurations
    - [x] Run `zensical build` to ensure static site compiles successfully
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Migration of Candidate Recipes' (Protocol in workflow.md)
