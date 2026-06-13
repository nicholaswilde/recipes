# /hyperlink-ingredient

Automatically find and add relative markdown hyperlinks to specific ingredients mentioned
in recipe files.

## Description

This skill automates the process of finding the correct recipe/ingredient file in `docs/`,
calculating the relative path, and replacing unlinked occurrences of the ingredient name
in a target recipe with markdown links.

## Protocol

1. **Verify the Ingredient Exists in Collection**:
   - Verify that the ingredient you want to link has an existing recipe file in the repository
     (e.g. `docs/ingredients/vegetarian-terasi.md` or similar). If it doesn't, create/import it first.

2. **Run the Hyperlink Task**:
   - Run the task runner command, specifying the target recipe file and the exact name of the ingredient:

     ```bash
     task hyperlink-ingredient TARGET=docs/path/to/recipe.md INGREDIENT="Sambal Oelek"
     ```

   - The script will search for the corresponding ingredient file in `docs/` (matching by slugified filename
     or the H1 title), calculate the relative path, and replace raw text instances of the ingredient with the link.
   - **Success**: Output shows "Successfully hyperlinked..." and the number of occurrences replaced.
   - **No Occurrences**: Output shows "No unlinked occurrences...". This means the ingredient is already linked or not found.

3. **Validate the File**:
   - Lint the updated file and check the build:

     ```bash
     task lint-changed
     task build
     ```

4. **Commit Changes**:
   - Stage and commit the modified recipe file following conventional commit standards.
