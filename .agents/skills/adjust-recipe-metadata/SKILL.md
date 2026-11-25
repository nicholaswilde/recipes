---
name: adjust-recipe-metadata
description: >-
  Adjust recipe metadata, tags, and frontmatter dynamically on recipe markdown files using mdfm. Trigger: /adjust-recipe-metadata, 'adjust recipe metadata', 'update recipe tags'.
---

# Adjust Recipe Metadata

This skill automates querying, modifying, deleting, and validating recipe frontmatter metadata and tags using [`mdfm`](https://github.com/nicholaswilde/mdfm).

## Description

Use `mdfm` (configured via `.mdfm.toml` and `.mdfm-schema.json`) to add/remove tags, update frontmatter keys (`comments`, `hero`, `source`, etc.), run filtered bulk updates with `--where`, and validate schema compliance without disturbing the Markdown body.

## Protocol

1. **Mutate or Query Frontmatter with `mdfm`**:

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

   **Set or delete metadata keys:**

   ```bash
   # Set comments flag and hero image path
   mdfm set comments=false hero=assets/images/new-hero.webp docs/breakfast/overnight-oats.md

   # Enable comments via Taskfile
   task add-comments -- docs/breakfast/overnight-oats.md

   # Delete a frontmatter key
   mdfm del legacy_key docs/breakfast/overnight-oats.md
   ```

   **Query or preview bulk edits with `--where` and `--dry-run`:**

   ```bash
   # List untried must-try recipes (excluding favorites)
   mdfm --where 'tags contains "must-try" and not (tags contains "favorite")' get tags docs/

   # Preview a bulk tag update before writing
   mdfm --where 'tags contains "applied-kitchen"' set --dry-run tags+=quick docs/
   ```

2. **Verify and Lint**:

   - Validate frontmatter schema and changed files:

     ```bash
     mdfm check <recipe_path>
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
