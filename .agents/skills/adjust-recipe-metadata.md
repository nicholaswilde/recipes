---
name: adjust-recipe-metadata
description: >-
  Adjust recipe metadata, tags, and frontmatter dynamically on recipe markdown files using mdfm. Trigger: /adjust-recipe-metadata, 'adjust recipe metadata', 'update recipe tags'.
---

# Adjust Recipe Metadata

This skill automates querying, modifying, deleting, and validating recipe frontmatter metadata and tags using [`mdfm`](https://github.com/nicholaswilde/mdfm).

## Description

Use `mdfm` (configured via `.mdfm.toml` with `extensions`, per-glob `[[schemas]]`, `errors_only = true`, and `sort_arrays = ["tags"]`) to add/remove tags, update/rename/delete frontmatter keys, format frontmatter, audit key/value taxonomies, run filtered bulk updates with `--where` / `--diff`, and validate schema compliance across `docs/` and `cook/` without disturbing document bodies.

## Protocol

1. **Mutate, Format, or Query Frontmatter with `mdfm`**:

   **Add / remove tags (deduplicated):**

   ```bash
   # Add one or more tags
   mdfm set tags+=healthy tags+=quick docs/breakfast/overnight-oats.md
   # Or via Taskfile:
   task add-tag -- quick docs/breakfast/overnight-oats.md

   # Remove tags (or promote must-try -> favorite)
   mdfm set tags-=must-try tags+=favorite docs/breakfast/overnight-oats.md
   # Or via Taskfile:
   task remove-tag -- must-try docs/breakfast/overnight-oats.md
   ```

   **Set, rename/merge, delete, or format metadata keys:**

   ```bash
   # Set comments flag and hero image path
   mdfm set comments=false hero=assets/images/new-hero.webp docs/breakfast/overnight-oats.md

   # Enable comments via Taskfile
   task add-comments -- docs/breakfast/overnight-oats.md

   # Rename or merge a frontmatter key across files (preview with --dry-run --diff)
   mdfm mv --merge --dry-run --diff serves servings docs/

   # Delete a frontmatter key
   mdfm del legacy_key docs/breakfast/overnight-oats.md

   # Format frontmatter and sort/deduplicate tags (uses sort_arrays in .mdfm.toml)
   mdfm fmt --diff docs/breakfast/overnight-oats.md
   ```

   **Query, audit taxonomies, or preview bulk edits (`-l`, multi-key `get`, `--where`, `--diff`):**

   ```bash
   # List untried must-try recipes (file paths only, excluding favorites)
   mdfm --where 'tags contains "must-try" and not (tags contains "favorite")' -l get . docs/

   # Inspect multiple keys at once
   mdfm get hero,tags docs/breakfast/

   # Audit frontmatter keys or tag usage across docs/ or cook/
   mdfm keys docs/
   mdfm values tags docs/
   mdfm --where 'has_frontmatter' keys cook/

   # Filter by optional key presence/absence (missing keys evaluate as null in == / !=)
   mdfm --where '`prep time` != null' -l get . cook/
   mdfm --where 'source == null' -l get . docs/

   # Preview a bulk tag update with unified diff before writing
   mdfm --where 'tags contains "applied-kitchen"' set --dry-run --diff tags+=quick docs/
   ```

2. **Verify and Lint**:

   - Validate frontmatter schemas (automatically resolves recipe, reference, and `.cook` schemas via `[[schemas]]`) and changed files:

     ```bash
     mdfm check <recipe_path>
     task lint:frontmatter
     task lint-changed
     task validate
     ```

   - Run `task build` when making broad metadata or tag changes.

3. **Commit the changes**:

   Commit the changes following standard commit guidelines:

   ```bash
   rtk git add <recipe_path>
   rtk git commit -m "docs(recipes): adjust metadata for <recipe_name>"
   ```
