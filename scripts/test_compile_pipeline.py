################################################################################
#
# test_compile_pipeline.py
# ----------------
# Tests for cook-docs compile pipeline (weights sync, enrichment, merge, doctor)
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 15 Nov 2026
# @version 0.2.0
#
################################################################################

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sync_weights = _load_module("sync_weights_yaml", "scripts/sync_weights_yaml.py")


class TestCookDocsCompilePipeline(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.cook_root = Path(self.tmp_dir) / "cook"
        self.docs_root = Path(self.tmp_dir) / "docs"
        self.assets_dir = self.docs_root / "assets" / "images"
        self.cook_root.mkdir(parents=True)
        self.docs_root.mkdir(parents=True)
        shutil.copy("cook/recipe.md.gotmpl", self.cook_root / "recipe.md.gotmpl")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def _run_cook_docs(self, *extra_args):
        cmd = [
            "cook-docs",
            "-c",
            str(self.cook_root),
            "-o",
            str(self.docs_root),
            "--assets-dir",
            str(self.assets_dir),
            "--emoji-file",
            "includes/emoji.yaml",
            "--weights-file",
            "includes/weights.yaml",
            "--link-dirs",
            "ingredients,sauces-and-dressings,breads",
            "--merge",
            *extra_args,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(
            res.returncode,
            0,
            f"cook-docs failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}",
        )
        return res

    def test_weights_yaml_in_sync_with_measuring_md(self):
        data = sync_weights.build_weights_data(Path("docs/reference/measuring.md"))
        weights = data["weights"]
        self.assertIn("baking powder", weights)
        self.assertIn("basil pesto", weights)
        self.assertIn("all-purpose flour", weights)
        self.assertIn("whole milk", weights)
        self.assertNotIn("basil", data["exclude_small_units"])
        self.assertIn("fresh basil", data["exclude_small_units"])

    def test_enrichment_weights_emojis_links_and_text_quantities(self):
        ing_dir = self.cook_root / "ingredients"
        main_dir = self.cook_root / "main"
        ing_dir.mkdir()
        main_dir.mkdir()

        (ing_dir / "Rice Flour.cook").write_text(
            "---\nsource: https://example.com\n---\nGrind @rice{1%cup}.\n",
            encoding="utf-8",
        )
        recipe = main_dir / "Weight Test.cook"
        recipe.write_text(
            """---
title: ":bread: Weight Test"
serves: 4
source: https://example.com
---

Mix @baking powder{1%tsp}, @basil pesto{2%Tbsp}, @butter{1/2%cup}, @all-purpose flour{1 1/2%cups}, @honey{1%Tbsp}, @kosher salt{1%tsp}, @ground cumin{1%tsp}, @cream cheese{8%oz}, @low-sodium chicken or vegetable stock{6%cups}, @whole black peppercorns{1%tsp}, @fennel seeds{1%tsp}, @whole milk{1%cup}, @rice flour{1/4%cup}, @agave{0.25 to 0.5%cup}, @salt{pinch}, and @neutral oil{} in a #saucepan{} and #large bowl{}.
""",
            encoding="utf-8",
        )

        self._run_cook_docs(str(recipe))
        out = (self.docs_root / "main" / "weight-test.md").read_text(encoding="utf-8")

        self.assertIn("# :bread: Weight Test", out)
        self.assertIn("- :chestnut: 1 tsp (4 g) baking powder", out)
        self.assertIn("- :herb: 2 tbsp (28 g) basil pesto", out)
        self.assertIn("- :butter: 1/2 cup (113 g) butter", out)
        self.assertIn("- :bread: 1 1/2 cups (180 g) all-purpose flour", out)
        self.assertIn("- :honey_pot: 1 tbsp (21 g) honey", out)
        self.assertIn("- :salt: 1 tsp kosher salt", out)
        self.assertIn("- :chestnut: 1 tsp ground cumin", out)
        self.assertIn("- :cheese: 8 oz cream cheese", out)
        self.assertIn("- :stew: 6 cups low-sodium chicken or vegetable stock", out)
        self.assertIn("- :hot_pepper: 1 tsp whole black peppercorns", out)
        self.assertIn("- :herb: 1 tsp fennel seeds", out)
        self.assertIn("- :glass_of_milk: 1 cup (227 g) whole milk", out)
        self.assertIn("- :bread: 1/4 cup (36 g) [rice flour](../ingredients/rice-flour.md)", out)
        self.assertIn("- :apple: 0.25 to 0.5 cup agave", out)
        self.assertIn("- :salt: salt (pinch)", out)
        self.assertIn("- :avocado: neutral oil", out)
        self.assertIn("- :shallow_pan_of_food: 1 saucepan", out)
        self.assertIn("- :bowl_with_spoon: 1 large bowl", out)

    def test_nested_relroot_category_tags_and_asset_copy(self):
        pesto_dir = self.cook_root / "sauces-and-dressings" / "gravy-and-savory-sauces" / "pesto"
        pesto_dir.mkdir(parents=True)
        recipe = pesto_dir / "Herb Pesto.cook"
        recipe.write_text(
            ">> source: https://example.com/pesto\n>> serves: 4\nBlend @olive oil{1/2%cup}.\n",
            encoding="utf-8",
        )
        (pesto_dir / "Herb Pesto.jpg").write_bytes(b"fakejpeg")

        self._run_cook_docs("--image-ext", "webp", str(recipe))
        md_path = (
            self.docs_root
            / "sauces-and-dressings"
            / "gravy-and-savory-sauces"
            / "pesto"
            / "herb-pesto.md"
        )
        out = md_path.read_text(encoding="utf-8")

        self.assertIn("hero: assets/images/herb-pesto.webp", out)
        self.assertIn("  - sauce", out)
        self.assertIn("  - pesto", out)
        self.assertIn("[1]: <../../../assets/images/herb-pesto.webp>", out)
        self.assertTrue((self.assets_dir / "herb-pesto.jpg").is_file())
        self.assertNotIn("## :cooking: Cookware", out)

    def test_merge_preserves_manual_edits_while_updating_cook_content(self):
        breads_cook = self.cook_root / "breads"
        breads_docs = self.docs_root / "breads"
        breads_cook.mkdir()
        breads_docs.mkdir()

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
        md_path = breads_docs / "custom-bread.md"
        md_path.write_text(existing, encoding="utf-8")

        cook_path = breads_cook / "Custom Bread.cook"
        cook_path.write_text(
            """---
serves: 3 loaves
total time: 2 hours
source: https://www.kingarthurbaking.com/example
tags:
  - bread
  - sourdough
---

Mix @all-purpose flour{3%cups} and @salt{1%tsp} in a #large bowl{}.
""",
            encoding="utf-8",
        )

        self._run_cook_docs(str(cook_path))
        merged = md_path.read_text(encoding="utf-8")

        # Updated .cook fields & ingredients applied
        self.assertIn("serves: 3 loaves", merged)
        self.assertIn("- :bread: 3 cups (360 g) all-purpose flour", merged)
        self.assertIn("- :salt: 1 tsp salt", merged)
        self.assertIn("Mix all-purpose flour and salt in a large bowl.", merged)

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
        pie_cook = self.cook_root / "desserts" / "pie"
        pie_docs = self.docs_root / "desserts" / "pie"
        pie_cook.mkdir(parents=True)
        pie_docs.mkdir(parents=True)

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
        md_path = pie_docs / "apple-pie.md"
        md_path.write_text(existing, encoding="utf-8")

        cook_path = pie_cook / "Apple Pie.cook"
        cook_path.write_text("Bake @apples{4%cups} thoroughly.\n", encoding="utf-8")

        self._run_cook_docs(str(cook_path))
        merged = md_path.read_text(encoding="utf-8")
        self.assertIn('=== "9 Inch"', merged)
        self.assertIn('=== "10 Inch"', merged)
        self.assertIn("Bake apples thoroughly.", merged)


if __name__ == "__main__":
    unittest.main()
