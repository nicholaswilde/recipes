#!/usr/bin/env python3

################################################################################
#
# test_youtube_recipe.py
# ----------------------
# Test YouTube recipe extraction and caption processing
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 27 Sep 2026
# @version 0.1.0
#
################################################################################

import unittest
import os
import sys

# Import functions from scripts/youtube_recipe.py
import importlib.util
spec = importlib.util.spec_from_file_location("youtube_recipe", "scripts/youtube_recipe.py")
youtube_recipe = importlib.util.module_from_spec(spec)
sys.modules["youtube_recipe"] = youtube_recipe
spec.loader.exec_module(youtube_recipe)

class TestYouTubeRecipe(unittest.TestCase):
    def test_is_youtube_url(self):
        self.assertTrue(youtube_recipe.is_youtube_url("https://www.youtube.com/watch?v=V0ki4Il9Npc"))
        self.assertTrue(youtube_recipe.is_youtube_url("https://youtu.be/V0ki4Il9Npc"))
        self.assertTrue(youtube_recipe.is_youtube_url("https://youtube.com/shorts/V0ki4Il9Npc"))
        self.assertTrue(youtube_recipe.is_youtube_url("V0ki4Il9Npc"))
        self.assertTrue(youtube_recipe.is_youtube_url("V0ki4Il9Npc&"))
        self.assertTrue(youtube_recipe.is_youtube_url("V0ki4Il9Npc&is=ushKtzdzAS7T8aLv"))
        self.assertFalse(youtube_recipe.is_youtube_url("https://example.com/recipe"))
        self.assertFalse(youtube_recipe.is_youtube_url("12345"))
        self.assertFalse(youtube_recipe.is_youtube_url(""))

    def test_extract_youtube_video_id(self):
        self.assertEqual(
            youtube_recipe.extract_youtube_video_id("https://youtube.com/watch?v=V0ki4Il9Npc&is=ushKtzdzAS7T8aLv"),
            "V0ki4Il9Npc"
        )
        self.assertEqual(
            youtube_recipe.extract_youtube_video_id("https://youtu.be/V0ki4Il9Npc"),
            "V0ki4Il9Npc"
        )
        self.assertEqual(
            youtube_recipe.extract_youtube_video_id("https://www.youtube.com/embed/V0ki4Il9Npc"),
            "V0ki4Il9Npc"
        )
        self.assertEqual(
            youtube_recipe.extract_youtube_video_id("V0ki4Il9Npc"),
            "V0ki4Il9Npc"
        )
        self.assertEqual(
            youtube_recipe.extract_youtube_video_id("V0ki4Il9Npc&"),
            "V0ki4Il9Npc"
        )
        self.assertEqual(
            youtube_recipe.extract_youtube_video_id("V0ki4Il9Npc&is=ushKtzdzAS7T8aLv"),
            "V0ki4Il9Npc"
        )

    def test_parse_fraction(self):
        self.assertEqual(youtube_recipe.parse_fraction("1/2"), "0.5")
        self.assertEqual(youtube_recipe.parse_fraction("½"), "0.5")
        self.assertEqual(youtube_recipe.parse_fraction("1½"), "1.5")
        self.assertEqual(youtube_recipe.parse_fraction("1 1/2"), "1.5")

    def test_parse_ingredient_line(self):
        name, cooklang, qty, unit = youtube_recipe.parse_ingredient_line("1 stick (113g) unsalted butter")
        self.assertEqual(name, "unsalted butter")
        self.assertEqual(cooklang, "@unsalted butter{1%stick (113g)}")

        name, cooklang, qty, unit = youtube_recipe.parse_ingredient_line("100g all-purpose flour")
        self.assertEqual(name, "all-purpose flour")
        self.assertEqual(cooklang, "@all-purpose flour{100%g}")

        name, cooklang, qty, unit = youtube_recipe.parse_ingredient_line("1½ teaspoons vanilla extract")
        self.assertEqual(name, "vanilla extract")
        self.assertEqual(cooklang, "@vanilla extract{1.5%tsp}")

        name, cooklang, qty, unit = youtube_recipe.parse_ingredient_line("140g dark chocolate, finely chopped")
        self.assertEqual(name, "dark chocolate")
        self.assertEqual(cooklang, "@dark chocolate{140%g} (finely chopped)")

    def test_extract_ingredients_from_description(self):
        desc = """
Chocolate Chip Cookie Soufflé

Ingredients

* 1 stick (113g) unsalted butter
* 100g all-purpose flour
* 1 large egg

Chapters:
0:00 Start
"""
        title, ings = youtube_recipe.extract_ingredients_from_description(desc)
        self.assertEqual(title, "Chocolate Chip Cookie Soufflé")
        self.assertEqual(len(ings), 3)
        self.assertIn("1 stick (113g) unsalted butter", ings)

    def test_clean_spoken_sentence(self):
        self.assertEqual(
            youtube_recipe.clean_spoken_sentence("Okay, so the first step I'm going to do is to brown my butter."),
            "Brown my butter."
        )
        self.assertEqual(
            youtube_recipe.clean_spoken_sentence("So, we're going to basically bring this to a boil."),
            "Bring this to a boil."
        )

    def test_inline_ingredients_into_steps(self):
        raw_ings = [
            "1 stick (113g) unsalted butter",
            "100g all-purpose flour",
            "1 large egg",
            "4 large egg whites"
        ]
        steps = [
            "Melt unsalted butter in a pan.",
            "Whisk in all-purpose flour.",
            "Beat large egg and fold into batter.",
            "Whip egg whites and fold into batter."
        ]
        inlined = youtube_recipe.inline_ingredients_into_steps(steps, raw_ings)
        self.assertIn("@unsalted butter{1%stick (113g)}", inlined[0])
        self.assertIn("@all-purpose flour{100%g}", inlined[1])
        self.assertIn("@egg{1%large}", inlined[2])
        self.assertIn("@egg whites{4%large}", inlined[3])
        # Ensure 'egg' does not match inside 'egg whites'
        self.assertNotIn("@egg{} whites", inlined[3])

    def test_live_youtube_extract(self):
        url = "https://youtube.com/watch?v=V0ki4Il9Npc&is=ushKtzdzAS7T8aLv"
        recipe = youtube_recipe.extract_youtube_recipe(url)
        self.assertEqual(recipe["name"], "Chocolate Chip Cookie Soufflé")
        self.assertEqual(recipe["author"], "Claire Saffitz x Dessert Person")
        self.assertEqual(len(recipe["ingredients"]), 13)
        self.assertGreaterEqual(len(recipe["instructions"]), 5)
        self.assertTrue(recipe["image_url"].startswith("http"))

if __name__ == "__main__":
    unittest.main()
