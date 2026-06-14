# Implementation Plan - Auto-Emoji Mapper Script Option

## Phase 1: Implementation & Validation

- [x] Task: Update `scripts/check-recipe-emojis.py` with `--fix` Flag (3091df5)
    - [x] Implement command line argument parsing for `--fix`.
    - [x] Implement similarity checking against mapped items in `includes/emoji.yaml`.
    - [x] Implement YAML writing logic to insert new items under matched emoji keys.
- [x] Task: Write Tests (3091df5)
    - [x] Add unit tests verifying auto-mapping accuracy and YAML integrity after rewrite.
- [x] Task: Update Scripts Registry (3091df5)
    - [x] Update `scripts-registry.md` to document the new `--fix` flag.
- [x] Task: Conductor - User Manual Verification (3091df5)

