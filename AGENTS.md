# Project Overview

This project is a personal recipe collection managed as a documentation site using MkDocs with the Material theme. Recipes are primarily written in a custom `.cook` format and then converted to Markdown (`.md`) files, which are then served by MkDocs. The site is deployed to GitHub Pages. The project uses various tools for linting, spellchecking, and link checking to maintain quality.

# Main Technologies

*   **MkDocs:** Static site generator for documentation.
*   **MkDocs Material Theme:** Provides the visual theme for the documentation site.
*   **Taskfile:** A task runner for automating development and deployment workflows.
*   **Docker:** Used to containerize various development tools and the MkDocs server.
*   **Cooklang:** A plain text format for writing recipes, indicated by `.cook` files and the `cook server` command.
*   **Python:** Used for MkDocs and its plugins.
*   **Git:** Version control system.
*   **GitHub Actions:** For continuous integration and deployment to GitHub Pages.
*   **Pre-commit hooks:** For enforcing code quality and formatting before commits.

# Building and Running

*   **Build MkDocs Docker image:** `task build`
*   **Start local development server (Docker):** `task serve` (access at `http://0.0.0.0:8000`)
*   **Start local development server (local MkDocs install):** `task serve-local`
*   **Start Cooklang server:** `task server`
*   **Deploy to GitHub Pages:** The GitHub Actions workflow `ci.yaml` automatically deploys the docs on pushes to `main` branch (paths `docs/**`, `mkdocs.**`). Manually, this would involve `mkdocs gh-deploy --force` after installing dependencies.

# Development Conventions

*   **Pre-commit hooks:**
    *   `trailing-whitespace`: Removes trailing whitespace.
    *   `end-of-file-fixer`: Ensures files end with a newline.
    *   `mixed-line-ending`: Standardizes line endings.
    *   `markdownlint`: Lints Markdown files for style and consistency.
    *   `markdown-link-check`: Checks for broken links in Markdown files.
*   **Linting:**
    *   `task lint`: Runs `markdownlint` and `yamllint`.
    *   `task markdownlint`: Runs `markdownlint-cli`.
    *   `task yamllint`: Runs `yamllint`.
*   **Spellchecking:** `task spellcheck` (uses `spellchecker-cli` with `dictionary.txt`).
*   **Link Checking:** `task linkcheck` (uses `markdown-link-check`).
*   **Recipe Management:** Recipes are stored in `cook/` as `.cook` files. There are scripts to manage these, such as `scripts/commit.sh` and `scripts/move.sh`.
*   **Markdown Formatting:** Specific formatting for images (`add-lazy-loading`) and temperatures (`deg`) is applied using `sed`.
*   **Front Matter:** Markdown files use front matter for metadata like comments and tags.
*   **Dependencies:** Python dependencies for MkDocs are managed via `pip install` in the CI workflow. `spellchecker-cli` is installed globally via `npm install`.
*   **Recipe Markdown Pages:** Recipe markdown pages in `docs/` should use emoji from `includes/emoji.yaml`.
*   **Recipe Markdown Format:** Recipe markdown pages should follow a consistent format, including front matter for metadata (e.g., comments, tags), a main title with an emoji, an image with `loading=lazy`, a table for serving and time information, and sections for ingredients, cookware, and instructions. Instructions should be numbered steps, with `!!! tip` used for additional information.