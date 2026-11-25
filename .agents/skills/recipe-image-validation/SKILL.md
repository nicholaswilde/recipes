---
name: recipe-image-validation
description: >-
  Identify and resolve missing or corrupted images in recipe files, ensuring valid hero frontmatter and body embeds. Trigger: /recipe-image-validation, 'validate recipe images'.
---

# Recipe Image Validation Skill

This skill documents how to identify and resolve missing or corrupted images in recipe files, ensuring all recipes have
proper hero images and body embeds.

## Description

Recipes require both a `hero:` field in their frontmatter and a matching image embed in the body of the markdown
document (in the format `![Title][1]{ loading=lazy }` with `[1]: <relative_path>`). This skill guides the user through
running the checker, resolving corrupted link syntax, adding missing frontmatter/embeds, and generating new image
assets.

## Protocol

### 1. Identify Image Issues

Run the image checker command using the Taskfile runner:

```bash
task check-missing-images
```

This checks all recipe files for:

- Missing hero frontmatter (`NO_HERO`)
- Missing body image embeds (`NO_EMBED`)
- Nonexistent image files (`HERO_MISSING`)
- Link-corrupted frontmatter fields (`HERO_CORRUPT`)

---

### 2. Fix Corrupted Hero Paths

Find any `hero:` values corrupted with markdown links using `mdfm` (also enforced by `.mdfm-schema.json`):

```bash
mdfm --where 'hero contains "["' get hero docs/
```

If frontmatter paths contain markdown links (e.g. `hero: assets/images/[ricotta]...`), set the clean raw path with `mdfm` (ensuring casing matches the filename on disk):

```bash
mdfm set hero=assets/images/ricotta-fritters.webp <recipe_path>
```

---

### 3. Resolve Missing Properties & Embeds

For recipes missing properties or body embeds:

- **Missing Hero Frontmatter**: Extract the image name from the body link and set `hero:` with `mdfm`:

  ```bash
  mdfm set hero=assets/images/<filename>.<ext> <recipe_path>
  ```

- **Missing Body Image Embeds**: Insert the embed below the main title (H1) and append the reference link to the
  bottom of the file:

  ```markdown
  ![Recipe Name][3]{ loading=lazy }

  ...

  [3]: <../assets/images/<filename>.<ext>>
  ```

  *Note*: Ensure the link reference index (e.g., `[3]`) does not conflict with existing references in the document
  (like ingredient markdown links).

---

### 4. Generate Missing Images

For recipes missing an image asset entirely:

1. Propose image generation using the `generate_image` tool with a descriptive prompt.
2. Save the image in `docs/assets/images/` using the hyphenated recipe slug.
3. Optimize and convert it using the image optimizer:

   ```bash
   ./scripts/optimize_images.sh
   ```

---

### 5. Validate & Lint

Before committing, ensure all tests, linters, and spellcheckers pass:

```bash
task lint-changed
task spellcheck-file FILE=docs/<path/to/recipe>.md
task build
```
