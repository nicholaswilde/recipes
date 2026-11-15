---
name: search-bayesian-recipes
description: >-
  Search online for lacto-ovo vegetarian, scratch-made recipes (avoiding commercial packets/mixes), extract ratings and vote counts, and rank candidates using Bayesian average. Trigger: /search-bayesian-recipes, 'search bayesian recipes', 'search high bayesian recipe', 'find best rated recipe'.
---

# Search Bayesian Recipes

Search online for recipe candidates, enforce lacto-ovo vegetarian and from-scratch (no commercial packets/mixes) preferences, extract ratings and vote counts, and rank them objectively by Bayesian average.

## Protocol

1. **Check Existing Collection**:

   Check whether a similar recipe already exists in `cook/` or `docs/` before searching:

   ```bash
   rtk fd -i "<keyword>" cook/ docs/
   ```

2. **Search Online Candidates**:

   Run targeted web searches for the requested dish (and any qualifiers such as `light`, `healthy`, `easy`, or `authentic`). Gather candidate URLs from reputable recipe blogs and recipe databases.

3. **Filter for Dietary & From-Scratch Standards**:

   Inspect each candidate's ingredient list (via JSON-LD `recipeIngredient` or recipe card) and apply project preferences:
   - **Lacto-Ovo Vegetarian**: Exclude recipes containing meat, poultry, fish, or seafood (including hidden animal ingredients like anchovies, fish sauce, or meat broth). Dairy and eggs are permitted unless requested otherwise.
   - **From Scratch Over Packets**: Prefer recipes made completely from scratch using individual herbs, spices, and pantry staples. Exclude or explicitly flag/demote candidates that rely on commercial seasoning packets, dressing mix packets (e.g., Good Seasons, ranch mix), instant pudding mixes, cake mixes, or bottled dressings as a base.

4. **Extract Ratings & Vote Counts**:

   Try automated scraping first via `rank_recipe_urls.py`:

   ```bash
   rtk uv run python3 scripts/rank_recipe_urls.py <URL1> <URL2> ... --min-votes 10 --prior-rating 3.5
   ```

   For URLs that return HTTP 403 or lack parsed schema in `urllib`, fetch JSON-LD `aggregateRating` (`ratingValue`, `ratingCount`/`reviewCount`) using `curl -sL` with a browser User-Agent or look up the exact site rating and vote count via web search. Never invent or estimate ratings or vote counts.

5. **Rank with Bayesian Average**:

   Pipe all verified candidates into `scripts/rank_recipes_bayesian.py` (`m=10.0`, `C=3.5` defaults; $W = \frac{v \cdot R + m \cdot C}{v + m}$):

   ```bash
   rtk uv run python3 scripts/rank_recipes_bayesian.py << 'EOF'
   [
     {
       "title": "Recipe Title (Source)",
       "rating": 4.93,
       "votes": 14,
       "url": "https://example.com/recipe/"
     }
   ]
   EOF
   ```

6. **Present Ranked Results & Offer Import**:

   - Display a ranked Markdown table with **Rank**, **Recipe**, **Raw Rating**, **Votes**, **Bayesian Average**, **Scratch / Notes**, and **Source Link**.
   - Recommend the highest-scoring scratch-made candidate matching the user's criteria (and note any packet-based higher-ranked entries separately if relevant).
   - Offer to import the chosen candidate via the `import-recipe` skill.
