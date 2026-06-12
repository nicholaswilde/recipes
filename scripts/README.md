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

---

## Detailed Script Descriptions

### 1. Recipe Relocation & Staging

#### [move.sh](move.sh)
* **Usage**: `./scripts/move.sh <recipe.cook>`
* **Description**: Moves compiled `.md` recipe files and their associated images to their final categories. It runs spellchecking, checks for dead links, adds the recipe to `zensical.toml` navigation, and triggers a clean task.

#### [commit.sh](commit.sh)
* **Usage**: `./scripts/commit.sh <recipe.cook>`
* **Description**: Automates adding new/modified files (the `.cook` file, markdown, image, `zensical.toml`, etc.) to git, prompts you for the corresponding GitHub issue number, and commits the changes using a structured conventional commit message (e.g., `feat: add recipe. Fixes #123.`).

#### [move_and_verify.py](move_and_verify.py)
* **Usage**: `uv run scripts/move_and_verify.py`
* **Description**: A specialized batch utility script that organizes and relocates recipes within the `sides` and `sauces-and-dressings` categories to their nested subdirectories (e.g., `potatoes`, `vinaigrettes`, `salsas`), maintaining both the `.cook` files and compiled markdown docs.

---

### 2. Auto-Fixers & Formatting

#### [zensical_fix.py](zensical_fix.py)
* **Usage**: `uv run scripts/zensical_fix.py`
* **Description**: Validates `zensical.toml` syntax and performs a clean build (`zensical build --clean`). It parses the warnings and errors to automatically fix common issues (e.g., removing unused reference definitions, escaping bracketed text like `[ml]`, or turning unresolved recipe links into plain text).

#### [convert-recipe-units.py](convert-recipe-units.py)
* **Usage**: `uv run scripts/convert-recipe-units.py <recipe.md>`
* **Description**: Scans a recipe's markdown Ingredients list, automatically converts volumetric/count measurements (like `1 cup` or `2 tbsp`) into weight-annotated units (`(120 g)`) by reading mappings in [docs/reference/measuring.md](../docs/reference/measuring.md), and inserts the matching ingredient emoji from [includes/emoji.yaml](../includes/emoji.yaml).

#### [fix_broken_links.py](fix_broken_links.py)
* **Usage**: `uv run scripts/fix_broken_links.py`
* **Description**: Scans all files in `docs/` and automatically resolves broken relative markdown links/images by matching the file basenames against existing files in the repository.

---

### 3. Checkers & Linter Generators

#### [check-recipe-emojis.py](check-recipe-emojis.py)
* **Usage**: `uv run scripts/check-recipe-emojis.py <recipe.cook>`
* **Description**: Scans a `.cook` file's ingredients (`@`) and cookware (`#`) references to check if they are mapped to emojis in [includes/emoji.yaml](../includes/emoji.yaml), exiting with a non-zero status if any mapped emojis are missing.

#### [generate_typos_config.py](generate_typos_config.py)
* **Usage**: `uv run scripts/generate_typos_config.py`
* **Description**: Re-generates `_typos.toml` by reading and sorting words from [dictionary.txt](../dictionary.txt).

#### [identify_multi_serving.py](identify_multi_serving.py)
* **Usage**: `uv run scripts/identify_multi_serving.py [directory]`
* **Description**: Scans for recipe markdown files containing multiple "Ingredients" headers (which usually represent multi-serving/tab configurations).

#### [find_duplicate_issues.py](find_duplicate_issues.py)
* **Usage**: `uv run scripts/find_duplicate_issues.py [--close]`
* **Description**: Scans open duplicate-labeled issues on GitHub and cross-references them against imported recipes in the codebase, with an optional `--close` flag to auto-close exact URL matches.

#### [comments.sh](comments.sh)
* **Usage**: `./scripts/comments.sh`
* **Description**: Traverses markdown recipes and appends `comments: true` to the front-matter of any file missing it.

#### [sync_giscus_comments.py](sync_giscus_comments.py)
* **Usage**: `uv run scripts/sync_giscus_comments.py`
* **Description**: Queries GitHub Discussions via `gh api` to locate recipes with active comments, automatically setting `comments: true` in their front-matter.

---

### 4. Helper Libraries

#### [lib/libbash](lib/libbash)
* **Description**: Sourced library containing common helper functions used across bash scripts in this repository. Includes utilities for terminal output, logging, version info, checking system commands, and parsing recipe file attributes.
