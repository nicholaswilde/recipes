# Agent Memory

- I have imported the Butternut Squash Tahini Curry recipe (Issue #1344).
- I have imported the Classic White Sandwich Bread recipe (King Arthur Baking).
- I have imported the Beautiful Burger Buns recipe (Ellen Dorsey).
- I have imported the Flaky Buttery Crescent Rolls recipe (King Arthur Baking).
- I have imported the Thai Red Curry Paste recipe.
- I have imported the Mock Soy Sauce recipe.
- I have imported the Dijon Mustard recipe.
- I have added a recipe for homemade Baking Powder.
- I have added a recipe for homemade Self-Rising Flour.
- I have imported the Cannelés de Bordeaux recipe (Issue #1351).
- I have imported the NYT Dutch Baby recipe (Issue #1349).
- I have imported the Lemon Poppy Seed Pound Cake (Melissa Clark) recipe (Issue #1348).
- I have imported the Key Lime Pound Cake recipe (Issue #1346).
- I have updated the Butternut Squash Tahini Curry recipe with a new image and source (Practically Vegan book).
- I have created a new Gemini command `/zensical fix` in `.gemini/commands/zensical-fix.toml` to validate the
  project and fix build issues.
- I have imported the `liteparse` skill into `.agents/skills/liteparse.md`.
- I have imported Stella Parks' BraveTart Brownies recipe, updated zensical.toml, includes/emoji.yaml, and
  dictionary.txt, and downloaded the recipe's hero image.
- I have removed the Peanut Butter Stuffed Brownies recipe, including its CookLang, Markdown, image files, and menu
  configurations.
- Always consult and filter out terms in `.agents/author_whitelist.txt` when listing recipes containing author
  names in their titles to respect whitelisted names (e.g. "Tante Myrna Seccia").
- When importing a recipe that calls for **terasi** (shrimp paste / belacan), always substitute it with a markdown
  link to the Vegetarian Terasi recipe (`[Vegetarian Terasi](../ingredients/vegetarian-terasi.md)`, adjusting the
  relative path as needed) in both the ingredients list and the instructions. Do not list terasi as a plain
  ingredient.
- When importing a recipe that calls for **sambal oelek** (or sambal ulek), always substitute it with a markdown
  link to the Sambal Oelek recipe (`[Sambal Oelek](../sauces-and-dressings/gravy-and-savory-sauces/sambal-oelek.md)`,
  adjusting the relative path as needed) in both the ingredients list and the instructions. Do not list sambal oelek
  as a plain ingredient.
- Always use the GitHub CLI (`gh`) to view, monitor, and debug remote GitHub Actions workflow runs when verifying
  the status of CI pipelines or investigating deployment failures.
- I have imported the Date Brownies recipe (Issue #1355).
- I have added the recipe servings and batch tab conversion skill to `.agents/skills/recipe-servings-tabs.md`.
- I have added a skill to monitor and fix GitHub Actions workflow runs in `.agents/skills/review-actions.md`.
- I have added the recipe image validation skill to `.agents/skills/recipe-image-validation.md`.
- I have imported the Chile Relleno recipe from Isabel Eats.
- I have imported the Frangipane Almond Cream recipe (King Arthur Baking).
- When searching for recipes to import, they must be lacto-ovo vegetarian and have a highly rated Bayesian score.
