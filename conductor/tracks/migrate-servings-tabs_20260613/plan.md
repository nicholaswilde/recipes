# Implementation Plan - Migrate Recipe Servings to Tabs

## Phase 1: Migration of Candidate Recipes

- [x] Task: Migrate `sides/grains-and-legumes/couscous.md` to Zensical tabs [72620c3]
    - [x] Modify `couscous.md` to remove the second servings table and place the ingredient lists under `=== "Serves 4"`, `=== "Serves 6"`, and `=== "Serves 8"` tabs
    - [x] Verify that all units and ingredients map correctly to the ratios in the servings table
    - [x] Check for reference-style links inside the tabs and convert them to inline links if needed
- [x] Task: Migrate `sides/grains-and-legumes/quinoa.md` to Zensical tabs [c9362f6]
    - [x] Modify `quinoa.md` to remove the second servings table and place the ingredient lists under `=== "Serves 4"`, `=== "Serves 6"`, and `=== "Serves 8"` tabs
    - [x] Verify that all units and ingredients map correctly to the ratios in the servings table
    - [x] Check for reference-style links inside the tabs and convert them to inline links if needed
- [ ] Task: Quality Assurance and Verification
    - [ ] Run `rumdl check` on `couscous.md` and `quinoa.md`
    - [ ] Run `task lint` and `task validate` to check configurations
    - [ ] Run `zensical build` to ensure static site compiles successfully
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Migration of Candidate Recipes' (Protocol in workflow.md)

