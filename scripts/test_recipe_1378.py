import unittest
import os

class TestRecipe1378(unittest.TestCase):
    def test_recipe_file_exists(self):
        recipe_path = "docs/sides/vegetables/ginger-and-garlic-green-beans.md"
        self.assertTrue(os.path.exists(recipe_path), f"Recipe file {recipe_path} should exist")

    def test_recipe_content(self):
        recipe_path = "docs/sides/vegetables/ginger-and-garlic-green-beans.md"
        if os.path.exists(recipe_path):
            with open(recipe_path, "r") as f:
                content = f.read()
            self.assertIn("Ginger and Garlic Green Beans", content)
            # Check that it doesn't contain placeholders or draft markers
            self.assertNotIn("draft: true", content)

if __name__ == "__main__":
    unittest.main()
