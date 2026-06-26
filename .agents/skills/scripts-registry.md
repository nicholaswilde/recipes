# Project Scripts Registry Skill

This registry outlines the purpose, inputs, and usage of the automation and utility scripts in this repository.
Agents should consult this list to avoid writing redundant logic and to ensure consistency with the repository's
workflows.

## Description

The repository contains specialized scripts for importing, moving, formatting, and checking recipes.
Running these scripts is preferred over manual edits.

---

## Script Protocols & Commands

### 1. Recipe Import, Relocation & Commit

#### Move and Stage Recipes

When a new `.cook` recipe file is compiled, relocate it to its final destination and update configuration/menus:

* **Protocol**:

  ```bash
  task move FILES="cook/category/recipe.cook"
  ```

* **Under the Hood**: Invokes [scripts/move.sh](file:///home/nicholas/git/nicholaswilde/recipes/scripts/move.sh),
  which compiles the markdown, moves images, adds navigation configuration to `zensical.toml` via
  [scripts/add-recipe-nav.py](file:///home/nicholas/git/nicholaswilde/recipes/scripts/add-recipe-nav.py),
  and runs validation.

#### Commit Recipe Changes

Once a recipe has been imported and verified, commit the changes using the conventional commit standard:

* **Protocol**:

  ```bash
  task commit FILES="cook/category/recipe.cook"
  ```

* **Under the Hood**: Invokes [scripts/commit.sh](file:///home/nicholas/git/nicholaswilde/recipes/scripts/commit.sh),
  which stages all files and prompts for the GitHub issue number to structure the commit message (e.g.
  `feat: add recipe. Fixes #123`).

#### Batch Organize Recipes (Sides / Sauces)

To batch-relocate sides and sauces to nested subfolders based on filename mappings:

* **Protocol**:

  ```bash
  uv run scripts/move_and_verify.py
  ```

#### Scrape Recipe Webpage to Cooklang

To automatically scrape a recipe from a URL, extract its title, servings, times, ingredients, and instructions,
and compile it into a CookLang `.cook` file while downloading the hero image:

* **Protocol**:

  ```bash
  uv run scripts/scrape_to_cook.py <URL> [--category <category_override>]
  ```

* **Under the Hood**: Attempts to extract JSON-LD recipe schema (`schema.org/Recipe`). If no JSON-LD schema is found,
  falls back to WordPress Recipe Maker (WPRM) HTML class extraction. It parses ISO 8601 durations, formats
  ingredients/cookware/time-ranges to CookLang syntax, automatically downloads the hero image, and auto-categorizes
  the recipe into subfolders of `cook/`.

#### Recipe Import Workflow Orchestrator

To orchestrate the entire recipe import process (scraping, moving, emoji matching, unit conversion, spellchecking, and whitelisting) in a single command execution:

* **Protocol**:

  ```bash
  uv run scripts/import_recipe_workflow.py <URL_or_issue> [category]
  ```

* **Under the Hood**: Runs `scripts/scrape_to_cook.py` to scrape the recipe from a URL or extracted URL from a GitHub issue description. Relocates it using `scripts/move.sh`, runs `scripts/check-recipe-emojis.py --fix` to verify emojis, `scripts/convert-recipe-units.py` to convert volume measurements to weight, and runs the typos spellchecker. It detects and prompts (or auto-whitelists in non-interactive modes) proper nouns flagged by the spellchecker using `scripts/whitelist_typos.py`.

#### Manual Recipe Import Orchestrator

To orchestrate the import, emoji checking/fixing, unit conversion, spelling validation, proper nouns whitelisting, and committing of manual or image-based recipes in a single command execution:

* **Protocol**:

  ```bash
  uv run scripts/import_manual_recipe.py <cook_file> [-i <image_path>] [-c <category>] [-n <issue_number>] [--commit]
  ```

* **Under the Hood**: Copies/moves the manual `.cook` and optional image file to the correct category directory inside `cook/`, runs `scripts/move.sh` to compile it to markdown and copy/convert images, runs `scripts/check-recipe-emojis.py --fix` to automatically map missing emojis, `scripts/convert-recipe-units.py` to format units and insert emojis, and runs `typos` with auto-whitelisting of proper nouns. Optionally prompts for GitHub issues and automates conventional git commits.

---

### 2. Auto-Fixers & Formatting

#### Auto-Fix Zensical Build and Link Warnings

If `zensical build` fails or outputs warnings about unused/unresolved links:

* **Protocol**:

  ```bash
  uv run scripts/zensical_fix.py
  ```

* **Under the Hood**: Runs checks, parses warnings, automatically removes unused reference links, and escapes
  unresolved bracket patterns like `[ml]`.

#### Auto-Format & Annotate Ingredient Weights

To automatically insert matching ingredient emojis and convert volumetric units (cups, tbsp) to
weight-annotated strings (grams) on a recipe's markdown file:

* **Protocol**:

  ```bash
  uv run scripts/convert-recipe-units.py docs/category/recipe.md
  ```

* **Under the Hood**: Cross-references ingredients with [includes/emoji.yaml](file:///home/nicholas/git/nicholaswilde/recipes/includes/emoji.yaml) and [docs/reference/measuring.md](file:///home/nicholas/git/nicholaswilde/recipes/docs/reference/measuring.md).

#### Auto-Fix Broken Relative Links

If Lychee checks fail or relative markdown links are broken:

* **Protocol**:

  ```bash
  uv run scripts/fix_broken_links.py
  ```

* **Under the Hood**: Automatically resolves relative markdown and image links against files in the repository.

#### Optimize and Convert Images

To convert all JPEGs to WebP, optimize PNGs, and update all Markdown recipe references globally or for a specific category:

* **Protocol**:

  ```bash
  # Globally
  bash scripts/optimize-images.sh

  # For a specific category
  bash scripts/optimize-images.sh [category]
  ```

* **Under the Hood**: Invokes [scripts/optimize-images.sh](file:///home/nicholas/git/nicholaswilde/recipes/scripts/optimize-images.sh),
  which converts JPEGs to `.webp` (using `cwebp` with a Python Pillow fallback to salvage truncated/corrupted JPEGs),
  deletes the original files, updates all Markdown recipe references, and runs `oxipng` to optimize PNG files.

#### Scale and Add Recipe Sizes

To scale recipe ingredients by a factor and append them as a new Zensical tab (e.g. `=== "Double"` or `=== "Half"`):

* **Protocol**:

  ```bash
  uv run python3 scripts/add_recipe_size.py <recipe_path> <scale_factor> "<tab_name>"
  ```

* **Under the Hood**: Invokes [scripts/add_recipe_size.py](file:///home/nicholas/git/nicholaswilde/recipes/scripts/add_recipe_size.py),
  which automatically converts plain ingredients lists to Zensical tabs (extracting the original serving size from the
  top metadata table and removing the serves column from the table) or appends the tab to existing tabs.

#### Adjust Recipe Metadata and Frontmatter

To dynamically adjust metadata, add/remove tags, or update frontmatter keys in a recipe markdown file:

* **Protocol**:

  ```bash
  uv run python3 scripts/adjust_recipe_metadata.py <recipe_path> [options]
  ```

* **Under the Hood**: Invokes [scripts/adjust_recipe_metadata.py](file:///home/nicholas/git/nicholaswilde/recipes/scripts/adjust_recipe_metadata.py),
  which uses PyYAML to parse and modify frontmatter (e.g., adding/removing tags, setting `comments` flags or
  `hero` image paths) while preserving the Markdown body.

---

### 3. Checkers & Generators

#### Check and Fix Recipe Emoji Mappings

To check if all ingredients or cookware used in a `.cook` recipe are registered in the central emoji list:

* **Protocol**:

  ```bash
  uv run scripts/check-recipe-emojis.py cook/category/recipe.cook
  ```

To automatically map and fix missing emojis in `includes/emoji.yaml` using similarity checking and fallback groups:

* **Protocol**:

  ```bash
  uv run scripts/check-recipe-emojis.py --fix cook/category/recipe.cook
  ```

* **Under the Hood**: Compares missing terms against existing emoji mappings using keyword-based heuristics (e.g. `cheese` -> `cheese_wedge`, `chili`/`pepper` -> `hot_pepper`, `onion`/`scallion` -> `tea`, `tomato`/`salsa` -> `tomato`, `cream`/`milk`/`butter` -> `glass_of_milk`, cookware containing `pan`/`skillet`/`pot`/`spoon`/`whisk` -> `bowl_with_spoon`), substring matching, word-overlap, and SequenceMatcher similarity. Confident matches are inserted under the matched emoji group, while unmatched terms fallback to generic categories (`takeout_box` for ingredients and `bowl_with_spoon` for cookware). Finally, it runs `task emoji-sort` to maintain ordering.

#### Regenerate Typos Configuration

When new words are added to `dictionary.txt`, regenerate the spellchecker exclusions/whitelist:

* **Protocol**:

  ```bash
  uv run scripts/generate_typos_config.py
  ```

#### Whitelist and Sort Typos Dictionary

To whitelist one or more words in `dictionary.txt`, sort the dictionary alphabetically and uniquely,
and automatically regenerate the spellcheck configuration:

* **Protocol**:

  ```bash
  uv run scripts/whitelist_typos.py <word1> [word2] ...
  ```

* **Under the Hood**: Appends the new words to `dictionary.txt`, performs an alphabetical sort and
  unique deduplication (`sort -u`), writes the sorted file back, and programmatically executes
  `scripts/generate_typos_config.py` to rebuild `_typos.toml`.

#### Identify Multi-Serving Recipes

To locate recipes that have multiple servings tabs/tables (multiple "Ingredients" headings):

* **Protocol**:

  ```bash
  uv run scripts/identify_multi_serving.py [directory]
  ```

#### Scan and Resolve Duplicate Issues

To find and optionally close duplicate GitHub issues that correspond to already-imported recipes:

* **Protocol**:

  ```bash
  uv run scripts/find_duplicate_issues.py [--close]
  ```

#### Sync Giscus Comments Flag

To verify which recipes have comments and append `comments: true` to their front-matter:

* **Protocol**:

  ```bash
  uv run scripts/sync_giscus_comments.py
  ```
