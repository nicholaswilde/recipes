# Implementation Plan - Recipe Webpage to CookLang Parser Script

## Phase 1: Implementation & Validation [checkpoint: 40e2ae30]

- [x] Task: Create `scripts/scrape_to_cook.py` (6a9167b)
    - [x] Set up HTML fetching and BeautifulSoup/JSON-LD parsing.
    - [x] Implement parsing of title, servings, times, source URL, ingredients, instructions.
    - [x] Format ingredients and time ranges to CookLang syntax.
    - [x] Resolve target category and save `.cook` and `.jpg` image files.
- [x] Task: Write Unit Tests (6a9167b)
    - [x] Add tests verifying parser accuracy against test HTML bodies from target recipe
      sites (e.g. RecipeTin Eats, The Plant Based School).
- [x] Task: Document in Scripts Registry (62b55cf)
    - [x] Document the script's usage in `scripts-registry.md`.
- [x] Task: Conductor - User Manual Verification (6a9167b)
