# Specification - Expand Measuring Reference

## Overview

Add more common baking and cooking ingredients to the measurement conversion table in `docs/reference/measuring.md`
using authoritative sources (such as the King Arthur Baking Ingredient Weight Chart) to increase unit
conversion coverage.

## Functional Requirements

1. **Gather Ingredient Data:**
   - Find weights (in grams per cup/tbsp/tsp) for missing ingredients like cocoa powder, rolled oats,
     maple syrup, coconut oil, brown sugar (packed vs light), etc.
2. **Update measuring.md:**
   - Append the new items alphabetically to the tables in `docs/reference/measuring.md`.
3. **Verify:**
   - Validate markdown structure and run `rumdl check` to verify linting.

## Acceptance Criteria

- Measuring reference document is updated with new conversions.
- File compiles correctly and passes all markdown lints.
