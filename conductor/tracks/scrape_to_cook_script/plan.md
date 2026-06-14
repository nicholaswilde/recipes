# Implementation Plan - Recipe Webpage to CookLang Parser Script

## Phase 1: Implementation & Validation

- [ ] Task: Create `scripts/scrape_to_cook.py`
    - [ ] Set up HTML fetching and BeautifulSoup/JSON-LD parsing.
    - [ ] Implement parsing of title, servings, times, source URL, ingredients, instructions.
    - [ ] Format ingredients and time ranges to CookLang syntax.
    - [ ] Resolve target category and save `.cook` and `.jpg` image files.
- [ ] Task: Write Unit Tests
    - [ ] Add tests verifying parser accuracy against test HTML bodies from target recipe sites (e.g. RecipeTin Eats, The Plant Based School).
- [ ] Task: Document in Scripts Registry
    - [ ] Document the script's usage in `scripts-registry.md`.
- [ ] Task: Conductor - User Manual Verification
