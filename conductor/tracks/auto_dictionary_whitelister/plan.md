# Implementation Plan - Auto-Dictionary Whitelister Script

## Phase 1: Implementation & Validation

- [x] Task: Create `scripts/whitelist_typos.py` (78fe480)
    - [x] Implement CLI argument parsing for list of words.
    - [x] Implement appending, sorting (`sort -u`), and saving logic for `dictionary.txt`.
    - [x] Trigger execution of `scripts/generate_typos_config.py` programmatically or via subprocess.
- [x] Task: Write Tests (78fe480)
    - [x] Add unit tests verifying words are correctly inserted, deduplicated, sorted, and config is regenerated.
- [x] Task: Update Scripts Registry (4b225d9)
    - [x] Document the script's usage in `scripts-registry.md`.
- [ ] Task: Conductor - User Manual Verification
