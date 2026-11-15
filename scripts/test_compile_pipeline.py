################################################################################
#
# test_compile_pipeline.py
# ----------------
# Tests for CookLang compile unit/emoji injection and Markdown edit preservation
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 15 Nov 2026
# @version 0.1.0
#
################################################################################

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


convert_units = _load_module("convert_recipe_units", "scripts/convert_recipe_units.py")
inject_fm = _load_module("inject_frontmatter", "scripts/inject_frontmatter.py")
merge_md = _load_module("merge_recipe_md", "scripts/merge_recipe_md.py")


class TestConvertRecipeUnits(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.measuring = convert_units.load_measuring_table("docs/reference/measuring.md")
        self.emojis = convert_units.load_emoji_mappings("includes/emoji.yaml")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_soft_hyphen_entries_load_and_convert(self):
        self.assertIn("baking powder", self.measuring)
        self.assertEqual(convert_units.convert_ingredient("1", "tsp", "baking powder", self.measuring), 4)
        self.assertEqual(convert_units.convert_ingredient("2", "Tbsp", "basil pesto", self.measuring), 28)
        self.assertEqual(convert_units.convert_ingredient("1/2", "cup", "butter", self.measuring), 113)

    def test_no_false_positive_measuring_matches(self):
        self.assertIsNone(
            convert_units.convert_ingredient("6", "cups", "low-sodium chicken or vegetable stock", self.measuring)
        )
        self.assertEqual(
            convert_units.find_best_key("russet potatoes", self.measuring),
            "potatoes (sliced)",
        )
        self.assertIsNone(
            convert_units.convert_ingredient("1", "tsp", "whole black peppercorns", self.measuring)
        )
        self.assertIsNone(
            convert_units.convert_ingredient("1", "tsp", "fennel seeds", self.measuring)
        )
        self.assertNotEqual(
            convert_units.find_best_key("whole milk", self.measuring),
            "dried whole milk (powdered)",
        )

    def test_small_seasoning_omits_grams_and_weight_units_not_reconverted(self):
        self.assertIsNone(convert_units.convert_ingredient("1", "tsp", "kosher salt", self.measuring))
        self.assertIsNone(convert_units.convert_ingredient("1", "tsp", "ground cumin", self.measuring))
        self.assertIsNone(convert_units.convert_ingredient("8", "oz", "cream cheese", self.measuring))

    def test_convert_markdown_file_ingredients_cookware_and_idempotency(self):
        md_path = os.path.join(self.tmp_dir, "test.md")
        initial = """---
comments: true
---

# Test Loaf

## :salt: Ingredients

- 1 1/2 cups all-purpose flour
- 1 Tbsp honey
- 1 tsp kosher salt
- 1 cup [all-purpose flour](../ingredients/all-purpose-flour.md)

## :cooking: Cookware

- 1 saucepan
- 1 large bowl

## :pencil: Instructions

### Step 1

Mix everything.
"""
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(initial)

        convert_units.convert_markdown_file(md_path)
        with open(md_path, "r", encoding="utf-8") as f:
            first_pass = f.read()

        self.assertIn("- :bread: 1 1/2 cups (180 g) all-purpose flour", first_pass)
        self.assertIn("- :honey_pot: 1 Tbsp (21 g) honey", first_pass)
        self.assertIn("- :salt: 1 tsp kosher salt", first_pass)
        self.assertIn("- :bread: 1 cup (120 g) [all-purpose flour](../ingredients/all-purpose-flour.md)", first_pass)
        self.assertIn("- :shallow_pan_of_food: 1 saucepan", first_pass)
        self.assertIn("- :bowl_with_spoon: 1 large bowl", first_pass)

        convert_units.convert_markdown_file(md_path)
        with open(md_path, "r", encoding="utf-8") as f:
            second_pass = f.read()
        self.assertEqual(first_pass, second_pass)


class TestInjectAndMergeMarkdown(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_inject_frontmatter_applies_cook_title_emoji(self):
        cook_path = os.path.join(self.tmp_dir, "Citron Chaud.cook")
        md_path = os.path.join(self.tmp_dir, "citron-chaud.md")
        with open(cook_path, "w", encoding="utf-8") as f:
            f.write("---\ntitle: ':lemon: Citron Chaud'\ntags:\n  - lemon\n---\nAdd @honey{1%tsp}.\n")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("---\ncomments: true\ntags:\n  - beverage\n---\n\n# Citron Chaud\n")

        with mock.patch.object(sys, "argv", ["inject_frontmatter.py", cook_path, md_path]):
            inject_fm.main()

        with open(md_path, "r", encoding="utf-8") as f:
            out = f.read()
        self.assertIn("# :lemon: Citron Chaud", out)
        self.assertIn("- beverage", out)
        self.assertIn("- lemon", out)

    def test_merge_preserves_manual_edits_while_updating_cook_content(self):
        existing = """---
comments: true
tags:
  - bread
  - favorite
hero: assets/images/custom-bread.webp
---

# :baguette_bread: Custom Bread

![Custom Bread][1]{ loading=lazy }

| :fork_and_knife_with_plate: Serves | :timer_clock: Total Time |
|:----------------------------------:|:-----------------------: |
| 2 loaves | 1 hour |

## :salt: Ingredients

- :bread: 2 cups (240 g) all-purpose flour

## :cooking: Cookware

- :bowl_with_spoon: 1 large bowl

## :pencil: Instructions

### Step 1

Mix old flour.

!!! tip

    Let the dough rest for extra flavor.

## :zap: Variations

Add sesame seeds on top.[^1]

## :link: Source

- [King Arthur Baking](https://www.kingarthurbaking.com/example)

## :link: References

- [Pancake Princess](https://www.thepancakeprincess.com/example)

[1]: <../assets/images/custom-bread.webp>
[^1]:
    Toast seeds lightly first.
"""
        compiled = """---
comments: true
tags:
  - bread
  - sourdough
serves: 3 loaves
---

# Custom Bread

| :fork_and_knife_with_plate: Serves | :timer_clock: Total Time |
|:----------------------------------:|:-----------------------: |
| 3 loaves | 2 hours |

## :salt: Ingredients

- :bread: 3 cups (360 g) all-purpose flour
- :salt: 1 tsp salt

## :cooking: Cookware

- :bowl_with_spoon: 1 large bowl

## :pencil: Instructions

### Step 1

Mix new flour and salt.

## :link: Source

- <https://www.kingarthurbaking.com/example>
"""
        merged = merge_md.merge_markdown(existing, compiled)

        # Updated .cook fields & ingredients applied
        self.assertIn("serves: 3 loaves", merged)
        self.assertIn("- :bread: 3 cups (360 g) all-purpose flour", merged)
        self.assertIn("- :salt: 1 tsp salt", merged)
        self.assertIn("Mix new flour and salt.", merged)

        # Preserved manual edits
        self.assertIn("- favorite", merged)
        self.assertIn("- sourdough", merged)
        self.assertIn("hero: assets/images/custom-bread.webp", merged)
        self.assertIn("# :baguette_bread: Custom Bread", merged)
        self.assertIn("![Custom Bread][1]{ loading=lazy }", merged)
        self.assertIn("[1]: <../assets/images/custom-bread.webp>", merged)
        self.assertIn("!!! tip", merged)
        self.assertIn("Let the dough rest for extra flavor.", merged)
        self.assertIn("## :zap: Variations", merged)
        self.assertIn("## :link: References", merged)
        self.assertIn("- [King Arthur Baking](https://www.kingarthurbaking.com/example)", merged)
        self.assertNotIn("<https://www.kingarthurbaking.com/example>", merged)
        self.assertIn("[^1]:", merged)

    def test_merge_preserves_manual_tabs_when_compiled_has_none(self):
        existing = """---
comments: true
---

# :pie: Apple Pie

## :salt: Ingredients

=== "9 Inch"

    - :apple: 4 cups apples

=== "10 Inch"

    - :apple: 6 cups apples

## :pencil: Instructions

### Step 1

Bake pie.
"""
        compiled = """---
comments: true
---

# Apple Pie

## :salt: Ingredients

- :apple: 4 cups apples

## :pencil: Instructions

### Step 1

Bake pie thoroughly.
"""
        merged = merge_md.merge_markdown(existing, compiled)
        self.assertIn('=== "9 Inch"', merged)
        self.assertIn('=== "10 Inch"', merged)
        self.assertIn("Bake pie thoroughly.", merged)


if __name__ == "__main__":
    unittest.main()
