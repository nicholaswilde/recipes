# /recipe-servings-tabs

Search for recipes with multiple `serves X` headers or multiple ingredient groups for different batch/serving sizes and convert them to Zensical tabs.

## Description
This skill automates and documents the process of converting multi-serving/batch-size ingredient lists into Zensical tab blocks (e.g. `=== "serves X"`, `=== "Full Batch"`, `=== "Half Batch"`), formatting the items with the correct 4-space nested indentation, and resolving any markdown link reference issues that arise inside tab blocks.

## Protocol
1. **Identify Candidate Files:**
   - Scan the `docs/` folder for files containing more than one occurrence of the Serves table header: `| :fork_and_knife_with_plate: Serves |` (or minor spacing variations).
   - Also search for files containing wording like `full batch`, `half batch`, or `double batch` (case-insensitive) in headers, table contents, or recipe text to locate other recipes offering multiple batch sizes.
   - Filter out files where the multiple tables represent distinct components of a single recipe (e.g. Dough vs. Filling vs. Glaze) rather than separate batch/serving sizes of the same recipe.
2. **Determine Tab Names:**
   - Use `Full Batch` and `Half Batch` (Title Case) for recipes defined in batches (e.g. `1/2 Batch`, `2 loaves`, `2 dozen large muffins`).
   - Use `serves X` (lowercase `serves`) where `X` is a numeric count or range of servings (e.g. `serves 6`, `serves 12`).
3. **Format Zensical Tabs:**
   - Group the ingredients list for each serving size under Zensical tabs.
   - Example tab syntax:
     ```markdown
     === "serves 6"

         - :banana: 0.5 cup (1) banana
         - :glass_of_milk: 1 cup (227 g) soy milk
     ```
   - Make sure all list elements (and any subheaders) inside the tab blocks are indented by exactly 4 spaces.
4. **Convert Reference-Style Links:**
   - Standard markdown linters (like `markdownlint`) do not parse link reference definitions (e.g., `[1]: <url>`) correctly if they are only referenced inside custom extension blocks like tabs.
   - If any ingredient uses reference-style links inside a tab block (e.g., `[peanut butter][1]`), convert them to inline links (e.g., `[peanut butter](../ingredients/peanut-butter.md)`) and delete the reference definitions from the bottom of the file.
5. **Verify and Lint:**
   - Validate the modified files by running the targeted linter:
     ```bash
     npx markdownlint-cli --config .markdownlint.yaml path/to/recipe.md
     ```
   - Ensure `task validate` passes successfully.
