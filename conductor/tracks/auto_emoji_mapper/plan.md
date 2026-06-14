# Implementation Plan - Auto-Emoji Mapper Script Option

## Phase 1: Implementation & Validation

- [ ] Task: Update `scripts/check-recipe-emojis.py` with `--fix` Flag
    - [ ] Implement command line argument parsing for `--fix`.
    - [ ] Implement similarity checking against mapped items in `includes/emoji.yaml`.
    - [ ] Implement YAML writing logic to insert new items under matched emoji keys.
- [ ] Task: Write Tests
    - [ ] Add unit tests verifying auto-mapping accuracy and YAML integrity after rewrite.
- [ ] Task: Update Scripts Registry
    - [ ] Update `scripts-registry.md` to document the new `--fix` flag.
- [ ] Task: Conductor - User Manual Verification
