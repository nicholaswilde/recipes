---
name: identify-hero-images
description: >-
  Scan recipes in docs/ to identify missing, corrupt, low-resolution, or duplicate hero images
  that should be generated or synced. Trigger: /identify-hero-images, 'identify hero images',
  'find missing hero images', 'recommend hero images'.
---

# Identify Hero Images Skill

Audit recipe Markdown files under `docs/` to pinpoint hero images needing generation (missing,
corrupt/non-image, low-resolution, or duplicated across unrelated dishes) versus metadata/embed
sync fixes.

## Protocol

### 1. Run the Hero Image Audit

Execute the scanner script (reuses `scripts/check_missing_images.py` helpers plus Pillow
verification and SHA-256 hashing):

```bash
rtk uv run .agents/skills/identify-hero-images/scripts/scan_hero_images.py
```

Optional flags:

- `--min-dim 300`: Minimum pixel width/height threshold (default `300`)
- `--min-bytes 5000`: Minimum image file size in bytes (default `5000`)
- `--json`: Output machine-readable JSON for filtering or issue creation

For frontmatter/embed structural checks on `docs/` or companion-image checks on `cook/`, run:

```bash
task check-missing-images
cook-docs doctor --only images
```

---

### 2. Triage Findings

Separate results into **Generation Required** vs. **Metadata / Sync Fixes**:

1. **Generate New Hero Image** (follow the `generate-hero-image` skill):
    - **Corrupt / Non-Image Files**: Files failing `Image.verify()` (HTML error pages, 404s,
      wget logs, or text saved with image extensions).
    - **Missing Image Files**: `hero:` or body embed points to a nonexistent path.
    - **Low-Resolution Thumbnails**: Images below `--min-dim` (`<300px`) or `--min-bytes`
      (`<5 KB`).
    - **Unrelated Duplicate Hashes**: Distinct dishes sharing identical image bytes (keep shared
      images only when recipes are direct variations of the same dish).
2. **Metadata / Embed Fixes Only** (no generation needed):
    - **`NO_HERO`**: Recipe already has a valid `.webp` body embed; set `hero:` in YAML frontmatter via `mdfm`:

      ```bash
      mdfm set hero=assets/images/<slug>.webp <recipe_path>
      ```
    - **Hero vs. Embed Mismatches**: Update the body embed reference to match the dedicated
      `hero:` file.
    - **Non-WebP Images**: For `.cook`-backed recipes, place the `.jpg` beside the `.cook` file and
      run `cook-docs "<cook/path/to/Recipe.cook>"` (`convert_images = "webp"`). For Markdown-only
      recipes or bulk cleanup, run `./scripts/optimize_images.sh`.

---

### 3. Track or Generate

- **Track in GitHub**: Use the `create-issue` skill (`rtk gh issue create ... | cat`) with
  checkboxes grouped into separated sections.
- **Generate Images**: Use the `generate-hero-image` skill for prioritized recipes (starting with
  corrupt and missing files, then low-res thumbnails).

---

### 4. Verify

After generating or syncing hero images, re-run verification:

```bash
rtk uv run .agents/skills/identify-hero-images/scripts/scan_hero_images.py
task check-missing-images
task validate
```
