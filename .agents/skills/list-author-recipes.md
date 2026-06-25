# /list-author-recipes

Print a list of all recipes in the repository that contain an author name, blog, restaurant, or brand in their title, using the `zensical.toml` configuration while respecting the whitelist.

## Description

This skill parses the `zensical.toml` navigation configuration, extracts all active recipes, identifies those with author names or brand identifiers in their titles, filters out whitelisted entries, and presents the resulting list.

## Protocol

1. **Read Configuration & Whitelist:**
   - Read the navigation entries in `zensical.toml` to collect all active recipe titles and their file paths.
   - Read `.agents/author_whitelist.txt` to obtain the list of whitelisted recipe titles, author names, or substrings.

2. **Detect Author Names/Identifiers:**
   - Scan the recipe titles for common indicators of authors, blogs, restaurants, or brands:
     - **Possessive forms:** e.g., `Claire Saffitz's`, `Dorie Greenspan's`, `Mom's`, `Grandpa's`.
     - **Parenthetical sources:** e.g., `(Jacques Torres)`, `(Maura Kilpatrick)`, `(Serious Eats)`.
     - **Trailing identifiers:** e.g., `King Arthur Baking`, `Tasty`, `Allrecipes`, `Shutterbean`, `iFoodReal`.
     - **Well-known names/entities:** e.g., `Gordon Ramsay`, `Jamie Oliver`, `Ina Garten`, `Julia Child`, `America's Test Kitchen`.

3. **Apply Whitelist Filtering:**
   - Compare each identified recipe title against the terms inside `.agents/author_whitelist.txt`.
   - If a title exactly matches a whitelisted entry, or contains a whitelisted name/substring as a standalone term (e.g., "Tante Myrna Seccia"), filter it out from the final list.

4. **Display the Results:**
   - Present the identified recipes in a clean, categorized Markdown table containing the following columns:
     - **Recipe Title** (the key from `zensical.toml`)
     - **Identified Author/Source** (the brand or person detected in the title)
     - **Category** (e.g., `Breads`, `Desserts`, `Breakfast`)
     - **File Path** (the file path value from `zensical.toml`)
   - Print a summary line indicating the total number of flagged recipes.
