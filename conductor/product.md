# Product Definition

## Vision

This project is a personal recipe collection managed as a documentation site using Zensical. Recipes are primarily written in a custom `.cook` format and then converted to Markdown (`.md`) files, which are then served by Zensical. The site is deployed to GitHub Pages. The project uses various tools for linting, spellchecking, and link checking to maintain quality.

To create a comprehensive, easily accessible, and visually appealing personal recipe collection using modern documentation tools. The project aims to digitize and preserve culinary knowledge while leveraging the Cooklang format for structured, machine-readable recipes.

## Goals

- **Centralize Knowledge:** Consolidate recipes from various sources into a single, version-controlled repository.
- **Accessibility:** Provide a responsive, search-friendly web interface for viewing recipes on any device.
- **Standardization:** Use the Cooklang specification to ensure consistent formatting of ingredients, cookware, and timers.
- **Automation:** Utilize CI/CD pipelines to automatically build and deploy the site, ensuring content is always up-to-date.

## Target Audience

- **Primary:** Nicholas Wilde (Author/Chef).
- **Secondary:** Friends and family looking for specific recipes.
- **Tertiary:** The open-source community and home cooks interested in the recipes or the technical stack.

## Core Features

- **Recipe Management:** Cooklang-based authoring with automated conversion to Markdown.
- **Categorization:** Functional organization (e.g., Main, Sides, Desserts) with tag-based discovery for cuisines and occasions (e.g., holiday, thanksgiving).
- **Search:** Full-text search capability provided by the documentation theme.
- **Reference Charts:** Quick-reference ingredient combinations and guides (e.g., "What Goes with What" charts).
- **Visuals:** High-quality images for each recipe with lazy loading.
- **Tools:** Integrated unit conversion, spellchecking, and link checking.

## Success Metrics

- Successful build and deployment of the documentation site.
- Accurate conversion of `.cook` files to `.md`.
- Zero broken links or spelling errors in the deployed site.
