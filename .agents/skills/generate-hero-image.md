# Generate Hero Image

This skill guides the process of generating a new hero image for an existing recipe and updating the recipe's markdown documentation accordingly.

## Description

This skill automates the creation of a hero image for a recipe using the `generate_image` tool. It then uses the project's internal scripts to properly link the new image to the recipe's `.cook` file, compile the markdown document, convert the image to WebP format, and commit the final changes.

## Protocol

1. **Determine Recipe Location:**
   Identify the recipe's `.cook` file location in the `cook/` directory (e.g., `cook/sides/Garlic Dill Pickles.cook`).

2. **Generate the Image:**
   Use the `generate_image` tool to create an appetizing, professional food photography shot that represents the recipe. 
   - **Aspect Ratio:** `1:1` is standard for hero images.
   - **Prompt:** Craft a high-quality prompt emphasizing lighting, styling, and key ingredients.

3. **Move and Rename the Image:**
   The `generate_image` tool outputs an image to the local brain/artifacts directory. Move and rename this image to match the recipe's `.cook` filename, placing it in the same directory (e.g., `cook/sides/Garlic Dill Pickles.jpg`).
   ```bash
   mv "<generated_image_path>" "cook/<category>/<Recipe Name>.jpg"
   ```

4. **Update Recipe Documentation:**
   Run the `move.sh` script on the recipe's `.cook` file. This script will automatically update the markdown file, convert the new image to `.webp` in `docs/assets/images/`, and link everything correctly.
   ```bash
   bash scripts/move.sh "cook/<category>/<Recipe Name>.cook"
   ```

5. **Commit the Changes:**
   Add and commit the new `.jpg` source image, the compiled `.md` markdown file, and the `.webp` image to version control.
   ```bash
   git add "cook/<category>/<Recipe Name>.jpg" "docs/<category>/<recipe-name>.md" "docs/assets/images/<recipe-name>.webp"
   git commit -m "feat: add hero image for <Recipe Name>"
   git push
   ```
