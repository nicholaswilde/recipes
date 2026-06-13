# /rename-recipe <old_name> <new_name>

Rename an existing recipe in the repository, including Markdown, Cooklang, images, zensical.toml configuration, and cross-references.

## Description
This skill safely and completely renames a recipe along with all of its associated source files, image assets, Cooklang files, configuration entries, and reference links in the repository, while preserving Git version control history.

## Protocol

1. **Locate the Existing Recipe:**
   - Search `zensical.toml` to find the entry matching `<old_name>`.
   - Identify its category (e.g., `breakfast`, `desserts/cake`, `sides/potatoes`) and existing file paths.
   - Confirm the existence of:
     - **Markdown Page:** `docs/{category}/{old-slug}.md`
     - **Cooklang File:** `cook/{category}/{Old Recipe Name}.cook`
     - **Cook Image:** `cook/{category}/{Old Recipe Name}.{jpg|png|webp}`
     - **Docs Image Asset:** `docs/assets/images/{old-slug}.{jpg|png|webp}`

2. **Check for Target Conflicts:**
   - **Scan Configuration:** Search `zensical.toml` to see if an entry with `<new_name>` or target path `docs/{category}/{new-slug}.md` already exists.
   - **Scan Filesystem:** Check for existing files matching the target name in:
     - `docs/{category}/{new-slug}.md`
     - `cook/{category}/{New Name}.cook`
     - `cook/{category}/{New Name}.{jpg|png|webp}`
     - `docs/assets/images/{new-slug}.{jpg|png|webp}`
   - **Conflict Resolution Protocol:**
     - If a conflict exists (e.g., another recipe has the same name or uses the same slug), do **not** overwrite it silently.
     - Present the naming conflict details to the user (e.g., highlighting that both the source recipe and the conflicting target recipe exist).
     - Use the `ask_question` tool to present structured options for conflict resolution, such as:
       - **Option 1 (Differentiate New):** Rename the new recipe to a differentiated title (e.g., adding a prefix/suffix like "Classic" or "Scratch").
       - **Option 2 (Differentiate Existing):** Rename the existing conflicting recipe to a more specific title (e.g., appending its author/brand) to free up the exact generic name for the new recipe.
       - **Option 3 (Overwrite/Merge):** Replace/delete the existing recipe to make the new one the sole recipe under that name (only if explicitly requested).

3. **Rename Files via Git (`git mv`):**
   - Rename the files using `git mv` to preserve commit history:
     - Markdown: `git mv docs/{category}/{old-slug}.md docs/{category}/{new-slug}.md`
     - Cooklang: `git mv "cook/{category}/{Old Name}.cook" "cook/{category}/{New Name}.cook"`
     - Cook Image: `git mv "cook/{category}/{Old Name}.{jpg|png|webp}" "cook/{category}/{New Name}.{jpg|png|webp}"` (depending on the extension of the existing image)
     - Docs Image: `git mv docs/assets/images/{old-slug}.{jpg|png|webp} docs/assets/images/{new-slug}.{jpg|png|webp}`

4. **Update File Contents:**
   - **Markdown Page:** 
     - Update the title (`# :emoji: New Recipe Name`).
     - Update the image reference alt text (`![New Recipe Name][1]`).
     - Update the image link path at the bottom of the page (`[1]: <../../assets/images/{new-slug}.{jpg|png|webp}>`).
   - **Cooklang File:**
     - Update the metadata title (`>> title: New Recipe Name`).
   - **zensical.toml:**
     - Replace the old name and path with the new name and path under the correct navigation section.

5. **Update Cross-References:**
   - Search the `docs/` folder for any other files containing links or references to the old recipe path (`docs/{category}/{old-slug}.md`).
   - Update those references to point to the new path to prevent broken links.

6. **Validation & Spellcheck:**
   - Run the spellcheck-file task on the renamed markdown recipe:
     ```bash
     task spellcheck-file FILE=docs/{category}/{new-slug}.md
     ```
   - Verify there are no syntax or formatting issues.

7. **Git Commit & Push:**
   - Stage all modified files (`git add`).
   - Commit using conventional commit format (e.g., `refactor({category}): rename {Old Name} to {New Name}`).
   - Push to the remote repository.
