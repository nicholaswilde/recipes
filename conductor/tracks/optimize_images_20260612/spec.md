# Specification: Image Optimization and WebP Conversion

## Overview
This track introduces image optimization and WebP conversion for all recipe images in the repository. It includes:
1. A one-time migration script `scripts/optimize-images.sh` to convert all existing `.jpg` images to `.webp` using `cwebp`, optimize all `.png` images in-place using `oxipng`, and update all corresponding image references in existing Markdown files under `docs/`.
2. Updates to the recipe import workflow (`scripts/move.sh`) to automatically convert incoming `.jpg` images to `.webp` and optimize them, as well as rewriting markdown references accordingly.
3. Reporting of the total space savings (in percentage and bytes) after the migration.

## Functional Requirements
- **Migration Script (`scripts/optimize-images.sh`):**
  - Check for the availability of `cwebp` and `oxipng` and exit gracefully with instructions if they are missing.
  - Process all `.jpg` files in `docs/assets/images/`:
    - Convert them to `.webp` with quality 80 and metadata preserved (`cwebp -q 80 -metadata all <input> -o <output>`).
    - Accumulate original and compressed file sizes.
    - Delete the original `.jpg` file upon successful conversion.
  - Process all `.png` files in `docs/assets/images/`:
    - Optimize in-place using `oxipng -o 4 --strip safe <file>`.
    - Accumulate original and optimized file sizes.
  - Update all Markdown files under `docs/` to replace references to `.jpg` with `.webp` (specifically updating lines like `[1]: <../assets/images/recipe-name.jpg>` or `hero: assets/images/recipe-name.jpg` to use `.webp`).
  - Print the total space savings in percentage and in bytes.
- **Workflow Script (`scripts/move.sh` & `scripts/lib/libbash`):**
  - Update the recipe movement flow so that when an image is moved/copied from a `.cook` category folder into `docs/assets/images/`:
    - If the image is a `.jpg`, convert it to `.webp` using `cwebp` and delete the original `.jpg` in the destination.
    - If the image is a `.png`, optimize it using `oxipng`.
    - Modify the generated Markdown file under `docs/` to point to the new `.webp` image extension instead of `.jpg`.

## Non-Functional Requirements
- Conversion and optimization must preserve standard image quality and metadata (e.g. ICC profiles, EXIF).
- Graceful error handling for missing binaries (`cwebp`, `oxipng`).

## Acceptance Criteria
- All existing `.jpg` images in `docs/assets/images/` are successfully converted to `.webp`.
- All existing `.png` images are optimized.
- All Markdown files in `docs/` correctly reference `.webp` files instead of `.jpg`.
- `task move` successfully converts and optimizes any new recipe images and outputs valid Markdown references.
- Running `task linkcheck-offline` succeeds with zero errors.
- Output includes total space savings.

## Out of Scope
- Modifying image assets in other directories (e.g., `.git/` or `site/` or `scratch/`).
