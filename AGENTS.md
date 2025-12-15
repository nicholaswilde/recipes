# Project Overview

This project is a personal recipe collection managed as a documentation site using Zensical. Recipes are primarily written in a custom `.cook` format and then converted to Markdown (`.md`) files, which are then served by Zensical. The site is deployed to GitHub Pages. The project uses various tools for linting, spellchecking, and link checking to maintain quality.

# Main Technologies

*   **Zensical:** Static site generator for documentation.
*   **Zensical Material Theme:** Provides the visual theme for the documentation site.
*   **Taskfile:** A task runner for automating development and deployment workflows.
*   **Docker:** Used to containerize various development tools and the server.
*   **Cooklang:** A plain text format for writing recipes, indicated by `.cook` files and the `cook server` command.
*   **Python:** Used for Zensical and its plugins.
*   **Git:** Version control system.
*   **GitHub Actions:** For continuous integration and deployment to GitHub Pages.
*   **Pre-commit hooks:** For enforcing code quality and formatting before commits.

# Building and Running

*   **Build Docker image:** `task build`
*   **Start local development server (Docker):** `task serve` (access at `http://0.0.0.0:8000`)
*   **Start local development server (local Zensical install):** `task serve-local`
*   **Start Cooklang server:** `task server`
*   **Deploy to GitHub Pages:** The GitHub Actions workflow `ci.yaml` automatically deploys the docs on pushes to `main` branch (paths `docs/**`, `mkdocs.**`). Manually, this would involve `zensical gh-deploy --force` after installing dependencies.

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
*   **Recipe Management:** Recipes are stored in `cook/` as `.cook` files and must be organized by category in subdirectories (e.g., `cook/breakfast/`, `cook/desserts/`). There are scripts to manage these, such as `scripts/commit.sh` and `scripts/move.sh`.
*   **Markdown Formatting:** Specific formatting for images (`add-lazy-loading`) and temperatures (`deg`) is applied using `sed`.
*   **Front Matter:** Markdown files use front matter for metadata like comments and tags.
*   **Dependencies:** Python dependencies for Zensical are managed via `pip install` in the CI workflow. `spellchecker-cli` is installed globally via `npm install`.
*   **Recipe Markdown Pages:** Recipe markdown pages in `docs/` should use emoji from `includes/emoji.yaml`.
*   **Recipe Markdown Format:** Recipe markdown pages should follow a consistent format, including front matter for metadata (e.g., comments, tags), a main title with an emoji, an image with `loading=lazy`, a table for serving and time information, and sections for ingredients, cookware, and instructions. Instructions should be numbered steps, with `!!! tip` used for additional information.

# Cooklang Specification

Recipes in this project are written using the [Cooklang](https://cooklang.org/docs/spec/) specification. Here is a quick reference for creating `.cook` files:

*   **Metadata:** Defined at the top of the file using `>> key: value`. Common keys include `source`, `serves`, `total time`, `time required`, `image`, and `tags`.
    ```cook
    >> source: https://example.com/recipe
    >> serves: 4
    >> total time: 30 minutes
    ```
*   **Ingredients:** Use `@` followed by the ingredient name. If there is a quantity, use `{}`.
    *   Simple: `@salt{}`
    *   With quantity: `@water{1%cup}`
    *   With quantity (no unit): `@eggs{2}`
    *   Multi-word ingredient: `@ground beef{1%lb}`
*   **Cookware:** Use `#` followed by the cookware name.
    *   Simple: `#pan{}`
    *   Multi-word: `#frying pan{}`
*   **Timer:** Use `~` followed by the duration in `{}`.
    *   Example: `~{25%minutes}`
*   **Comments:** Use `[-` and `-]` for block comments or `--` for line comments.
    *   Example: `[- This is a comment -]`
*   **Steps:** Write instructions as natural text. Ingredients, cookware, and timers are embedded directly within the sentences.