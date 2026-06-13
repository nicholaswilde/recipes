# Markdown Style Guide

This document outlines Markdown coding principles and style rules for this project, with a specific focus on Content Tabs.

## 1. Content Tabs

We use `pymdownx.tabbed` to implement content tabs in recipe files to handle different variations or servings.

### Syntax and Indentation

- Use `=== "Tab Label"` syntax to define a tab.
- All content inside the tab block must be indented with **4 spaces**.
- A blank line must separate the tab definition from the tab content, and separate successive tab blocks.

### Naming Conventions

- Keep tab labels short and descriptive (e.g., `"9 Inch"` or `"10 Inch"` instead of `"serves 1 9 inch cake"`).
- Capitalize the first letter of each word in the label.

### Header Nesting

- If a tab contains sections, use `###` (H3) or `####` (H4) headers.
- The headers must be indented by 4 spaces.
- Maintain consistent heading structure across all tabs within the same group.

### Multi-Section Alignment

- If a recipe variation has both unique ingredients and instructions, use separate tab blocks under
  `## :salt: Ingredients` and `## :pencil: Instructions` with matching tab labels
  (e.g., `=== "Fresh Egg Whites"` and `=== "Powdered Egg Whites"`).

### Example

```markdown
## :salt: Ingredients

=== "Fresh Egg Whites"

    - :egg: 1 large egg white
    - :candy: 0.33 cup (65 g) confectioners' sugar

=== "Powdered Egg Whites"

    - :candy: 1.33 cups (263 g) confectioners' sugar
    - :egg: 1 Tbsp powdered egg whites
```
