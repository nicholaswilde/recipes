# /rank-recipe-urls

Fetch ratings and review counts from recipe URLs and rank them objectively using the Bayesian average.

## Description

This skill extracts structured recipe schema metadata (rating value, review/rating counts) directly from a list of recipe URLs, calculates their Bayesian average rating, and ranks them in a clean Markdown table. This helps verify the quality of recipes before importing them.

## Protocol

### 1. Collect Recipe URLs

Identify a list of recipe URLs you want to compare (for example, from a search page or different recipe blogs).

### 2. Invoke the Script

Run the URL ranker script by passing the URLs as arguments:

```bash
uv run python3 scripts/rank_recipe_urls.py <URL1> <URL2> ... [--min-votes 10] [--prior-rating 3.5]
```

Or pipe a list of URLs directly (one URL per line) into the script:

```bash
cat urls.txt | uv run python3 scripts/rank_recipe_urls.py
```

### 3. Review and Select the Best Recipe

The script will print a ranked table showing:

- Raw Rating
- Number of Reviews/Votes
- Weighted Bayesian Average Rating
- Link to the Source

Select the recipe with the highest Bayesian Average to import into the repository using the `import-recipe` skill.
