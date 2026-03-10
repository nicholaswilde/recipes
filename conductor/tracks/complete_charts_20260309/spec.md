# Specification: Complete Julia Turshen's "What Goes with What" Charts

## Overview
This track involves completing the "What Goes with What" charts from Julia Turshen's book in `docs/reference/charts.md`. This includes adding all remaining charts identified in issue #1331 and potentially refining the format for better readability and mobile experience.

## Functional Requirements
- **Complete Missing Charts:** Add content for the following sections as specified in issue #1331:
    - Non-lettuce salads
    - Sandwiches
    - Stovetop Vegetables
    - Roasted Vegetables
    - Stuffed Vegetables
    - Brothy Soups
    - Beans
    - Pureed Soups
    - Stews
    - Braises
    - One-pot Rice Dishes
    - Grain Bowls
    - Quick Pastas
    - Meatballs
    - Sheet Pan Dinners
    - Savory Pies
    - One-Bowl Batters
    - Menu Suggestions
- **Fix Existing Charts:** Review and correct any inaccuracies or formatting issues in the existing charts (Fruity Cobblers & Crisps, Salad Dressings, Salads with Lettuce).
- **New Formatting:** Implement a "New Format" for the charts to improve readability, especially on mobile devices. This might involve nested lists, specific CSS classes, or a more compact table structure.

## Non-Functional Requirements
- **Mobile Experience:** The new format must be responsive and easy to read on mobile devices.
- **Consistency:** Maintain a consistent style across all charts.
- **Maintainability:** Use clean Markdown/HTML that is easy to update.

## Acceptance Criteria
- All 20 charts from Julia Turshen's book are present in `docs/reference/charts.md`.
- All charts follow the agreed-upon "New Format".
- The file passes `task lint` and `task spellcheck`.
- The site builds correctly and the charts are rendered as expected.

## Out of Scope
- Adding recipes related to the charts (unless explicitly requested as a separate track).
- Major redesign of the documentation theme.
