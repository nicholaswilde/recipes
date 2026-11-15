---
name: compare-issue-bayesian
description: >-
  Compare a GitHub issue recipe URL's Bayesian average rating against top lacto-ovo vegetarian, scratch-made web alternatives and recommend whether to import the issue source or switch. Trigger: /compare-issue-bayesian, 'compare issue bayesian', 'compare bayesian score to issue', 'compare issue to web search', 'evaluate issue recipe'.
---

# Compare Issue Bayesian

Evaluate a recipe proposed in a GitHub issue against online alternatives using Bayesian average scoring (`m=10.0`, `C=3.5`), dietary rules, and from-scratch standards.

## Protocol

1. **Fetch GitHub Issue & Extract Source URL**:

   Query the issue details with `gh` (piped to `cat` in native shell, or directly inside `ctx_execute`):

   ```bash
   rtk gh issue view <issue_number> --json number,title,body,url,labels | cat
   ```

   - Extract the recipe title/keyword from the issue title.
   - Extract the external recipe URL from the issue body (ignoring `github.com/` and `github.com/user-attachments` links).
   - If the issue has no external recipe URL (e.g., image-only or PDF-only), note that the issue lacks a scrapable web rating and proceed using the recipe name.

2. **Check Existing Collection**:

   Check whether the recipe already exists in `cook/` or `docs/`:

   ```bash
   rtk fd -i "<keyword>" cook/ docs/
   ```

3. **Search Online Alternatives**:

   Run targeted web searches for the recipe name (and qualifiers such as `homemade`, `from scratch`, `best rated`, or reputable baking/cooking sites).

   - Resolve any search redirect URLs inside `ctx_execute` to canonical recipe URLs:

     ```bash
     curl -sLI -o /dev/null -w '%{url_effective}\n' -A 'Mozilla/5.0' "<redirect_url>"
     ```

4. **Filter for Dietary & From-Scratch Standards**:

   Inspect each candidate's ingredient list (via JSON-LD `recipeIngredient` or recipe card) and enforce project standards:

   - **Lacto-Ovo Vegetarian**: Exclude recipes containing meat, poultry, fish, or seafood (including hidden animal ingredients like anchovies, fish sauce, or meat broth). Dairy and eggs are permitted unless requested otherwise.
   - **From Scratch Over Packets**: Prefer recipes made from scratch using individual herbs, spices, and pantry staples. Exclude or explicitly flag/demote candidates relying on commercial seasoning packets, dressing mix packets, instant pudding/cake mixes, bottled dressings, or commercial syrup shortcuts.

5. **Score Issue URL & Candidates Together**:

   Run `scripts/rank_recipe_urls.py` with the issue URL and all collected candidate URLs:

   ```bash
   rtk uv run python3 scripts/rank_recipe_urls.py \
     <IssueURL> <CandidateURL1> <CandidateURL2> ... \
     --min-votes 10 --prior-rating 3.5
   ```

   - For URLs returning HTTP 403 or lacking parsed JSON-LD in `urllib`, fetch JSON-LD `aggregateRating` (`ratingValue`, `ratingCount`/`reviewCount`) using `curl -sL -A "Mozilla/5.0"` or verified site search results.
   - If any scores were collected manually, pipe all verified candidates (including the issue source) into `scripts/rank_recipes_bayesian.py` (`m=10.0`, `C=3.5`; $W = \frac{v \cdot R + m \cdot C}{v + m}$).
   - Never invent or estimate ratings or vote counts.

6. **Compare & Recommend**:

   - Present a single ranked Markdown table with **Rank**, **Recipe**, **Raw Rating**, **Votes**, **Bayesian Average**, **Scratch / Notes**, and **Source**.
   - Clearly mark the issue source row (e.g., `**Matches Issue #<num>**`).
   - State the comparison verdict:
     - Whether the issue URL ranks #1 or is outperformed by a higher-scoring scratch-made alternative (reporting exact Bayesian score delta).
     - Whether the issue recipe meets lacto-ovo vegetarian and from-scratch criteria.
   - Offer to import the winning candidate via the `import-recipe` skill (closing or updating `#<num>` as appropriate).
