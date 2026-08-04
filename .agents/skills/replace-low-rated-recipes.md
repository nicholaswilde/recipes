# /replace-low-rated-recipes

Detect low-performing recipes in the repository and identify high-quality online replacements.

## Description

This skill automates the process of scanning all imported recipe files in the repository, checking their original web ratings, and identifying ones that fall below a certain Bayesian average threshold. It then generates convenient search links to locate higher-rated alternatives from authority recipe blogs.

## Protocol

### 1. Scan for Low-Ranked Recipes

Run the scanner script in your terminal to see a list of recipes that have low Bayesian ratings (under 4.4 ★ by default):

```bash
uv run python3 scripts/find_low_ranked_recipes.py
```

Optional arguments:

* `--threshold`: Flag recipes with a Bayesian score under this number (default: `4.4`).
* `--min-votes`: Minimum votes threshold for Bayesian formula (default: `10.0`).
* `--prior-rating`: Prior rating to weight against (default: `3.5`).
* `--dir`: The folder to scan (default: `cook`).

### 2. Research Replacements

For each flagged recipe, the output table provides a **Search Replacements** link. Use this link or query search engines to find recipes on top-tier websites (e.g., *Sally's Baking Addiction*, *King Arthur Baking*, *The Cozy Cook*, *Serious Eats*).

### 3. Rank and Compare Candidates

Collect the URLs of promising replacement recipes and evaluate them against the current source using the `rank-recipe-urls` skill:

```bash
uv run python3 scripts/rank_recipe_urls.py <CurrentURL> <NewURL1> <NewURL2>
```

Identify the candidate with the highest Bayesian average.

### 4. Replace the Recipe

Run the project's unified import workflow for the chosen new recipe:

```bash
uv run scripts/import_recipe_workflow.py <NewURL> <category>
```

Once the new recipe is imported:

1. Delete the old `.cook` recipe file and its generated `.md` docs/assets.
2. Update the navigation in [zensical.toml](file:///home/nicholas/git/nicholaswilde/recipes/zensical.toml) by removing the old file reference and positioning the new file reference alphabetically in the correct category block.
3. run `task validate` and `task lint-changed` to verify structural and lint correctness.
