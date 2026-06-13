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

* **Under the Hood**: Invokes [scripts/optimize-images.sh](file:///home/nicholas/git/nicholaswilde/recipes/scripts/optimize-images.sh), which converts JPEGs to `.webp` (using `cwebp` with a Python Pillow fallback to salvage truncated/corrupted JPEGs), deletes the original files, updates all Markdown recipe references, and runs `oxipng` to optimize PNG files.

---

### 3. Checkers & Generators

#### Check Recipe Emoji Mappings

To check if all ingredients or cookware used in a `.cook` recipe are registered in the central emoji list:

* **Protocol**:

  ```bash
  uv run scripts/check-recipe-emojis.py cook/category/recipe.cook
  ```

#### Regenerate Typos Configuration

When new words are added to `dictionary.txt`, regenerate the spellchecker exclusions/whitelist:

* **Protocol**:

  ```bash
  uv run scripts/generate_typos_config.py
  ```

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
