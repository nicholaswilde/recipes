import unittest
import os
import re

class TestMeasuringTable(unittest.TestCase):
    def setUp(self):
        self.file_path = "docs/reference/measuring.md"

    def test_file_exists(self):
        self.assertTrue(os.path.exists(self.file_path))

    def test_agave_syrup_is_present(self):
        with open(self.file_path, "r") as f:
            content = f.read()
        self.assertIn("Agave syrup", content)

    def test_table_is_sorted(self):
        with open(self.file_path, "r") as f:
            lines = f.readlines()
            
        table_lines = []
        in_table = False
        for line in lines:
            if "| Ingredient" in line:
                in_table = True
                continue
            if in_table:
                if line.strip() == "" or not line.strip().startswith("|"):
                    in_table = False
                    continue
                if not line.startswith("|---"):
                    table_lines.append(line.strip())
                    
        # Extract normalized names
        names = []
        for line in table_lines:
            parts = [p.strip() for p in line.split("|")][1:-1]
            if parts:
                raw_name = parts[0]
                # strip links
                clean_name = re.sub(r'\[([^\]]+)\](?:\([^)]+\)|\[[^\]]+\])', r'\1', raw_name)
                names.append(clean_name.lower().replace('’', "'"))
                
        # Assert names are sorted alphabetically
        for i in range(len(names) - 1):
            self.assertTrue(names[i] <= names[i+1], f"Table is not sorted at: {names[i]} vs {names[i+1]}")

if __name__ == "__main__":
    unittest.main()
