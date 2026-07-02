import os
import shutil
import tempfile
import unittest
import subprocess

class TestOptimizeImages(unittest.TestCase):
    def setUp(self):
        # Create a temporary workspace
        self.test_dir = tempfile.mkdtemp()
        self.docs_dir = os.path.join(self.test_dir, "docs")
        self.images_dir = os.path.join(self.docs_dir, "assets", "images")
        self.category_dir = os.path.join(self.docs_dir, "desserts")
        
        os.makedirs(self.images_dir)
        os.makedirs(self.category_dir)
        
        # Create dummy JPEG (actually just text or simple bytes)
        self.jpg_path = os.path.join(self.images_dir, "test-cake.jpg")
        with open(self.jpg_path, "wb") as f:
            # Simple minimal 1x1 pixel JPEG bytes or just dummy data
            f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00\x37\xff\xd9")
            
        # Create dummy PNG (minimal 1x1 pixel PNG bytes)
        self.png_path = os.path.join(self.images_dir, "test-cookie.png")
        with open(self.png_path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc` \x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82")

        # Create dummy markdown file
        self.md_path = os.path.join(self.category_dir, "test-recipe.md")
        with open(self.md_path, "w") as f:
            f.write("# Test Recipe\n\n![Cake](../assets/images/test-cake.jpg)\n![Cookie](../assets/images/test-cookie.png)\n")

        # Path to the actual script under test
        self.script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "optimize_images.sh"))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_script_execution(self):
        # The script does not exist yet or we want to verify it conversion.
        # We run the script using the test_dir as the ROOT_DIR by stubbing or env var if we make it configurable.
        # Let's pass ROOT_DIR to script or run it with cwd=self.test_dir if the script uses git rev-parse.
        # But wait, git rev-parse inside self.test_dir won't work unless it's a git repo.
        # Let's initialize a git repo inside self.test_dir so git rev-parse works!
        subprocess.run(["git", "init"], cwd=self.test_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.test_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=self.test_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "add", "."], cwd=self.test_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=self.test_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Verify the script runs and performs conversion
        # We need to make sure the script is executable.
        self.assertTrue(os.path.exists(self.script_path), f"Script {self.script_path} does not exist yet (expected for RED phase)")
        
        result = subprocess.run([self.script_path], cwd=self.test_dir, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Script failed with:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        
        # Check that JPG is converted to WebP and original is deleted
        webp_path = os.path.join(self.images_dir, "test-cake.webp")
        self.assertTrue(os.path.exists(webp_path), "WebP file was not created")
        self.assertFalse(os.path.exists(self.jpg_path), "Original JPEG file was not deleted")
        
        # Check that PNG still exists
        self.assertTrue(os.path.exists(self.png_path), "PNG file was deleted")
        
        # Check that Markdown references are updated
        with open(self.md_path, "r") as f:
            content = f.read()
        self.assertIn("test-cake.webp", content)
        self.assertNotIn("test-cake.jpg", content)
        self.assertIn("test-cookie.png", content)

    def test_script_category_filtering(self):
        # Test running with a specific category
        subprocess.run(["git", "init"], cwd=self.test_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "add", "."], cwd=self.test_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=self.test_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Let's run with a non-existent category first, or "desserts"
        # If we specify "desserts", it should process it.
        result = subprocess.run([self.script_path, "desserts"], cwd=self.test_dir, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        
        webp_path = os.path.join(self.images_dir, "test-cake.webp")
        self.assertTrue(os.path.exists(webp_path), "WebP file was not created under category filtering")

if __name__ == "__main__":
    unittest.main()
