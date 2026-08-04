# /hyperlink-ingredient-global

Globally find and add relative markdown hyperlinks to a specific ingredient in all recipe files
that mention it.

## Description

This skill automates the process of identifying all recipe files in `docs/` that use a specific
ingredient, and updating them with relative hyperlinks pointing to the ingredient's own recipe file.

## Protocol

1. **Verify the Ingredient Exists in Collection**:
   - Verify that the ingredient you want to link has its own recipe file in the repository
     (e.g. `docs/ingredients/vegetarian-terasi.md` or similar).

2. **Run the Global Hyperlink Task**:
   - Run the task runner command, specifying the exact name of the ingredient:

     ```bash
     task hyperlink-ingredient-global INGREDIENT="Sambal Oelek"
     ```

   - The script will search for the corresponding ingredient file, scan all recipes in `docs/`
     (excluding reference guides and the ingredient file itself), calculate the correct relative
     path for each file, and replace raw instances of the ingredient with the markdown link.
   - **Success**: Output lists each updated recipe with the number of occurrences replaced.

3. **Validate the Workspace**:
   - Lint the updated files and check the build:

     ```bash
     task lint-changed
     task build
     ```

4. **Commit Changes**:
   - Stage and commit the modified recipe files and push to origin:

     ```bash
     git add -A
     git commit -m "docs(recipes): Globally hyperlink '<Ingredient Name>'"
     git push
     ```
