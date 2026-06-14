import unittest
import os
import sys
import shutil
import tempfile
import subprocess
from unittest.mock import patch, MagicMock

# Import the orchestrator dynamically
import importlib.util

class TestImportRecipeWorkflow(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_import_recipe_workflow_module(self):
        spec = importlib.util.spec_from_file_location("import_recipe_workflow", "scripts/import_recipe_workflow.py")
        self.assertIsNotNone(spec, "import_recipe_workflow spec should exist")
        import_recipe_workflow = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(import_recipe_workflow)
        self.assertIsNotNone(import_recipe_workflow)

    @patch("subprocess.run")
    @patch("sys.exit")
    @patch("os.path.exists")
    def test_workflow_url(self, mock_exists, mock_exit, mock_run):
        spec = importlib.util.spec_from_file_location("import_recipe_workflow", "scripts/import_recipe_workflow.py")
        import_recipe_workflow = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(import_recipe_workflow)

        # Mock functions
        import_recipe_workflow.find_newest_cook_file = MagicMock(return_value="cook/main/DummyRecipe.cook")
        mock_exists.return_value = True

        # Setup mock responses for subprocess.run
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = ""
        mock_res.stderr = ""
        mock_run.return_value = mock_res

        # Run main
        test_argv = ["scripts/import_recipe_workflow.py", "http://example.com/recipe", "main"]
        with patch.object(sys, "argv", test_argv):
            import_recipe_workflow.main()

        # Check subprocess.run was called
        self.assertTrue(mock_run.called)
        
    @patch("subprocess.run")
    @patch("sys.exit")
    @patch("os.path.exists")
    def test_workflow_issue(self, mock_exists, mock_exit, mock_run):
        spec = importlib.util.spec_from_file_location("import_recipe_workflow", "scripts/import_recipe_workflow.py")
        import_recipe_workflow = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(import_recipe_workflow)

        import_recipe_workflow.find_newest_cook_file = MagicMock(return_value="cook/main/DummyRecipe.cook")
        mock_exists.return_value = True

        # Setup mock side effect for subprocess.run
        def run_side_effect(cmd, *args, **kwargs):
            res = MagicMock()
            res.returncode = 0
            if "gh" in cmd:
                res.stdout = '{"title": "Dummy Issue", "body": "Check this recipe: http://example.com/recipe-from-issue"}'
            else:
                res.stdout = ""
            res.stderr = ""
            return res

        mock_run.side_effect = run_side_effect

        test_argv = ["scripts/import_recipe_workflow.py", "123", "main"]
        with patch.object(sys, "argv", test_argv):
            import_recipe_workflow.main()

        self.assertTrue(mock_run.called)

if __name__ == "__main__":
    unittest.main()
