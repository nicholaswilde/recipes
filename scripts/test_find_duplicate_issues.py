#!/usr/bin/env python3

################################################################################
#
# test_find_duplicate_issues.py
# ----------------
# Test duplicate issues and ignore list functions
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 19 Sep 2026
# @version 0.1.0
#
################################################################################

import unittest
import os
import shutil
import tempfile
import sys
import importlib.util

spec = importlib.util.spec_from_file_location("find_duplicate_issues", "scripts/find_duplicate_issues.py")
find_duplicate_issues = importlib.util.module_from_spec(spec)
sys.modules["find_duplicate_issues"] = find_duplicate_issues
spec.loader.exec_module(find_duplicate_issues)

class TestFindDuplicateIssues(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.ignore_path = os.path.join(self.test_dir, "duplicate_ignore.txt")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_duplicate_ignore_singles_and_pairs(self):
        with open(self.ignore_path, "w", encoding="utf-8") as f:
            f.write("# Comment\n")
            f.write("classic-pineapple-upside-down-cake : pineapple-upside-down-cake\n")
            f.write("another-recipe\n")

        pairs, singles = find_duplicate_issues.load_duplicate_ignore(self.ignore_path)
        self.assertTrue(len(pairs) > 0)
        self.assertTrue(len(singles) > 0)

    def test_is_ignored_pineapple_upside_down_cake(self):
        with open(self.ignore_path, "w", encoding="utf-8") as f:
            f.write("classic-pineapple-upside-down-cake : pineapple-upside-down-cake\n")
            f.write("pineapple-upside-down-cake\n")

        pairs, singles = find_duplicate_issues.load_duplicate_ignore(self.ignore_path)

        r1 = {
            "path": "docs/desserts/cake/classic-pineapple-upside-down-cake.md",
            "title": "Classic Pineapple Upside Down Cake",
            "clean_title": "pineapple upside down cake"
        }
        r2 = {
            "path": "docs/desserts/cake/pineapple-upside-down-cake.md",
            "title": "Pineapple Upside Down Cake",
            "clean_title": "pineapple upside down cake"
        }
        r_other1 = {
            "path": "docs/breads/fry-bread.md",
            "title": "Fry Bread",
            "clean_title": "fry bread"
        }
        r_other2 = {
            "path": "docs/main/fry-bread-recipe.md",
            "title": "Fry Bread Recipe",
            "clean_title": "fry bread"
        }

        self.assertTrue(find_duplicate_issues.is_ignored(r1, r2, pairs, singles))
        self.assertFalse(find_duplicate_issues.is_ignored(r_other1, r_other2, pairs, singles))

    def test_is_ignored_issue_matching(self):
        with open(self.ignore_path, "w", encoding="utf-8") as f:
            f.write("pineapple-upside-down-cake\n")

        pairs, singles = find_duplicate_issues.load_duplicate_ignore(self.ignore_path)

        iss = {
            "number": 1080,
            "title": "Pineapple Upside Down Cake - Shutterbean",
            "clean_title": "pineapple upside down cake"
        }
        recipe_path = "docs/desserts/cake/pineapple-upside-down-cake.md"

        self.assertTrue(find_duplicate_issues.is_ignored(iss, recipe_path, pairs, singles))

if __name__ == "__main__":
    unittest.main()
