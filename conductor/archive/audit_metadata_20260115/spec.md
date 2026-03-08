# Specification: Audit and Update Recipe Metadata

## Overview

This track aims to bring all existing recipes in the collection into compliance with the newly established Product Guidelines. This ensures consistency across the entire digital cookbook, improving both the authoring experience and the final user-facing site.

## Goals

- **Consistency:** Standardize units, emojis, and formatting across all 700+ recipes.
- **Enhanced Data:** Ensure every recipe has accurate tags and source information.
- **Usability:** Add gram conversions for all major ingredients to improve recipe accuracy for users.
- **Performance:** Ensure all images are optimized with lazy loading.

## Requirements

### 1. Metadata Standardization

- Every recipe Markdown file must have a `tags` field in the front matter.
- Every recipe Markdown file must have a `source` field in the front matter (if known).

### 2. Formatting Standardization

- **Emoji:** Ingredients in Markdown files must use emoji shortcodes from `includes/emoji.yaml`.
- **Units:** `.cook` files should use `Tbsp` for tablespoons and `tsp` for teaspoons.
- **Images:** Markdown images must include `loading="lazy"`.

### 3. Gram Conversions

- Major ingredients (flour, sugar, etc.) in Markdown files must include gram conversions in parentheses following the volume (e.g., `2 cups (240 g) all-purpose flour`).
- Use `docs/reference/measuring.md` as the primary reference for conversions.

### 4. Quality Assurance

- All modified files must pass `markdownlint` and `yamllint`.
- No broken links or spelling errors should be introduced.

## Success Criteria

- 100% of recipes have tags.
- 100% of recipe ingredients use emoji shortcodes.
- All major volumetric measurements have corresponding gram conversions.
- Site build completes successfully with no linting errors.
