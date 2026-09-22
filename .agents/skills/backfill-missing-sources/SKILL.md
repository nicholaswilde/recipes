---
name: backfill-missing-sources
description: >-
  Audit recipes for missing Source sections, investigate origins via git history, issues,
  or external references, format standard source headings and links, and validate the site.
---

# Backfill Missing Recipe Sources Skill

Use this skill when auditing recipes for missing sources, investigating recipe origins,
standardizing source headings, and backfilling references across the cookbook.

## Workflow

### 1. Identify Recipes Missing Sources

Run the repository source checker:

```bash
task check-missing-sources
```

- Under the hood: runs `uv run scripts/find_missing_sources.py`.
- Excludes non-recipe files (`index.md`, `tags.md`, `README.md`, `reference/`, `assets/`).
- Scans for standard heading patterns (`## :link: Source` or `## :link: Sources`).

---

### 2. Triage & Normalize Existing Sources

Before researching external origins, check for misformatted or pre-existing source data:

1. **Heading Normalization**:
   - Fix non-standard heading levels (e.g., `### :link: Source` &rarr; `## :link: Source`).
   - Fix non-standard section titles (e.g., `## :link: References` &rarr; `## :link: Sources`).
2. **CookLang Metadata Sync**:
   - Check if the corresponding `.cook` file in `cook/` already defines source metadata:

     ```bash
     grep -E "^>> source:" cook/<category>/<recipe>.cook
     ```

   - If found in `.cook`, format and transfer the source into the markdown file.

---

### 3. Investigate Missing Recipe Origins

For recipes genuinely lacking source information, research the recipe provenance using the following hierarchy:

1. **Git Commit History**:
   - Inspect the commit that initially added or modified the recipe:

     ```bash
     rtk git log --diff-filter=A --follow -p -- docs/<path>/<recipe>.md
     ```

   - Look for commit messages like `feat: add <recipe>. Fixes #<issue>` or `Imported from <url>`.
2. **GitHub Issue & Attachments**:
   - If a GitHub issue is mentioned:

     ```bash
     rtk gh issue view <issue_number> | cat
     ```

   - If the issue contains attached images or PDFs, check image OCR (or use `tesseract` /
     `liteparse`) to extract URLs, author names, or cookbook titles.
3. **Known Original & Family Recipes**:
   - Recipes authored by Nicholas Wilde: `- Nicholas Wilde original recipe`
   - Family / friend recipes (e.g. Cindy's, Mom's): `- Cindy's Recipe Box` or `- Recipe Box`
4. **Brand / Manufacturer / Web Search**:
   - Classic branded recipes (e.g., Betty Crocker, Pillsbury, Jiffy, Todd Wilbur, Bob's Red Mill) or
     known food blogs:
     - Search for the recipe title and key distinctive ingredients/quantities.
     - Locate the canonical publisher URL.
5. **Fallback**:
   - If no specific provenance or external author is identifiable, attribute to `- Recipe Box`.

---

### 4. Standard Source Section Formatting

Adhere strictly to markdown formatting standards:

#### Single Source (with URL)

```markdown
## :link: Source

- [Publisher / Author Name][1]

<!-- Link References -->
[1]: https://example.com/recipe
```

#### Multiple Sources

```markdown
## :link: Sources

- [Primary Source Name][1]
- [Secondary Source Name][2]

<!-- Link References -->
[1]: https://example.com/recipe-1
[2]: https://example.com/recipe-2
```

#### Offline / Personal / Book Source

```markdown
## :link: Source

- Recipe Box
```

## (Or specific cookbook title / author without link)

### Positioning Rules

- The `## :link: Source` section must precede the link reference definitions (`<!-- Link References -->` or `[1]: ...`).
- Link reference definitions MUST be placed at the very end of the file.
- Keep lines wrapped cleanly without trailing whitespace.

---

### 5. Validate Changes

Run repository validation tasks to guarantee formatting and link integrity:

```bash
# Verify all recipes now contain a source section
task check-missing-sources

# Verify all links and internal anchors are valid
task linkcheck-offline

# Verify header emojis remain valid and registered
task check-header-emojis
```

---

### 6. Commit & Push

Stage and commit changes following Conventional Commits:

```bash
# Script / mapping updates (if any)
rtk git add includes/emoji.yaml scripts/check_header_emojis.py scripts/find_missing_sources.py
rtk git commit -m "chore: update emoji mappings and check scripts"

# Recipe source updates
rtk git add docs/
rtk git commit -m "docs: backfill missing recipe sources and update metadata"

# Push to remote
rtk git push
```
