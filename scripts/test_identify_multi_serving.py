import os
import shutil
import tempfile
import unittest
from identify_multi_serving import find_multi_serving_recipes

class TestIdentifyMultiServing(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_find_multi_serving_recipes(self):
        # File with one Ingredients header
        file1 = os.path.join(self.test_dir, "recipe1.md")
        with open(file1, "w") as f:
            f.write("## :salt: Ingredients\n- salt\n")

        # File with two Ingredients headers
        file2 = os.path.join(self.test_dir, "recipe2.md")
        with open(file2, "w") as f:
            f.write("## :salt: Ingredients - Small\n- salt\n## :salt: Ingredients - Large\n- salt\n")

        # File with no Ingredients headers
        file3 = os.path.join(self.test_dir, "recipe3.md")
        with open(file3, "w") as f:
            f.write("# Recipe 3\nInstructions\n")

        results = find_multi_serving_recipes(self.test_dir)
        self.assertIn("recipe2.md", [os.path.basename(r) for r in results])
        self.assertNotIn("recipe1.md", [os.path.basename(r) for r in results])
        self.assertNotIn("recipe3.md", [os.path.basename(r) for r in results])

if __name__ == "__main__":
    unittest.main()
