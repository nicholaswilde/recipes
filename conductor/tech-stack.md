# Tech Stack

## Core Technologies

- **Zensical:** A static site generator for documentation, used here to serve the recipe collection.
- **Cooklang:** The primary source format for recipes, enabling structured data extraction.
- **Markdown:** The intermediate format used by Zensical for rendering the final site.

## Frontend

- **MkDocs Material:** The underlying theme for Zensical, providing a responsive and modern UI.
- **Custom CSS/JS:** Utilized for specific styling and MathJax support for mathematical notations (if needed).

## Tools and Automation

- **Taskfile:** A task runner used to automate development workflows like building, serving, and linting.
- **GitHub Actions:** CI/CD platform for automated testing and deployment to GitHub Pages.
- **Recipes MCP Server:** Provides tools for scraping, formatting, and converting recipes and ingredients.
- **Docker:** Used to containerize development tools ensuring environment consistency.
- **uv:** A fast Python package manager used for managing Zensical and its dependencies.

## Quality Assurance

- **markdownlint:** For maintaining consistent Markdown style.
- **yamllint:** For validating YAML configuration files.
- **spellchecker-cli:** For project-wide spellchecking against a custom dictionary.
- **markdown-link-check:** To ensure all internal and external links are valid.
