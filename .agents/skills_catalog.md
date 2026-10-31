# Agent Skills Catalog

Catalog of custom Antigravity agent skills available in `recipes`.

| Skill | Description | Task / Command |
|---|---|---|
| [`backfill-missing-sources`](skills/backfill-missing-sources/SKILL.md) | Audit recipes for missing Source sections, investigate origins, format standard source headings and links, and validate the site | `uv run scripts/audit_missing_sources.py` |
| [`fix-failed-workflows`](skills/fix-failed-workflows/SKILL.md) | Diagnose and resolve failed GitHub Actions workflow runs (Documentation, spellcheck, link-check, zensical build, TOML decode errors, CookLang validation, and linting) | `task lint` / `task validate` |
| [`import-recipe`](skills/import-recipe/SKILL.md) | Import a recipe from a URL, GitHub issue, image, PDF, or YouTube video into the collection: scrape or OCR, draft CookLang, handle hero images, compile, validate, and commit | `FILES=<path> task move` / `/import-recipe` |
