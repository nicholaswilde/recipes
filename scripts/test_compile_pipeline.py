################################################################################
#
# test_compile_pipeline.py
# ----------------
# Tests for cook-docs compile pipeline (weights sync, enrichment, webp, nav, merge, doctor)
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 15 Nov 2026
# @version 0.3.0
#
################################################################################

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


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

    def _run_cook_docs(self, *extra_args, nav_file=""):
        cmd = [
            "cook-docs",
            "-C",
            ".cookdocs.toml",
            "-c",
            str(self.cook_root),
            "-o",
            str(self.docs_root),
            "--assets-dir",
            str(self.assets_dir),
            "--nav-file",
            str(nav_file),
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
        self.assertIn("basil", data["exclude_small_units"])
        self.assertIn("cinnamon", data["exclude_small_units"])
        self.assertIn("ginger", data["exclude_small_units"])
        self.assertIn("pesto", data["exclude_small_units_except"])
        self.assertIn("sugar", data["exclude_small_units_except"])
        self.assertIn("crystallized", data["exclude_small_units_except"])

    def test_enrichment_weights_emojis_step_links_and_title_emoji(self):
        ing_dir = self.cook_root / "ingredients"
        main_dir = self.cook_root / "main"
        ing_dir.mkdir()
        main_dir.mkdir()

        (ing_dir / "Rice Flour.cook").write_text(
            "---\nsource: https://example.com\n---\nGrind @rice{1%cup}.\n",
            encoding="utf-8",
        )
        recipe = main_dir / "Weight Test Soup.cook"
        recipe.write_text(
            """---
serves: 4
source: https://example.com
---

Mix @baking powder{1%tsp}, @basil pesto{2%Tbsp}, @fresh basil{2%Tbsp}, @cinnamon sugar{1%tsp}, @ground cinnamon{1%tsp}, @crystallized ginger{1%Tbsp}, @butter{1/2%cup}, @all-purpose flour{1 1/2%cups}, @honey{1%Tbsp}, @kosher salt{1%tsp}, @ground cumin{1%tsp}, @cream cheese{8%oz}, @low-sodium chicken or vegetable stock{6%cups}, @whole black peppercorns{1%tsp}, @fennel seeds{1%tsp}, @whole milk{1%cup}, @rice flour{1/4%cup}, @agave{0.25 to 0.5%cup}, @salt{pinch}, and @neutral oil{} in a #saucepan{} and #large bowl{}.
""",
            encoding="utf-8",
        )

        self._run_cook_docs(str(recipe))
        out = (self.docs_root / "main" / "weight-test-soup.md").read_text(encoding="utf-8")

        # Native titleEmoji resolution from .cookdocs.toml [emoji.titles]
        self.assertIn("# :stew: Weight Test Soup", out)
        # Weight guard (exclude_small_units + exclude_small_units_except)
        self.assertIn("- :chestnut: 1 tsp (4 g) baking powder", out)
        self.assertIn("- :herb: 2 tbsp (28 g) basil pesto", out)
        self.assertIn("- :herb: 2 tbsp fresh basil", out)
        self.assertIn("- :candy: 1 tsp (4 g) cinnamon sugar", out)
        self.assertIn("- :chestnut: 1 tsp ground cinnamon", out)
        self.assertIn("1 tbsp (12 g) crystallized ginger", out)
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
        # Built-in cook.ingredients formatting for text & bare items
        self.assertIn("- :apple: 0.25 to 0.5 cup agave", out)
        self.assertIn("- :salt: salt (pinch)", out)
        self.assertIn("- :avocado: neutral oil", out)
        self.assertIn("- :shallow_pan_of_food: 1 saucepan", out)
        self.assertIn("- :bowl_with_spoon: 1 large bowl", out)
        # link_in_steps cross-links inside Step directions
        self.assertIn("[rice flour](../ingredients/rice-flour.md), agave", out)

    def test_category_tags_webp_conversion_and_nav_sync(self):
        pesto_dir = self.cook_root / "sauces-and-dressings" / "gravy-and-savory-sauces" / "pesto"
        butter_dir = self.cook_root / "ingredients" / "butter"
        pesto_dir.mkdir(parents=True)
        butter_dir.mkdir(parents=True)

        pesto = pesto_dir / "Zzz Herb Pesto.cook"
        pesto.write_text(
            "---\nsource: https://example.com/pesto\nserves: 4\ntags:\n  - summer\n---\nBlend @olive oil{1/2%cup}.\n",
            encoding="utf-8",
        )
        Image.new("RGB", (16, 16), (40, 140, 60)).save(pesto_dir / "Zzz Herb Pesto.jpg", "JPEG")

        butter = butter_dir / "Zzz Compound Blend.cook"
        butter.write_text(
            "---\nsource: https://example.com/butter\nserves: 8\n---\nWhip @butter{1%cup}.\n",
            encoding="utf-8",
        )
        Image.new("RGBA", (16, 16), (255, 220, 100, 255)).save(
            butter_dir / "Zzz Compound Blend.png", "PNG"
        )

        tmp_nav = Path(self.tmp_dir) / "zensical.toml"
        shutil.copy("zensical.toml", tmp_nav)

        self._run_cook_docs(str(pesto), str(butter), nav_file=tmp_nav)

        pesto_md = (
            self.docs_root
            / "sauces-and-dressings"
            / "gravy-and-savory-sauces"
            / "pesto"
            / "zzz-herb-pesto.md"
        ).read_text(encoding="utf-8")
        # Category tags merged with frontmatter tags
        self.assertIn("  - sauce", pesto_md)
        self.assertIn("  - pesto", pesto_md)
        self.assertIn("  - summer", pesto_md)
        # Native JPEG -> WebP conversion via convert_images = "webp"
        self.assertIn("hero: assets/images/zzz-herb-pesto.webp", pesto_md)
        self.assertIn("[1]: <../../../assets/images/zzz-herb-pesto.webp>", pesto_md)
        self.assertTrue((self.assets_dir / "zzz-herb-pesto.webp").is_file())
        self.assertFalse((self.assets_dir / "zzz-herb-pesto.jpg").exists())
        # Empty cookware heading omitted natively
        self.assertNotIn("## :cooking: Cookware", pesto_md)

        butter_md = (
            self.docs_root / "ingredients" / "butter" / "zzz-compound-blend.md"
        ).read_text(encoding="utf-8")
        # Category fallback titleEmoji from [emoji.categories] ("ingredients/butter" = "butter")
        self.assertIn("# :butter: Zzz Compound Blend", butter_md)
        self.assertIn("  - butter", butter_md)
        self.assertIn("  - ingredient", butter_md)
        # PNG preserved untouched
        self.assertIn("hero: assets/images/zzz-compound-blend.png", butter_md)
        self.assertTrue((self.assets_dir / "zzz-compound-blend.png").is_file())

        # Nav file updated cleanly for both flattened & nested sections
        nav_text = tmp_nav.read_text(encoding="utf-8")
        self.assertIn(
            '{ "Zzz Herb Pesto" = "sauces-and-dressings/gravy-and-savory-sauces/pesto/zzz-herb-pesto.md" }',
            nav_text,
        )
        self.assertIn(
            '{ "Zzz Compound Blend" = "ingredients/butter/zzz-compound-blend.md" }',
            nav_text,
        )

    def test_doctor_only_ignored_ingredients(self):
        main_dir = self.cook_root / "main"
        main_dir.mkdir()
        bad = main_dir / "Spray Test.cook"
        bad.write_text(
            "---\nsource: https://example.com\n---\nCoat pan with @nonstick baking spray{}.\n",
            encoding="utf-8",
        )
        res = subprocess.run(
            [
                "cook-docs",
                "-C",
                ".cookdocs.toml",
                "-c",
                str(self.cook_root),
                "doctor",
                "--only",
                "ignored",
                "--strict",
                str(bad),
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("nonstick baking spray", res.stdout + res.stderr)

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
        self.assertIn("# :bread: Custom Bread", merged)
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
