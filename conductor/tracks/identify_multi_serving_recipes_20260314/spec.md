# Specification - Identify Recipes with Multiple Serving-Sized Ingredient Lists

## Overview
The goal of this track is to scan all recipe Markdown files in the `docs/` directory to identify those that list ingredients multiple times for different sized servings. These recipes are characterized by having multiple "Ingredients" headers (e.g., "## Ingredients - 1lb", "## Ingredients - 2lb"). The result of this track will be a comprehensive list of these files, which will be used in a subsequent track to convert them to use Zensical tabs.

## Functional Requirements
1.  **Recursive Scan:** Scan all `.md` files within the `docs/` directory and its subdirectories.
2.  **Pattern Identification:** Identify files that contain more than one occurrence of a header starting with "Ingredients" (e.g., matching the pattern `## :salt: Ingredients`).
3.  **List Generation:** Create a list of the relative file paths for all identified recipes.
4.  **Task Documentation:** Update this specification (or the implementation plan) with the final list of identified recipes.

## Non-Functional Requirements
- **Accuracy:** Ensure all recipes with multiple "Ingredients" headers are captured.
- **Efficiency:** Use optimized search tools (like `grep` or `ripgrep`) to perform the scan.

## Acceptance Criteria
- [ ] A complete list of all recipe files in `docs/` containing multiple "Ingredients" headers is generated.
- [ ] The list is documented within the track artifacts (specifically in the `spec.md` file).

## Out of Scope
- Converting the identified recipes to use Zensical tabs.
- Updating the content of the identified Markdown files.
