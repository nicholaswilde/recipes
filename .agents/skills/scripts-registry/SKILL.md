---
name: scripts-registry
description: >-
  Registry of automation and utility scripts in recipes repository for importing, formatting, moving, and checking recipes. Trigger: /scripts-registry, 'scripts registry'.
---

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
  which validates syntax and ignored ingredients via `cook-docs doctor --only syntax,ignored`, compiles directly into
  `docs/` via `cook-docs` (configured in `.cookdocs.toml` + `cook/recipe.md.gotmpl` for frontmatter, `[category_tags]`,
  H1 `titleEmoji`, emojis from `includes/emoji.yaml`, gram weights from `includes/weights.yaml`, ingredient & step
  cross-links, JPEG-to-WebP image conversion, non-destructive `--merge` unless `-f`/`--force`, and `zensical.toml`
  navigation sync), runs Pillow fallback / `oxipng` PNG optimization when needed, formats with `rumdl`, and runs
  spell/link validation.

#### Commit Recipe Changes

Once a recipe has been imported and verified, commit the changes using the conventional commit standard:

* **Protocol**:

  ```bash
  task commit FILES="cook/category/recipe.cook"
  ```

* **Under the Hood**: Invokes [scripts/commit.sh](file:///home/nicholas/git/nicholaswilde/recipes/scripts/commit.sh),
  which stages all files and prompts for the GitHub issue number to structure the commit message (e.g.
  `feat: add recipe. Fixes #123`).

#### Scrape Recipe Webpage or YouTube Video to Cooklang

To automatically scrape a recipe from a webpage URL or YouTube video (full URL or standalone video ID like `V0ki4Il9Npc` / `V0ki4Il9Npc&`), extract its title, servings, times, ingredients, and instructions,
and compile it into a CookLang `.cook` file while downloading the hero image:

* **Protocol**:

  ```bash
  uv run scripts/scrape_to_cook.py <URL_or_video_ID> [--category <category_override>]
  ```

* **Under the Hood**: For YouTube URLs or video IDs, delegates to [scripts/youtube_recipe.py](file:///home/nicholas/git/nicholaswilde/recipes/scripts/youtube_recipe.py) to read video descriptions for ingredients/quantities and uses `youtube-transcript-api` to read captions and determine recipe steps. For webpages, attempts to extract JSON-LD recipe schema (`schema.org/Recipe`). If no JSON-LD schema is found, falls back to WordPress Recipe Maker (WPRM) HTML class extraction. It parses ISO 8601 durations, formats ingredients/cookware/time-ranges to CookLang syntax, automatically downloads the hero image, and auto-categorizes the recipe into subfolders of `cook/`.

#### Recipe Import Workflow Orchestrator

To orchestrate the entire recipe import process (scraping from a URL, YouTube video ID, or GitHub issue, moving, emoji matching, unit conversion, spellchecking, and whitelisting) in a single command execution:

* **Protocol**:

  ```bash
  uv run scripts/import_recipe_workflow.py <URL_video_ID_or_issue> [category]
  ```

* **Under the Hood**: Runs `scripts/scrape_to_cook.py` to scrape the recipe from a URL, YouTube video ID, or extracted URL from a GitHub issue description. Maps missing emojis with `scripts/check_recipe_emojis.py --fix`, compiles and organizes via `scripts/move.sh` (`cook-docs` handles frontmatter, emojis, gram weights, cross-links, asset copy, and merge), and runs the typos spellchecker. It detects and prompts (or auto-whitelists in non-interactive modes) proper nouns flagged by the spellchecker using `scripts/whitelist_typos.py`.

#### Manual Recipe Import Orchestrator

To orchestrate the import, emoji checking/fixing, `cook-docs` compilation, spelling validation, proper nouns whitelisting, and committing of manual or image-based recipes in a single command execution:

* **Protocol**:

  ```bash
  uv run scripts/import_manual_recipe.py <cook_file> [-i <image_path>] [-c <category>] [-n <issue_number>] [--commit]
  ```

* **Under the Hood**: Copies/moves the manual `.cook` and optional image file to the correct category directory inside `cook/`, maps missing emojis via `scripts/check_recipe_emojis.py --fix`, runs `scripts/move.sh` (`cook-docs`) to compile enriched Markdown and copy/convert images, and runs `typos` with auto-whitelisting of proper nouns. Checks if the corresponding GitHub issue requested a hero image (`Generate hero image` checkbox) and warns if missing. Optionally prompts for GitHub issues and automates conventional rtk git commits.

#### Automated PDF Recipe Import Workflow

To automate the download, text parsing, hero image cropping, and CookLang skeleton generation of a PDF-based recipe:

* **Protocol**:

  ```bash
  uv run python3 scripts/import_pdf_workflow.py <PDF_URL_or_path> [-c <category>] [-n <issue_number>] [--commit]
  ```

* **Under the Hood**: Automatically downloads a PDF (if remote) silently to save logs, runs `lit parse` from the `liteparse` skill to extract text, renders the first page using `lit screenshot`, auto-crops the main hero image from the right/top section of the page using Pillow color-variance detection, checks if the GitHub issue requested a generated hero image (`Generate hero image` checkbox), and initializes a draft `.cook` file containing the raw extracted text as comments. It then prepares the final `import_manual_recipe.py` command for verification and final staging.

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

#### Sync Weights Table for `cook-docs`

When `docs/reference/measuring.md` is updated, regenerate `includes/weights.yaml` so `cook-docs` uses the new gram densities during compilation:

* **Protocol**:

  ```bash
  task sync-weights
  # or directly:
  uv run scripts/sync_weights_yaml.py
  ```

* **Under the Hood**: Parses the Ingredient Weight Chart in [docs/reference/measuring.md](file:///home/nicholas/git/nicholaswilde/recipes/docs/reference/measuring.md) and writes [includes/weights.yaml](file:///home/nicholas/git/nicholaswilde/recipes/includes/weights.yaml) for `cook-docs` (`toGrams`).

#### Re-Compile & Merge Recipes with `cook-docs`

`cook-docs` reads [.cookdocs.toml](file:///home/nicholas/git/nicholaswilde/recipes/.cookdocs.toml) (`merge = true`) and [cook/recipe.md.gotmpl](file:///home/nicholas/git/nicholaswilde/recipes/cook/recipe.md.gotmpl) to render emojis, gram weights, cross-links, and frontmatter while preserving manual Markdown edits (`!!!` admonitions, custom sections, frontmatter tags, H1 emoji, formatted sources, manual `===` tabs):

* **Protocol**:

  ```bash
  # Re-compile a single recipe safely (non-destructive merge)
  cook-docs "cook/<category>/<Recipe Name>.cook"

  # Live watch mode while editing .cook files
  task watch

  # Validate config, templates, syntax, images, and emojis
  task doctor
  ```

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
  bash scripts/optimize_images.sh

  # For a specific category
  bash scripts/optimize_images.sh [category]
  ```

* **Under the Hood**: Invokes [scripts/optimize_images.sh](file:///home/nicholas/git/nicholaswilde/recipes/scripts/optimize_images.sh),
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

To query, mutate, rename, format, audit, or validate frontmatter keys and tags in recipe Markdown and Cooklang files (replaces the removed `scripts/adjust_recipe_metadata.py`):

* **Protocol**:

  ```bash
  # Add/remove tags (deduplicated), rename/merge keys, or format frontmatter
  mdfm set tags+=healthy tags+=quick <recipe_path>
  mdfm set --diff tags-=must-try tags+=favorite <recipe_path>
  mdfm set comments=true hero=assets/images/<slug>.webp <recipe_path>
  mdfm mv --merge --dry-run --diff serves servings docs/
  mdfm del <key> <recipe_path>
  mdfm fmt --diff <recipe_path>

  # Query, audit taxonomies, or preview filtered bulk edits
  mdfm --where 'tags contains "must-try" and not (tags contains "favorite")' -l get . docs/
  mdfm get hero,tags docs/breakfast/
  mdfm keys docs/
  mdfm values tags docs/
  mdfm --where 'tags contains "applied-kitchen"' set --dry-run --diff tags+=quick docs/

  # Validate docs/ and cook/ frontmatter schemas (per-glob [[schemas]] in .mdfm.toml)
  task lint:frontmatter
  ```

* **Under the Hood**: Uses [`mdfm`](https://github.com/nicholaswilde/mdfm) (`task add-comments`, `task add-tag`, `task remove-tag`, `task lint:frontmatter`), preserving bodies byte-for-byte, formatting YAML lists/sorting tags (`sort_arrays = ["tags"]`), and skipping no-op writes.

---

### 3. Checkers & Generators

#### Check and Fix Recipe Emoji Mappings

To check if all ingredients or cookware used in a `.cook` recipe are registered in the central emoji list:

* **Protocol**:

  ```bash
  uv run scripts/check_recipe_emojis.py cook/category/recipe.cook
  ```

To automatically map and fix missing emojis in `includes/emoji.yaml` using similarity checking and fallback groups:

* **Protocol**:

  ```bash
  uv run scripts/check_recipe_emojis.py --fix cook/category/recipe.cook
  ```

* **Under the Hood**: Compares missing terms against existing emoji mappings using keyword-based heuristics (e.g. `cheese` -> `cheese_wedge`, `chili`/`pepper` -> `hot_pepper`, `onion`/`scallion` -> `tea`, `tomato`/`salsa` -> `tomato`, `cream`/`milk`/`butter` -> `glass_of_milk`, cookware containing `pan`/`skillet`/`pot`/`spoon`/`whisk` -> `bowl_with_spoon`), substring matching, word-overlap, and SequenceMatcher similarity. Confident matches are inserted under the matched emoji group, while unmatched terms fallback to generic categories (`takeout_box` for ingredients and `bowl_with_spoon` for cookware). Finally, it runs `task emoji-sort` to maintain ordering.

#### Check and Fix Recipe Header Emojis

To verify that recipe Markdown H1 headers include valid emoji shortcodes (e.g. `# :pie: Recipe Name`):

* **Protocol**:

  ```bash
  # Check only
  task check-header-emojis
  # or directly:
  uv run scripts/check_header_emojis.py

  # Auto-fix missing header emojis based on category and ingredients
  task check-header-emojis -- --fix
  # or directly:
  uv run scripts/check_header_emojis.py --fix
  ```

* **Under the Hood**: Parses all recipe markdown files under `docs/`, checks if the H1 header begins with an emoji shortcode `:<name>:`. With `--fix`, matches against `[emoji.titles]` and `[emoji.categories]` loaded from `.cookdocs.toml` (plus `includes/emoji.yaml`) and prepends the emoji shortcode directly to the Markdown H1.

#### Check and Backfill Missing Recipe Sources

To check for recipes missing a `## :link: Source` section or backfill recipe provenance:

* **Protocol**:

  ```bash
  task check-missing-sources
  # or directly:
  uv run scripts/find_missing_sources.py
  ```

* **Under the Hood**: Invokes [scripts/find_missing_sources.py](file:///home/nicholas/git/nicholaswilde/recipes/scripts/find_missing_sources.py),
  which scans all markdown recipe files under `docs/` (excluding `index.md`, `tags.md`, `README.md`,
  `reference/`, and `assets/`) for `## :link: Source` or `## :link: Sources`. For detailed investigation
  and backfilling instructions, consult the `backfill-missing-sources` skill.

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

#### Rank Recipes (Bayesian)

To calculate the Bayesian average for a set of recipe search results (rating/votes) to rank them:

* **Protocol**:

  ```bash
  uv run scripts/rank_recipes_bayesian.py --input recipes_to_rank.json --min-votes 10 --prior-rating 3.5
  ```

#### Rank Recipe URLs (Bayesian URL Scraper)

To fetch a list of recipe URLs, extract their structured rating metadata, and rank them objectively:

* **Protocol**:

  ```bash
  uv run scripts/rank_recipe_urls.py <URL1> <URL2> ... [--min-votes 10] [--prior-rating 3.5]
  ```

#### Find Low-Ranked Recipes (Bayesian Scanner)

To scan the repository's recipes, parse their rating metadata, and flag low-scoring entries with suggested search replacements:

* **Protocol**:

  ```bash
  uv run scripts/find_low_ranked_recipes.py [--threshold 4.4] [--min-votes 10] [--prior-rating 3.5]
  ```
