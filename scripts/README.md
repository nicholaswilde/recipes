# Scripts Registry

This directory contains utility scripts to automate recipe importing, validation, navigation updating, and content formatting.

## Command & Task Map

Where possible, run these via `Taskfile.yaml` using the `task` runner.

| Script / Command | Taskfile Shortcut | Purpose |
| :--- | :--- | :--- |
| `scripts/move.sh` | `task move FILES="<path>"` | Compiles a single `.cook` recipe directly into `docs/` via `cook-docs` (`.cookdocs.toml` + `cook/recipe.md.gotmpl` for frontmatter, `[category_tags]`, H1 `titleEmoji`, emojis, gram weights, ingredient & step cross-links, JPEG-to-WebP conversion, non-destructive merge, and `zensical.toml` nav sync), runs Pillow/PNG post-processing, formats with `rumdl` and `mdfm fmt`, validates frontmatter via `mdfm check`, and checks spelling/links. |
| `scripts/commit.sh` | `task commit FILES="<path>"` | Automates staging files, prompts for issue number, and commits with standard conventional message. |
| `scripts/spellcheck.sh` | `task spellcheck` | Re-generates `_typos.toml` and spellchecks the repository. |
| `scripts/linkcheck.sh` | `task linkcheck` | Runs the `lychee` link checker. |
| `scripts/list_ingredients.sh` | `task list-ingredients` | Copies a `cook shopping-list` command for all recipes to the clipboard. |
| `scripts/lint_changed.py` | `task lint-changed` | Lints only modified/changed files with `rumdl`, `mdfm check --errors-only`, `mdfm fmt --check` (`docs/` and `cook/`), and `yamllint-rs` (saves tokens). |
| `scripts/git_summary.py` | `task git-summary` | Displays a token-efficient summary of the git workspace status and changes. |
| `scripts/hyperlink_ingredient.py` | `task hyperlink-ingredient TARGET="<path>" INGREDIENT="<name>"` | Hyperlinks occurrences of an ingredient to its recipe/file. |
| `scripts/hyperlink_ingredient_global.py` | `task hyperlink-ingredient-global INGREDIENT="<name>"` | Globally hyperlinks occurrences of an ingredient across all recipes. |
| `scripts/scrape_to_cook.py` | - | Scrapes a recipe webpage URL and compiles it into a CookLang `.cook` file while downloading the image. |
| `scripts/import_recipe_workflow.py` | - | Orchestrates the entire recipe import workflow (scrape, emoji mapping, `move.sh` / `cook-docs`, spellcheck, whitelist). |
| `scripts/import_manual_recipe.py` | - | Orchestrates the manual recipe import pipeline (`.cook`, image, emoji mapping, `move.sh` / `cook-docs`, spellcheck, commit). |
| `scripts/whitelist_typos.py` | - | Whitelists words in the typos dictionary, sorts the file, and rebuilds typos config. |
| `scripts/find_missing_sources.py` | `task check-missing-sources` | Scans markdown recipes to find files that do not have a Source/Sources section. |
| `scripts/check_missing_images.py` | `task check-missing-images` | Scans recipe files (querying `hero` via `mdfm`) to find missing hero images or embeds. |
| `scripts/add_recipe_size.py` | - | Scales ingredients of a recipe by a factor and appends it as a new tab block. |
| `scripts/optimize_images.sh` | - | Converts recipe JPEGs to WebP and optimizes PNG files to reduce image asset file sizes. |
| `scripts/sync_weights_yaml.py` | `task sync-weights` | Regenerates `includes/weights.yaml` from `docs/reference/measuring.md` for `cook-docs` `toGrams` enrichment. |

---

## Detailed Script Descriptions

### 1. Recipe Relocation & Staging

#### [move.sh](move.sh)

* **Usage**: `./scripts/move.sh [-f|--force] <recipe.cook>`
* **Description**: Validates `.cook` syntax and ignored ingredients with `cook-docs doctor --only syntax,ignored`,
  compiles the single recipe directly into `docs/` via `cook-docs` using `.cookdocs.toml` and `cook/recipe.md.gotmpl`
  (handling frontmatter, `[category_tags]`, H1 `titleEmoji`, ingredient/cookware emojis from `includes/emoji.yaml`,
  gram weights from `includes/weights.yaml`, ingredient & step cross-links, JPEG-to-WebP conversion, non-destructive
  merging unless `-f`/`--force` is passed, and `zensical.toml` navigation sync), runs Pillow fallback / `oxipng`
  post-processing when needed, formats with `rumdl` and `mdfm fmt`, validates frontmatter via `mdfm check`, and
  runs spell/link checks.

#### [commit.sh](commit.sh)

* **Usage**: `./scripts/commit.sh <recipe.cook>`
* **Description**: Automates adding new/modified files (the `.cook` file, markdown, image,
  `zensical.toml`, etc.) to git, prompts you for the corresponding GitHub issue number,
  and commits the changes using a structured conventional commit message (e.g.,
  `feat: add recipe. Fixes #123.`).

#### [scrape_to_cook.py](scrape_to_cook.py)

* **Usage**: `uv run scripts/scrape_to_cook.py <URL> [--category <category_override>]`
* **Description**: Scrapes a recipe webpage, extracts its metadata, ingredients, and instructions, and compiles
  them into a properly structured CookLang `.cook` file while downloading the recipe's hero image.

#### [import_recipe_workflow.py](import_recipe_workflow.py)

* **Usage**: `uv run scripts/import_recipe_workflow.py <URL_or_issue> [category]`
* **Description**: Orchestrates the entire single recipe import pipeline: scrapes a recipe URL or
  extracts it from a GitHub issue, maps missing emojis via `check_recipe_emojis.py --fix`, compiles and
  organizes the recipe via `move.sh` (`cook-docs`), and runs the spellchecker (with auto-whitelisting for
  proper nouns).

#### [import_manual_recipe.py](import_manual_recipe.py)

* **Usage**: `uv run scripts/import_manual_recipe.py <cook_file> [-i <image_path>] [-c <category>] [-n <issue_number>] [--commit]`
* **Description**: Orchestrates the manual recipe import pipeline: copies/moves the `.cook` and optional image file
  to the correct category under `cook/`, maps missing emojis via `check_recipe_emojis.py --fix`, runs `move.sh`
  (`cook-docs`) to compile enriched Markdown and process images, and runs the spellchecker (with auto-whitelisting
  of proper nouns). Supports interactive category selection, GitHub issue lookup, and automated conventional committing.

---

### 2. Auto-Fixers & Formatting

#### [zensical_fix.py](zensical_fix.py)

* **Usage**: `uv run scripts/zensical_fix.py`
* **Description**: Validates `zensical.toml` syntax and performs a clean build (`zensical build --clean`).
  It parses the warnings and errors to automatically fix common issues (e.g., removing unused
  reference definitions, escaping bracketed text like `[ml]`, or turning unresolved recipe links into plain text).

#### [sync_weights_yaml.py](sync_weights_yaml.py)

* **Usage**: `uv run scripts/sync_weights_yaml.py` or `task sync-weights`
* **Description**: Parses the Ingredient Weight Chart in [docs/reference/measuring.md](../docs/reference/measuring.md)
  and generates [includes/weights.yaml](../includes/weights.yaml) for `cook-docs`'s built-in `toGrams` helper.
  Run after editing `docs/reference/measuring.md`.

#### [fix_broken_links.py](fix_broken_links.py)

* **Usage**: `uv run scripts/fix_broken_links.py`
* **Description**: Scans all files in `docs/` and automatically resolves broken relative markdown
  links/images by matching the file basenames against existing files in the repository.

#### [hyperlink_ingredient.py](hyperlink_ingredient.py)

* **Usage**: `uv run python3 scripts/hyperlink_ingredient.py --target <recipe.md> --ingredient "<Name>"` or
  `task hyperlink-ingredient TARGET=<recipe.md> INGREDIENT="<Name>"`
* **Description**: Scans the target recipe and automatically replaces raw text occurrences of the specified
  ingredient with a relative markdown link pointing to its corresponding file in `docs/`.

#### [hyperlink_ingredient_global.py](hyperlink_ingredient_global.py)

* **Usage**: `uv run python3 scripts/hyperlink_ingredient_global.py --ingredient "<Name>"` or
  `task hyperlink-ingredient-global INGREDIENT="<Name>"`
* **Description**: Scans all recipes in `docs/` and automatically replaces raw text occurrences of the specified
  ingredient with a relative markdown link pointing to its corresponding file.

#### [add_recipe_size.py](add_recipe_size.py)

* **Usage**: `uv run scripts/add_recipe_size.py <recipe.md> <scale_factor> <tab_name>`
* **Description**: Scales ingredient quantities in a recipe's markdown file by a given multiplier and adds
  the result as a new tab (e.g. `=== "Serves 4"`). Handles mixed fractions, simple fractions, decimals,
  integers, and weight measurements in grams.

#### [optimize_images.sh](optimize_images.sh)

* **Usage**: `./scripts/optimize_images.sh [category]`
* **Description**: Converts recipe JPEGs to WebP format, optimizes PNG files using `oxipng`, updates markdown links
  automatically, and removes the original image assets to reduce file sizes.

---

### 3. Checkers & Linter Generators

#### [check_recipe_emojis.py](check_recipe_emojis.py)

* **Usage**: `uv run scripts/check_recipe_emojis.py [--fix] <recipe.cook>`
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

#### [sync_giscus_comments.py](sync_giscus_comments.py)

* **Usage**: `uv run scripts/sync_giscus_comments.py [--triage] [--mode auto|pr|issue] [--dry-run] [--seed-state]`
* **Description**: Queries GitHub Discussions via `gh api` to locate recipes with active comments,
  setting `comments: true` via `mdfm`. With `--triage`, detects new cooking notes, promotes
  `must-try` tags to `favorite` via `mdfm`, stages notes in source `.cook` files, and opens PRs/issues.

#### [find_missing_sources.py](find_missing_sources.py)

* **Usage**: `uv run scripts/find_missing_sources.py` or `task check-missing-sources`
* **Description**: Scans all markdown recipe files under `docs/` (excluding configuration, index, and reference files)
  to identify those missing a Source/Sources heading.

#### [check_missing_images.py](check_missing_images.py)

* **Usage**: `uv run scripts/check_missing_images.py [--json] [--category CATEGORY]` or `task check-missing-images`
* **Description**: Queries recipe `hero` frontmatter via `mdfm` and scans recipe markdown files under `docs/` to report
  missing hero frontmatter fields, missing image embeds (`![...]`), nonexistent hero files, and corrupted links.

---

### 4. Helper Libraries

#### [lib/libbash](lib/libbash)

* **Description**: Sourced library containing common helper functions used across bash scripts in this
  repository. Includes utilities for terminal output, logging, version info, checking system commands,
  and parsing recipe file attributes.

---

### 5. Token-Saving Tools for AI Agents

#### [lint_changed.py](lint_changed.py)

* **Usage**: `uv run python3 scripts/lint_changed.py` or `task lint-changed`
* **Description**: A specialized linter wrapper that detects modified, staged, or untracked Markdown,
  Cooklang, and YAML files in the git workspace, running `rumdl`, `mdfm check --errors-only`, `mdfm fmt --check`
  (on `docs/**/*.md` and `cook/**/*.cook`), and `yamllint-rs` only on those files to save context tokens.

#### [git_summary.py](git_summary.py)

* **Usage**: `uv run python3 scripts/git_summary.py` or `task git-summary`
* **Description**: Prints a highly compact, token-efficient summary of branch status, modified files stat,
  and the last commit, avoiding verbose git status and git diff outputs.
