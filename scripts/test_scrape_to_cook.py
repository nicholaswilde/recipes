################################################################################
#
# test_scrape_to_cook.py
# ----------------
# Test the scrape_to_cook recipe parser
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 14 Jun 2026
# @version 0.1.0
#
################################################################################

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

    def test_format_minutes_to_duration(self):
        self.assertEqual(scrape_to_cook.format_minutes_to_duration(15), "15 minutes")
        self.assertEqual(scrape_to_cook.format_minutes_to_duration(60), "1 hour")
        self.assertEqual(scrape_to_cook.format_minutes_to_duration(90), "1 hour 30 minutes")
        self.assertEqual(scrape_to_cook.format_minutes_to_duration(120), "2 hours")
        self.assertEqual(scrape_to_cook.format_minutes_to_duration(125), "2 hours 5 minutes")
        self.assertEqual(scrape_to_cook.format_minutes_to_duration(0), "")
        self.assertEqual(scrape_to_cook.format_minutes_to_duration(None), "")

    def test_extract_recipe_scrapers_supported(self):
        html = """
        <html>
        <head>
          <script type="application/ld+json">
          {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": "Triple Chocolate Cake",
            "recipeYield": "12 servings",
            "prepTime": "PT30M",
            "cookTime": "PT35M",
            "totalTime": "PT1H5M",
            "recipeIngredient": [
              "2 cups sugar",
              "1 3/4 cups all-purpose flour",
              "3/4 cup cocoa powder"
            ],
            "recipeInstructions": [
              {
                "@type": "HowToStep",
                "text": "Preheat oven to 350F."
              },
              {
                "@type": "HowToStep",
                "text": "Mix dry ingredients."
              }
            ],
            "recipeCategory": "Cake",
            "image": "https://sallysbakingaddiction.com/wp-content/uploads/cake.jpg"
          }
          </script>
        </head>
        <body></body>
        </html>
        """
        url = "https://sallysbakingaddiction.com/triple-chocolate-cake/"
        recipe = scrape_to_cook.extract_recipe_scrapers(html, url, supported_only=True)
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe["name"], "Triple Chocolate Cake")
        self.assertEqual(recipe["servings"], "12")
        self.assertEqual(recipe["prep_time"], "30 minutes")
        self.assertEqual(recipe["cook_time"], "35 minutes")
        self.assertEqual(recipe["total_time"], "1 hour 5 minutes")
        self.assertEqual(recipe["image_url"], "https://sallysbakingaddiction.com/wp-content/uploads/cake.jpg")
        self.assertEqual(
            recipe["ingredients"],
            ["2 cups sugar", "1 3/4 cups all-purpose flour", "3/4 cup cocoa powder"]
        )
        self.assertEqual(
            recipe["instructions"],
            ["Preheat oven to 350F.", "Mix dry ingredients."]
        )
        self.assertEqual(recipe["category"], "Cake")

    def test_extract_recipe_scrapers_unsupported(self):
        html = "<html><body><h1>Recipe</h1></body></html>"
        url = "https://unsupported-site-12345.org/recipe"
        recipe = scrape_to_cook.extract_recipe_scrapers(html, url, supported_only=True)
        self.assertIsNone(recipe)

    def test_scrape_recipe_priority(self):
        # 1. Supported site should parse via recipe-scrapers
        sally_html = """
        <html>
        <head>
          <script type="application/ld+json">
          {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": "Sally Cake",
            "recipeIngredient": ["1 cup flour"],
            "recipeInstructions": [{"@type": "HowToStep", "text": "Bake cake."}]
          }
          </script>
        </head>
        <body></body>
        </html>
        """
        sally_url = "https://sallysbakingaddiction.com/sally-cake/"
        res_sally = scrape_to_cook.scrape_recipe(sally_html, sally_url)
        self.assertIsNotNone(res_sally)
        self.assertEqual(res_sally["name"], "Sally Cake")
        self.assertEqual(res_sally["ingredients"], ["1 cup flour"])

        # 2. Unsupported site with JSON-LD should fallback to JSON-LD
        generic_json_html = """
        <html>
        <head>
          <script type="application/ld+json">
          {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": "Generic JSON Recipe",
            "recipeIngredient": ["1 cup rice"],
            "recipeInstructions": [{"@type": "HowToStep", "text": "Boil rice."}]
          }
          </script>
        </head>
        <body></body>
        </html>
        """
        unsupported_url = "https://my-obscure-blog.net/recipe"
        res_json = scrape_to_cook.scrape_recipe(generic_json_html, unsupported_url)
        self.assertIsNotNone(res_json)
        self.assertEqual(res_json["name"], "Generic JSON Recipe")
        self.assertEqual(res_json["ingredients"], ["1 cup rice"])

        # 3. Unsupported site with WPRM should fallback to WPRM
        generic_wprm_html = """
        <div class="wprm-recipe-container">
          <span class="wprm-recipe-name">WPRM Fallback Recipe</span>
          <div class="wprm-recipe-ingredient">
            <span class="wprm-recipe-ingredient-amount">2</span>
            <span class="wprm-recipe-ingredient-unit">tbsp</span>
            <span class="wprm-recipe-ingredient-name">olive oil</span>
          </div>
          <div class="wprm-recipe-instruction">
            <div class="wprm-recipe-instruction-text">Heat oil in pan.</div>
          </div>
        </div>
        """
        res_wprm = scrape_to_cook.scrape_recipe(generic_wprm_html, unsupported_url)
        self.assertIsNotNone(res_wprm)
        self.assertEqual(res_wprm["name"], "WPRM Fallback Recipe")
        self.assertEqual(res_wprm["ingredients"], ["2 tbsp olive oil"])

if __name__ == "__main__":
    unittest.main()
