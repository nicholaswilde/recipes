################################################################################
#
# test_whitelist_typos.py
# ----------------
# Test typos whitelisting functions
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 14 Jun 2026
# @version 0.1.0
#
################################################################################

import unittest
import os
import shutil
import tempfile
from unittest.mock import patch
import sys

# Import functions from whitelist_typos directly
import importlib.util
spec = importlib.util.spec_from_file_location("whitelist_typos", "scripts/whitelist_typos.py")
whitelist_typos = importlib.util.module_from_spec(spec)
sys.modules["whitelist_typos"] = whitelist_typos
spec.loader.exec_module(whitelist_typos)

class TestWhitelistTypos(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.dict_path = os.path.join(self.test_dir, "dictionary.txt")
        self.config_path = os.path.join(self.test_dir, "_typos.toml")
        
        # Create a dummy dictionary.txt (unsorted, containing duplicates)
        self.dummy_words = ["zebra", "apple", "banana", "apple"]
        with open(self.dict_path, "w", encoding="utf-8") as f:
            for w in self.dummy_words:
                f.write(f"{w}\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_module_exists(self):
        self.assertIsNotNone(whitelist_typos, "whitelist_typos module should exist")

    @patch("sys.exit")
    def test_whitelist_words(self, mock_exit):
        # We will mock argv to add "cherry" and "date"
        test_argv = ["scripts/whitelist_typos.py", "cherry", "date"]
        
        # Set module-level paths for dictionary.txt and _typos.toml
        setattr(whitelist_typos, "DICTIONARY_PATH", self.dict_path)
        setattr(whitelist_typos, "TYPOS_TOML_PATH", self.config_path)
        
        with patch.object(sys, "argv", test_argv):
            try:
                whitelist_typos.main()
            except SystemExit:
                pass
                
        # Verify dictionary.txt contains new words, is sorted and unique
        with open(self.dict_path, "r", encoding="utf-8") as f:
            dict_content = [line.strip() for line in f if line.strip()]
            
        expected_dict = ["apple", "banana", "cherry", "date", "zebra"]
        self.assertEqual(dict_content, expected_dict)
        
        # Verify _typos.toml was regenerated and contains the new words
        self.assertTrue(os.path.exists(self.config_path))
        with open(self.config_path, "r", encoding="utf-8") as f:
            config_content = f.read()
            
        self.assertIn('"cherry" = "cherry"', config_content)
        self.assertIn('"date" = "date"', config_content)

if __name__ == "__main__":
    unittest.main()
