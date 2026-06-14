# Specification - Auto-Dictionary Whitelister Script

## Overview
Develop a Python utility `scripts/whitelist_typos.py` that takes one or more words flagged as typos, appends them to `dictionary.txt`, automatically runs the alphabetical sorting command, and regenerates `_typos.toml` so the spellcheck configuration stays up-to-date in one step.

## Functional Requirements
1. **Inputs:** Accepts one or more words as CLI positional arguments.
2. **Insertion:**
   - Appends words to the end of `dictionary.txt`.
3. **Sorting:**
   - Runs sorting logic (`sort -u`) on `dictionary.txt` to keep the dictionary unique and alphabetically ordered.
4. **Regeneration:**
   - Automatically executes `scripts/generate_typos_config.py` to rebuild the typos config (`_typos.toml`).

## Acceptance Criteria
- Running `uv run scripts/whitelist_typos.py <word1> [word2] ...` successfully updates, sorts, and regenerates typos config in one run.
- The dictionary is correctly sorted and formatting is preserved.
