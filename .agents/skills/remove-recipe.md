# /remove-recipe <args>

Remove a recipe from the repository, including Markdown, Cooklang, images, cross-references, and navigation entries.

## Description

This skill safely and completely removes a recipe and all of its associated source files, images, configurations, and reference links from the repository.

## Protocol

1. **Locate the Recipe:**
   - Search `zensical.toml` for the exact entry matching `<args>`.
   - If not found in `zensical.toml`, search the `cook/` and `docs/` directories for filenames matching `<args>`.
   - Identify the category and the Markdown file path (e.g., `main/banh-mi-sandwich.md`).

2. **Collect Paths:**
   - **Markdown Page:** `docs/{path_from_zensical}` (e.g., `docs/main/banh-mi-sandwich.md`).
   - **Cooklang File:** `cook/{category}/{Recipe Name}.cook`.
   - **Cook Image:** Check for `cook/{category}/{Recipe Name}.{jpg|png|jpeg|webp}`.
   - **Site Asset Image:** Check for `docs/assets/images/{recipe-slug}.{jpg|png|jpeg|webp}` (and optionally check `site/` or other build assets).

3. **Check for Cross-References:**
   - Run a search across `docs/` for any links referencing the markdown file (e.g., `[1]: ../{category}/{recipe-slug}.md`).
   - Update those referring files to point to correct alternatives or remove the broken links to prevent dead link warnings.

4. **Removal Process:**
   - **Git Remove:** Delete all collected files via git staging (`git rm`).
   - **Update zensical.toml:** Remove the specific entry line from the `zensical.toml` file. Stage `zensical.toml` and any modified files with cross-reference updates.

5. **Validation & Verification:**
   - Run `task spellcheck-file` or `task lint` on any files modified during cross-reference cleanup to ensure no formatting or link validation issues arise.

6. **Git Commit & Push:**
   - Commit the deletion with a clear, conventional commit message (e.g., `refactor: remove {recipe_name} recipe`).
   - Push to the remote repository if requested.

## Safety Checks

- Verify file existence before attempting removal.
- If the recipe name is ambiguous or matches multiple entries, ask the user to clarify.
- Do not delete shared images that are also referenced by other active recipes.
