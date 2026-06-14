# Scripts Registry

This directory contains utility scripts to automate recipe importing, validation, navigation updating, and content formatting.

## Command & Task Map

Where possible, run these via `Taskfile.yaml` using the `task` runner.

| Script / Command | Taskfile Shortcut | Purpose |
| :--- | :--- | :--- |
| `scripts/move.sh` | `task move FILES="<path>"` | Relocates a compiled recipe `.md` and its image, runs spellchecking, and updates navigation. |
| `scripts/commit.sh` | `task commit FILES="<path>"` | Automates staging files, prompts for issue number, and commits with standard conventional message. |
| `scripts/spellcheck.sh` | `task spellcheck` | Re-generates `_typos.toml` and spellchecks the repository. |
| `scripts/linkcheck.sh` | `task linkcheck` | Runs the `lychee` link checker. |
| `scripts/list-ingredients.sh` | `task list-ingredients` | Copies a `cook shopping-list` command for all recipes to the clipboard. |
| `scripts/lint-changed.py` | `task lint-changed` | Lints only modified/changed files (saves tokens). |
| `scripts/git-summary.py` | `task git-summary` | Displays a token-efficient summary of the git workspace status and changes. |
| `scripts/hyperlink-ingredient.py` | `task hyperlink-ingredient TARGET="<path>" INGREDIENT="<name>"` | Hyperlinks occurrences of an ingredient to its recipe/file. |
| `scripts/hyperlink-ingredient-global.py` | `task hyperlink-ingredient-global INGREDIENT="<name>"` | Globally hyperlinks occurrences of an ingredient across all recipes. |
| `scripts/scrape_to_cook.py` | - | Scrapes a recipe webpage URL and compiles it into a CookLang `.cook` file while downloading the image. |
| `scripts/import_recipe_workflow.py` | - | Orchestrates the entire recipe import workflow (scrape, move, emojis, units, spellcheck, whitelist). |
| `scripts/whitelist_typos.py` | - | Whitelists words in the typos dictionary, sorts the file, and rebuilds typos config. |
| `scripts/find_missing_sources.py` | `task check-missing-sources` | Scans markdown recipes to find files that do not have a Source/Sources section. |
| `scripts/check_missing_images.py` | `task check-missing-images` | Scans recipe files to find files missing hero images or embeds. |
| `scripts/add-recipe-nav.py` | - | Adds a recipe's relative path to the correct navigation section in `zensical.toml`. |
| `scripts/add_recipe_size.py` | - | Scales ingredients of a recipe by a factor and appends it as a new tab block. |
| `scripts/adjust_recipe_metadata.py` | - | Modifies frontmatter metadata tags and custom properties for a recipe markdown file. |
| `scripts/optimize-images.sh` | - | Converts recipe JPEGs to WebP and optimizes PNG files to reduce image asset file sizes. |
| `scripts/refactor_nav.py` | - | Replaces navigation blocks in `zensical.toml` with preset navigation structures. |
| `scripts/move_and_verify.py` | - | Relocates recipes in `sides` and `sauces-and-dressings` to subdirectories and updates navigation. |

---

## Detailed Script Descriptions

### 1. Recipe Relocation & Staging

#### [move.sh](move.sh)

* **Usage**: `./scripts/move.sh <recipe.cook>`
* **Description**: Moves compiled `.md` recipe files and their associated images to their
  final categories. It runs spellchecking, checks for dead links, adds the recipe to
  `zensical.toml` navigation, and triggers a clean task.

#### [commit.sh](commit.sh)

* **Usage**: `./scripts/commit.sh <recipe.cook>`
* **Description**: Automates adding new/modified files (the `.cook` file, markdown, image,
  `zensical.toml`, etc.) to git, prompts you for the corresponding GitHub issue number,
  and commits the changes using a structured conventional commit message (e.g.,
  `feat: add recipe. Fixes #123.`).

#### [move_and_verify.py](move_and_verify.py)

* **Usage**: `uv run scripts/move_and_verify.py`
* **Description**: A specialized batch utility script that organizes and relocates recipes within
  the `sides` and `sauces-and-dressings` categories to their nested subdirectories (e.g.,
  `potatoes`, `vinaigrettes`, `salsas`), maintaining both the `.cook` files and compiled markdown docs.

#### [add-recipe-nav.py](add-recipe-nav.py)

* **Usage**: `uv run scripts/add-recipe-nav.py <recipe_name> <relative_path>`
* **Description**: Automatically inserts a recipe file under the correct section list in
  `zensical.toml` and maintains alphabetical ordering of the list items.

#### [scrape_to_cook.py](scrape_to_cook.py)

* **Usage**: `uv run scripts/scrape_to_cook.py <URL> [--category <category_override>]`
* **Description**: Scrapes a recipe webpage, extracts its metadata, ingredients, and instructions, and compiles
  them into a properly structured CookLang `.cook` file while downloading the recipe's hero image.

#### [import_recipe_workflow.py](import_recipe_workflow.py)

* **Usage**: `uv run scripts/import_recipe_workflow.py <URL_or_issue> [category]`
* **Description**: Orchestrates the entire single recipe import pipeline: scrapes a recipe URL or
  extracts it from a GitHub issue, moves it to the appropriate category, runs emoji verification
  and auto-fixing, converts volumetric measurements to weights, and runs the spellchecker (with
  auto-whitelisting for proper nouns).

---

### 2. Auto-Fixers & Formatting

#### [zensical_fix.py](zensical_fix.py)

* **Usage**: `uv run scripts/zensical_fix.py`
* **Description**: Validates `zensical.toml` syntax and performs a clean build (`zensical build --clean`).
  It parses the warnings and errors to automatically fix common issues (e.g., removing unused
  reference definitions, escaping bracketed text like `[ml]`, or turning unresolved recipe links into plain text).

#### [convert-recipe-units.py](convert-recipe-units.py)

* **Usage**: `uv run scripts/convert-recipe-units.py <recipe.md>`
* **Description**: Scans a recipe's markdown Ingredients list, automatically converts volumetric/count
  measurements (like `1 cup` or `2 tbsp`) into weight-annotated units (`(120 g)`) by reading mappings
  in [docs/reference/measuring.md](../docs/reference/measuring.md), and inserts the matching ingredient
  emoji from [includes/emoji.yaml](../includes/emoji.yaml).

#### [fix_broken_links.py](fix_broken_links.py)

* **Usage**: `uv run scripts/fix_broken_links.py`
* **Description**: Scans all files in `docs/` and automatically resolves broken relative markdown
  links/images by matching the file basenames against existing files in the repository.

#### [hyperlink-ingredient.py](hyperlink-ingredient.py)

* **Usage**: `uv run python3 scripts/hyperlink-ingredient.py --target <recipe.md> --ingredient "<Name>"` or
  `task hyperlink-ingredient TARGET=<recipe.md> INGREDIENT="<Name>"`
* **Description**: Scans the target recipe and automatically replaces raw text occurrences of the specified
  ingredient with a relative markdown link pointing to its corresponding file in `docs/`.

#### [hyperlink-ingredient-global.py](hyperlink-ingredient-global.py)

* **Usage**: `uv run python3 scripts/hyperlink-ingredient-global.py --ingredient "<Name>"` or
  `task hyperlink-ingredient-global INGREDIENT="<Name>"`
* **Description**: Scans all recipes in `docs/` and automatically replaces raw text occurrences of the specified
  ingredient with a relative markdown link pointing to its corresponding file.

#### [add_recipe_size.py](add_recipe_size.py)

* **Usage**: `uv run scripts/add_recipe_size.py <recipe.md> <scale_factor> <tab_name>`
* **Description**: Scales ingredient quantities in a recipe's markdown file by a given multiplier and adds
  the result as a new tab (e.g. `=== "Serves 4"`). Handles mixed fractions, simple fractions, decimals,
  integers, and weight measurements in grams.

#### [adjust_recipe_metadata.py](adjust_recipe_metadata.py)

* **Usage**:

  ```bash
  uv run scripts/adjust_recipe_metadata.py <recipe.md> \
    [--add-tags <tag1,tag2>] [--remove-tags <tag3>] [--set-metadata <key=val>]
  ```

* **Description**: Modifies frontmatter metadata tags and custom properties (such as comments or hero images)
  for a recipe markdown file.

#### [optimize-images.sh](optimize-images.sh)

* **Usage**: `./scripts/optimize-images.sh [category]`
* **Description**: Converts recipe JPEGs to WebP format, optimizes PNG files using `oxipng`, updates markdown links
  automatically, and removes the original image assets to reduce file sizes.

---

### 3. Checkers & Linter Generators

#### [check-recipe-emojis.py](check-recipe-emojis.py)

* **Usage**: `uv run scripts/check-recipe-emojis.py [--fix] <recipe.cook>`
* **Description**: Scans a `.cook` file's ingredients (`@`) and cookware (`#`) references to check
  if they are mapped to emojis in [includes/emoji.yaml](../includes/emoji.yaml), exiting with a
  non-zero status if any mapped emojis are missing. The optional `--fix` flag automatically maps
  missing items using similarity checking or fallback groups and writes them back.

#### [generate_typos_config.py](generate_typos_config.py)

* **Usage**: `uv run scripts/generate_typos_config.py`
* **Description**: Re-generates `_typos.toml` by reading and sorting words from [dictionary.txt](../dictionary.txt).

#### [whitelist_typos.py](whitelist_typos.py)

* **Usage**: `uv run scripts/whitelist_typos.py <word1> [word2] ...`
* **Description**: Appends one or more words to [dictionary.txt](../dictionary.txt), automatically runs
  an alphabetical sort and unique deduplication on the dictionary, and executes the typos config generator
  to rebuild `_typos.toml` in a single run.

#### [identify_multi_serving.py](identify_multi_serving.py)

* **Usage**: `uv run scripts/identify_multi_serving.py [directory]`
* **Description**: Scans for recipe markdown files containing multiple "Ingredients" headers (which
  usually represent multi-serving/tab configurations).

#### [find_duplicate_issues.py](find_duplicate_issues.py)

* **Usage**: `uv run scripts/find_duplicate_issues.py [--close]`
* **Description**: Scans open duplicate-labeled issues on GitHub and cross-references them against
  imported recipes in the codebase, with an optional `--close` flag to auto-close exact URL matches.

#### [comments.sh](comments.sh)

* **Usage**: `./scripts/comments.sh`
* **Description**: Traverses markdown recipes and appends `comments: true` to the front-matter of
  any file missing it.

#### [sync_giscus_comments.py](sync_giscus_comments.py)

* **Usage**: `uv run scripts/sync_giscus_comments.py`
* **Description**: Queries GitHub Discussions via `gh api` to locate recipes with active comments,
  automatically setting `comments: true` in their front-matter.

#### [find_missing_sources.py](find_missing_sources.py)

* **Usage**: `uv run scripts/find_missing_sources.py` or `task check-missing-sources`
* **Description**: Scans all markdown recipe files under `docs/` (excluding configuration, index, and reference files)
  to identify those missing a Source/Sources heading.

#### [check_missing_images.py](check_missing_images.py)

* **Usage**: `uv run scripts/check_missing_images.py [--json] [--category CATEGORY]` or `task check-missing-images`
* **Description**: Scans all recipe markdown files under `docs/` and reports missing hero frontmatter fields,
  missing image embeds (`![...]`), nonexistent hero files, and corrupted links.

#### [refactor_nav.py](refactor_nav.py)

* **Usage**: `uv run scripts/refactor_nav.py`
* **Description**: A batch helper script that replaces the `Sides` and `Sauces & Dressings` navigation configurations
  in `zensical.toml` with pre-defined structures.

---

### 4. Helper Libraries

#### [lib/libbash](lib/libbash)

* **Description**: Sourced library containing common helper functions used across bash scripts in this
  repository. Includes utilities for terminal output, logging, version info, checking system commands,
  and parsing recipe file attributes.

---

### 5. Token-Saving Tools for AI Agents

#### [lint-changed.py](lint-changed.py)

* **Usage**: `uv run python3 scripts/lint-changed.py` or `task lint-changed`
* **Description**: A specialized linter wrapper that detects modified, staged, or untracked Markdown
  and YAML files in the git workspace, running the appropriate linters only on those files to save context tokens.

#### [git-summary.py](git-summary.py)

* **Usage**: `uv run python3 scripts/git-summary.py` or `task git-summary`
* **Description**: Prints a highly compact, token-efficient summary of branch status, modified files stat,
  and the last commit, avoiding verbose git status and git diff outputs.
