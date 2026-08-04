################################################################################
#
# test_check_recipe_emojis.py
# ----------------
# Test emoji check and mapping functions
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 14 Jun 2026
# @version 0.1.0
#
################################################################################

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch
import sys
import yaml

# Import main and helper functions from check_recipe_emojis
import importlib.util
spec = importlib.util.spec_from_file_location("check_recipe_emojis", "scripts/check_recipe_emojis.py")
check_recipe_emojis = importlib.util.module_from_spec(spec)
sys.modules["check_recipe_emojis"] = check_recipe_emojis
spec.loader.exec_module(check_recipe_emojis)

class TestCheckRecipeEmojis(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.emoji_yaml_path = os.path.join(self.test_dir, "emoji.yaml")
        
        # Create a dummy emoji.yaml matching the exact 4-space layout of the real includes/emoji.yaml
        self.dummy_yaml_content = """---
emoji:
  cookware:
    - bowl_with_spoon:
        - large bowl
        - mixing bowl
    - cookie:
        - baking sheet
  ingredients:
    - apple:
        - apple
        - apple sauce
        - gala apples
    - chestnut:
        - almonds
        - walnuts
"""
        with open(self.emoji_yaml_path, "w", encoding="utf-8") as f:
            f.write(self.dummy_yaml_content)
            
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("sys.exit")
    def test_fix_missing_ingredients_similarity(self, mock_exit):
        # Create a dummy cook recipe with a missing ingredient that has high similarity to "almonds" (e.g., "almond flakes")
        # and one that has no similarity (e.g., "mystery substance").
        cook_path = os.path.join(self.test_dir, "test_recipe.cook")
        with open(cook_path, "w", encoding="utf-8") as f:
            f.write("Add @almond flakes{10%g} and @mystery substance{5%g} to a #large bowl{}.\n")
            
        test_argv = ["scripts/check_recipe_emojis.py", "--fix", cook_path]
        
        # Set module level EMOJI_YAML_PATH if it exists, otherwise we'll define it on the module
        setattr(check_recipe_emojis, "EMOJI_YAML_PATH", self.emoji_yaml_path)
        
        with patch.object(sys, "argv", test_argv):
            try:
                check_recipe_emojis.main()
            except SystemExit:
                pass

        # Load back the emoji.yaml to verify if "almond flakes" got added under "chestnut"
        with open(self.emoji_yaml_path, "r") as f:
            updated_data = yaml.safe_load(f)
            
        ingredients_list = updated_data["emoji"]["ingredients"]
        chestnut_group = next(item["chestnut"] for item in ingredients_list if "chestnut" in item)
        self.assertIn("almond flakes", chestnut_group)
        
        # Verify mystery substance got mapped to fallback group "takeout_box"
        takeout_box_group = next(item["takeout_box"] for item in ingredients_list if "takeout_box" in item)
        self.assertIn("mystery substance", takeout_box_group)

    @patch("sys.exit")
    def test_fix_missing_cookware(self, mock_exit):
        # Create a dummy cook recipe with a missing cookware that has high similarity to "baking sheet" (e.g., "baking dish")
        # and a cookware with no similarity (e.g., "magic device").
        cook_path = os.path.join(self.test_dir, "test_cookware_recipe.cook")
        with open(cook_path, "w", encoding="utf-8") as f:
            f.write("Bake on #baking dish{} and use #magic device{}.\n")
            
        test_argv = ["scripts/check_recipe_emojis.py", "--fix", cook_path]
        setattr(check_recipe_emojis, "EMOJI_YAML_PATH", self.emoji_yaml_path)
        
        with patch.object(sys, "argv", test_argv):
            try:
                check_recipe_emojis.main()
            except SystemExit:
                pass

        # Load back the emoji.yaml to verify
        with open(self.emoji_yaml_path, "r") as f:
            updated_data = yaml.safe_load(f)
            
        cookware_list = updated_data["emoji"]["cookware"]
        cookie_group = next(item["cookie"] for item in cookware_list if "cookie" in item)
        self.assertIn("baking dish", cookie_group)
        
        # Verify magic device got mapped to fallback group "bowl_with_spoon"
        bowl_group = next(item["bowl_with_spoon"] for item in cookware_list if "bowl_with_spoon" in item)
        self.assertIn("magic device", bowl_group)

    @patch("sys.exit")
    def test_no_fix_mode_exits_with_error(self, mock_exit):
        # When --fix is not passed, it should exit with code 1 if there are missing emojis.
        cook_path = os.path.join(self.test_dir, "test_recipe.cook")
        with open(cook_path, "w", encoding="utf-8") as f:
            f.write("Add @almond flakes{10%g} to #large bowl{}.\n")
            
        test_argv = ["scripts/check_recipe_emojis.py", cook_path]
        setattr(check_recipe_emojis, "EMOJI_YAML_PATH", self.emoji_yaml_path)
        
        with patch.object(sys, "argv", test_argv):
            try:
                check_recipe_emojis.main()
            except SystemExit:
                pass
                
        mock_exit.assert_called_with(1)

if __name__ == "__main__":
    unittest.main()
