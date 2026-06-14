import unittest
import os

class TestRecipe1379(unittest.TestCase):
    def test_recipe_file_exists(self):
        recipe_path = "docs/sides/vegetables/green-beans-with-lime-and-red-onions.md"
        self.assertTrue(os.path.exists(recipe_path), f"Recipe file {recipe_path} should exist")

    def test_recipe_content(self):
        recipe_path = "docs/sides/vegetables/green-beans-with-lime-and-red-onions.md"
        if os.path.exists(recipe_path):
            with open(recipe_path, "r") as f:
                content = f.read()
            self.assertIn("Green Beans With Lime and Red Onions", content)
            self.assertNotIn("draft: true", content)

if __name__ == "__main__":
    unittest.main()
