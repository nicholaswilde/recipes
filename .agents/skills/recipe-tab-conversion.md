# /recipe-tab-conversion

Convert recipes with multiple ingredients/instructions headers (e.g., Dough and Glaze, or 9-inch and 10-inch) to use Zensical Content Tabs (`pymdownx.tabbed`).

## Protocol

1. **Identify Candidates**:
   - Locate recipes with multiple ingredients headers:
     ```bash
     uv run scripts/identify_multi_serving.py
     ```

2. **Convert to Tabs**:
   - **For different serving/batch sizes**: Use the automated size scaling script:
     ```bash
     uv run python3 scripts/add_recipe_size.py <recipe_path> <scale_factor> "<tab_name>"
     ```
   - **For different components (e.g. Dough vs. Glaze)**: Manually wrap them in tabs following the 4-space indentation standard:
     ```markdown
     === "Dough"

         - :salt: 1 tsp salt

     === "Glaze"

         - :sweet_potato: 1 cup sugar
     ```

3. **Verify and Validate**:
   - Check tab indentation (exactly 4 spaces) and link references (convert reference links inside tabs to inline links).
   - Run `rumdl check <recipe_path>`, `task lint-changed`, and `task validate`.
   - Run `task build` to ensure compilation success.
