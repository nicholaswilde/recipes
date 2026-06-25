# /rank-recipes-bayesian

Calculate the Bayesian average for a set of recipe search results to rank them objectively by both rating and review count.

## Description

When searching for recipes on the internet, sorting purely by raw rating (e.g. 5.0 stars) often highlights recipes with only 1 or 2 reviews. This skill ranks recipes using a simplified Bayesian average formula, ensuring that recipes with many high-rating reviews are ranked above those with very few reviews.

### Mathematical Formula

The simplified Bayesian average is calculated as:

$$ W = \frac{v \cdot R + m \cdot C}{v + m} $$

Where:

- **$W$**: Weighted rating (the resulting Bayesian average).
- **$R$**: Raw average rating of the recipe (from 0 to 5 stars).
- **$v$**: Number of ratings/votes/reviews for the recipe.
- **$m$**: Minimum number of ratings required to be considered (Default: `10` or the 25th percentile of votes).
- **$C$**: The prior rating / mean rating to smooth towards (Default: `3.5` stars).

---

## Protocol

### 1. Structure the Input Data

Prepare a JSON file containing the recipe search results with `title`, `rating` (0.0 to 5.0), `votes` (integer count), and optionally `url` or `source`. For example, save this to `recipes_to_rank.json`:

```json
[
  {
    "title": "Perfect Butter Cake (Preppy Kitchen)",
    "rating": 4.8,
    "votes": 500,
    "url": "https://preppykitchen.com/butter-cake/"
  },
  {
    "title": "Quick Butter Cake (Blog X)",
    "rating": 5.0,
    "votes": 3,
    "url": "https://example.com/quick-butter-cake"
  },
  {
    "title": "Decent Butter Cake (Blog Y)",
    "rating": 4.6,
    "votes": 85,
    "url": "https://example.com/decent-butter-cake"
  }
]
```

### 2. Invoke the Script

Run the Bayesian ranker script on the input JSON file:

```bash
uv run python3 scripts/rank_recipes_bayesian.py --input recipes_to_rank.json --min-votes 10 --prior-rating 3.5
```

### 3. Interactive Mode (Alternative)

To quickly compare a few ratings without writing a JSON file, run in interactive mode:

```bash
uv run python3 scripts/rank_recipes_bayesian.py --interactive
```

This will prompt you to enter the rating and votes of each recipe one-by-one, and output the ranked table when you enter `q`.
