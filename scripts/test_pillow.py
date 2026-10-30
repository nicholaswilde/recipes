################################################################################
#
# test_pillow.py
# ----------------
# Smoke test the Pillow code paths used by the image scripts
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 29 Oct 2026
# @version 0.1.0
#
################################################################################

import os
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from import_pdf_workflow import auto_crop_recipe_image  # noqa: E402

# Same one-liner used as the cwebp fallback in move.sh and optimize_images.sh.
WEBP_ONELINER = (
    "from PIL import Image, ImageFile; "
    "ImageFile.LOAD_TRUNCATED_IMAGES = True; "
    "Image.open('{src}').convert('RGB').save('{dst}', 'WEBP', quality=80)"
)


class TestPillow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def path(self, name):
        return os.path.join(self.dir, name)

    def convert(self, src):
        dst = os.path.splitext(src)[0] + ".webp"
        cmd = WEBP_ONELINER.format(src=src, dst=dst)
        subprocess.run([sys.executable, "-c", cmd], check=True)
        with Image.open(dst) as out:
            self.assertEqual(out.format, "WEBP")
            self.assertEqual(out.mode, "RGB")
            return out.size

    def test_webp_from_jpeg(self):
        src = self.path("a.jpg")
        Image.new("RGB", (64, 48), (200, 100, 50)).save(src, "JPEG")
        self.assertEqual(self.convert(src), (64, 48))

    def test_webp_from_rgba_png(self):
        src = self.path("b.png")
        Image.new("RGBA", (32, 32), (0, 128, 255, 100)).save(src, "PNG")
        self.assertEqual(self.convert(src), (32, 32))

    def test_webp_from_truncated_jpeg(self):
        src = self.path("c.jpg")
        Image.effect_noise((128, 128), 64).convert("RGB").save(src, "JPEG")
        with open(src, "rb") as f:
            data = f.read()
        with open(src, "wb") as f:
            f.write(data[: len(data) * 2 // 3])
        self.assertEqual(self.convert(src), (128, 128))

    def test_auto_crop_recipe_image(self):
        page = self.path("page.png")
        out = self.path("hero.jpg")
        img = Image.new("RGB", (1000, 1400), "white")
        img.paste((180, 60, 30), (600, 200, 900, 500))
        img.save(page)
        self.assertTrue(auto_crop_recipe_image(page, out))
        with Image.open(out) as hero:
            self.assertEqual(hero.format, "JPEG")
            w, h = hero.size
            # Box is the red block plus up to 15px pad, on a 10px scan grid.
            self.assertTrue(290 <= w <= 330 and 290 <= h <= 330, hero.size)

    def test_auto_crop_blank_page(self):
        page = self.path("blank.png")
        Image.new("RGB", (1000, 1400), "white").save(page)
        self.assertFalse(auto_crop_recipe_image(page, self.path("x.jpg")))


if __name__ == "__main__":
    unittest.main()
