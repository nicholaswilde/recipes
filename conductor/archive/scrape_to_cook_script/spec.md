# Specification - Recipe Webpage to CookLang Parser Script

## Overview
Develop a Python utility `scripts/scrape_to_cook.py` that automatically extracts recipe data (from recipe schema JSON-LD or standard HTML structure) and compiles it into a properly formatted CookLang `.cook` file, along with downloading the hero recipe image.

## Functional Requirements
1. **Inputs:** Accepts a recipe URL as a CLI argument.
2. **Extraction:**
   - Fetches target webpage HTML.
   - Extracts structured recipe JSON-LD schema or parses the HTML using BeautifulSoup.
   - Extracts: title, servings count, prep time, cook time, total time, source URL, ingredients list, and instructions steps.
3. **CookLang Compilation:**
   - Formats metadata headers (e.g. `>> title: ...`, `>> servings: ...`, `>> source: ...`).
   - Parses the ingredients and tags them with `@` (e.g. `@plain flour{2.5%cups}`).
   - Formats measurement ranges cleanly (e.g., converting `1-2 minutes` to `1 to ~{2%minutes}`).
   - Respects ignored ingredients defined in `cook/config/ignored_ingredients.yaml`.
4. **Hero Image:**
   - Detects the primary high-resolution recipe image.
   - Automatically downloads and saves the image with the same name as the `.cook` file (e.g., `Recipe Name.jpg`) in the target directory.
5. **Output Path:** Automatically categorizes the recipe and writes the files under `cook/{category}/{Recipe Name}.cook` and `cook/{category}/{Recipe Name}.jpg`.

## Acceptance Criteria
- Running `uv run scripts/scrape_to_cook.py <URL>` successfully creates the `.cook` and `.jpg` files without manual parser steps.
- The compiled `.cook` file passes CookLang compiler checks.
- All dependencies are managed cleanly using `uv`.
