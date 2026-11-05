# Agent Skills Catalog

Catalog of custom Antigravity agent skills available in `recipes`.

| Skill | Description | Task / Command |
|---|---|---|
| [`add-recipe-size`](skills/add-recipe-size/SKILL.md) | Automate adding additional serving or batch sizes to a recipe file by creating a new Zensical tab | `/add-recipe-size` |
| [`adjust-recipe-metadata`](skills/adjust-recipe-metadata/SKILL.md) | Adjust recipe metadata, tags, and frontmatter dynamically on recipe markdown files | `/adjust-recipe-metadata` |
| [`backfill-missing-sources`](skills/backfill-missing-sources/SKILL.md) | Audit recipes for missing Source sections, investigate origins via git history, issues, or external references, format standard source headings and links, and validate the site | `uv run scripts/audit_missing_sources.py` |
| [`create-issue`](skills/create-issue/SKILL.md) | Create a new GitHub issue using gh CLI with structured titles and appropriate labels | `/create-issue <title> [description]` |
| [`dedupe-zensical`](skills/dedupe-zensical/SKILL.md) | Remove duplicate array entries in the zensical.toml configuration file | `/dedupe-zensical` |
| [`find-duplicate-issues`](skills/find-duplicate-issues/SKILL.md) | Scan GitHub issues and local recipe repositories to detect duplicate issues, cross-issue duplicates, and already-imported recipes | `uv run scripts/find_duplicate_issues.py` / `/find-duplicate-issues` |
| [`find-duplicates`](skills/find-duplicates/SKILL.md) | Analyze recipes for title and ingredient similarities to identify duplicates or highly similar recipes | `uv run scripts/find_duplicates.py` / `/find-duplicates` |
| [`fix-failed-workflows`](skills/fix-failed-workflows/SKILL.md) | Diagnose and resolve failed GitHub Actions workflow runs (Documentation, spellcheck, link-check, zensical build, TOML decode errors, CookLang validation, and linting) | `task lint` / `task validate` |
| [`generate-hero-image`](skills/generate-hero-image/SKILL.md) | Generate a hero image for an existing recipe, link it to the .cook file, compile to markdown, and convert to WebP | `/generate-hero-image` |
| [`hyperlink-ingredient`](skills/hyperlink-ingredient/SKILL.md) | Automatically find and add relative markdown hyperlinks to specific ingredients mentioned in target recipe files | `python3 scripts/hyperlink_ingredient.py` / `/hyperlink-ingredient` |
| [`hyperlink-ingredient-global`](skills/hyperlink-ingredient-global/SKILL.md) | Globally find and add relative markdown hyperlinks to a specific ingredient in all recipe files that mention it | `python3 scripts/hyperlink_ingredient_global.py` / `/hyperlink-ingredient-global` |
| [`import-manual-recipe`](skills/import-manual-recipe/SKILL.md) | Import recipes from manual sources, images, PDFs, or unscrapable websites into CookLang format with strict validation | `/import-manual-recipe` |
| [`import-recipe`](skills/import-recipe/SKILL.md) | Import a recipe from a URL, GitHub issue, image, PDF, or YouTube video into the collection: scrape or OCR, draft CookLang, handle hero images, compile, validate, and commit | `FILES=<path> task move` / `/import-recipe` |
| [`link-ingredient`](skills/link-ingredient/SKILL.md) | Search for an ingredient in Markdown recipes and create links to its own recipe page | `/link-ingredient <args>` |
| [`linkcheck-fix`](skills/linkcheck-fix/SKILL.md) | Perform offline link checking with lychee and automatically resolve and fix broken local markdown links and image paths | `uv run scripts/fix_broken_links.py` / `/linkcheck-fix` |
| [`linkcheck-online`](skills/linkcheck-online/SKILL.md) | Perform online link check with lychee to verify external URLs across markdown files and fix genuine dead links | `task linkcheck` / `/linkcheck-online` |
| [`lint-changed-files`](skills/lint-changed-files/SKILL.md) | Run fast linting checks (rumdl and yamllint-rs) only on modified, staged, or untracked files in the workspace | `task lint-changed` / `/lint-changed-files` |
| [`list-author-recipes`](skills/list-author-recipes/SKILL.md) | List recipes in repository containing an author name, blog, restaurant, or brand in title, respecting author whitelist | `uv run scripts/list_author_recipes.py` / `/list-author-recipes` |
| [`list-issues`](skills/list-issues/SKILL.md) | List open issues in the GitHub repository with optional label filtering | `/list-issues [args]` |
| [`liteparse`](skills/liteparse/SKILL.md) | Parse, convert multi-format documents, or spatially extract text from unstructured files (PDF, DOCX, XLSX, images) locally without cloud dependencies | `lit parse <file>` / `/liteparse` |
| [`rank-recipe-urls`](skills/rank-recipe-urls/SKILL.md) | Extract ratings and review counts from recipe URLs and rank them objectively using Bayesian average | `uv run scripts/rank_recipe_urls.py` / `/rank-recipe-urls` |
| [`rank-recipes-bayesian`](skills/rank-recipes-bayesian/SKILL.md) | Calculate Bayesian average for recipe search results to rank them objectively by rating and review count | `uv run scripts/rank_recipes_bayesian.py` / `/rank-recipes-bayesian` |
| [`recipe-image-validation`](skills/recipe-image-validation/SKILL.md) | Identify and resolve missing or corrupted images in recipe files, ensuring valid hero frontmatter and body embeds | `python3 scripts/check_recipe_images.py` / `/recipe-image-validation` |
| [`recipe-servings-tabs`](skills/recipe-servings-tabs/SKILL.md) | Convert recipes with multiple serving sizes or batch variations into Zensical content tabs with 4-space indentation | `python3 scripts/format_recipe_servings_tabs.py` / `/recipe-servings-tabs` |
| [`recipe-tab-conversion`](skills/recipe-tab-conversion/SKILL.md) | Convert recipes with multiple ingredients or instructions sections into Zensical Content Tabs (pymdownx.tabbed) | `/recipe-tab-conversion` |
| [`remove-recipe`](skills/remove-recipe/SKILL.md) | Safely and completely remove a recipe including Markdown, Cooklang, images, cross-references, and zensical.toml navigation entries | `uv run scripts/remove_recipe.py` / `/remove-recipe <args>` |
| [`rename-recipe`](skills/rename-recipe/SKILL.md) | Safely rename a recipe along with Markdown, Cooklang, images, zensical.toml entries, and cross-references while preserving git history | `uv run scripts/rename_recipe.py` / `/rename-recipe <old> <new>` |
| [`replace-low-rated-recipes`](skills/replace-low-rated-recipes/SKILL.md) | Detect low-performing recipes below Bayesian rating threshold and identify high-quality online replacements | `uv run scripts/replace_low_rated_recipes.py` / `/replace-low-rated-recipes` |
| [`resolve-duplicate-issues`](skills/resolve-duplicate-issues/SKILL.md) | Scan duplicate-labeled GitHub issues and close them automatically if recipe has already been imported | `uv run scripts/find_duplicate_issues.py --auto-close` / `/resolve-duplicate-issues` |
| [`review-actions`](skills/review-actions/SKILL.md) | Monitor GitHub Actions workflow runs, diagnose failure logs, and apply fixes for linting, spellcheck, link check, or build issues | `/review-actions` |
| [`scripts-registry`](skills/scripts-registry/SKILL.md) | Registry of automation and utility scripts in recipes repository for importing, formatting, moving, and checking recipes | `/scripts-registry` |
| [`spellcheck-fix`](skills/spellcheck-fix/SKILL.md) | Perform fast spell checking using typos and automatically fix spelling errors across repository files | `task spellcheck-fix` / `/spellcheck-fix` |
| [`zensical-fix`](skills/zensical-fix/SKILL.md) | Validate Zensical project and automatically fix issues (unresolved reference links, unused link definitions, build warnings) | `uv run scripts/zensical_fix.py` / `/zensical-fix` |
