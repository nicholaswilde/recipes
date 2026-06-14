import unittest
import os
import sys

# Import functions from scrape_to_cook directly
import importlib.util
spec = importlib.util.spec_from_file_location("scrape_to_cook", "scripts/scrape_to_cook.py")
scrape_to_cook = importlib.util.module_from_spec(spec)
sys.modules["scrape_to_cook"] = scrape_to_cook
spec.loader.exec_module(scrape_to_cook)

class TestScrapeToCook(unittest.TestCase):
    def test_module_exists(self):
        self.assertIsNotNone(scrape_to_cook, "scrape_to_cook module should exist")

    def test_parse_iso_duration(self):
        self.assertEqual(scrape_to_cook.parse_iso_duration("PT15M"), "15 minutes")
        self.assertEqual(scrape_to_cook.parse_iso_duration("PT1H30M"), "1 hour 30 minutes")
        self.assertEqual(scrape_to_cook.parse_iso_duration("PT2H"), "2 hours")
        self.assertEqual(scrape_to_cook.parse_iso_duration(""), "")

    def test_parse_ingredient(self):
        self.assertEqual(
            scrape_to_cook.parse_ingredient("2 1/2 cups all-purpose flour"),
            "@all-purpose flour{2.5%cups}"
        )
        self.assertEqual(
            scrape_to_cook.parse_ingredient("1 tsp salt"),
            "@salt{1%tsp}"
        )
        # Ignored ingredient from cook/config/ignored_ingredients.yaml
        self.assertEqual(
            scrape_to_cook.parse_ingredient("nonstick baking spray"),
            "nonstick baking spray"
        )
        self.assertEqual(
            scrape_to_cook.parse_ingredient("3 large eggs"),
            "@eggs{3%large}"
        )

    def test_format_time_range(self):
        self.assertEqual(
            scrape_to_cook.format_time_range("7-8 minutes"),
            "7 to ~{8%minutes}"
        )
        self.assertEqual(
            scrape_to_cook.format_time_range("10 to 12 minutes"),
            "10 to ~{12%minutes}"
        )
        self.assertEqual(
            scrape_to_cook.format_time_range("about 5 minutes"),
            "about ~{5%minutes}"
        )

    def test_resolve_category(self):
        self.assertEqual(scrape_to_cook.resolve_category("Dessert"), "desserts")
        self.assertEqual(scrape_to_cook.resolve_category("Bread & Buns"), "breads")
        self.assertEqual(scrape_to_cook.resolve_category("Soup"), "soups-and-stews")
        self.assertEqual(scrape_to_cook.resolve_category("Something Unknown"), "main")

    def test_extract_json_ld_recipe(self):
        html = """
        <html>
        <head>
          <script type="application/ld+json">
          {
            "@context": "https://schema.org",
            "@graph": [
              {
                "@type": "Recipe",
                "name": "Dummy Chocolate Cake",
                "recipeYield": ["8 servings"],
                "prepTime": "PT15M",
                "cookTime": "PT45M",
                "recipeIngredient": [
                  "1 cup sugar",
                  "2 cups flour"
                ],
                "recipeInstructions": [
                  {
                    "@type": "HowToStep",
                    "text": "Mix sugar and flour."
                  },
                  {
                    "@type": "HowToStep",
                    "text": "Bake for 45 minutes."
                  }
                ]
              }
            ]
          }
          </script>
        </head>
        <body></body>
        </html>
        """
        recipe = scrape_to_cook.extract_json_ld_recipe(html)
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe.get("name"), "Dummy Chocolate Cake")
        self.assertEqual(recipe.get("recipeYield"), ["8 servings"])
        self.assertEqual(recipe.get("recipeIngredient"), ["1 cup sugar", "2 cups flour"])

    def test_extract_wprm_recipe(self):
        html = """
        <div class="wprm-recipe-container">
          <span class="wprm-recipe-name">WPRM Oatmeal Cookies</span>
          <span class="wprm-recipe-servings">12</span>
          <div class="wprm-recipe-ingredient">
            <span class="wprm-recipe-ingredient-amount">1</span>
            <span class="wprm-recipe-ingredient-unit">cup</span>
            <span class="wprm-recipe-ingredient-name">oats</span>
          </div>
          <div class="wprm-recipe-instruction">
            <div class="wprm-recipe-instruction-text">Bake cookies.</div>
          </div>
        </div>
        """
        recipe = scrape_to_cook.extract_wprm_recipe(html)
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe["name"], "WPRM Oatmeal Cookies")
        self.assertEqual(recipe["servings"], "12")
        self.assertEqual(recipe["ingredients"], ["1 cup oats"])
        self.assertEqual(recipe["instructions"], ["Bake cookies."])

if __name__ == "__main__":
    unittest.main()
