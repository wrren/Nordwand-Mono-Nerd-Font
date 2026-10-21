"""Regression checks for Windows discovery of generated and patched fonts."""

import tempfile
import unittest
from pathlib import Path

from fontTools.ttLib import TTFont

from generate_font import build_font
from scripts.clean_nerd_names import clean_font


class WindowsCodePageTests(unittest.TestCase):
    def test_generated_formats_declare_windows_latin_support(self):
        with tempfile.TemporaryDirectory() as directory:
            build_font(out_root=directory, woff=True, woff2=True)

            for extension in ("otf", "ttf", "woff", "woff2"):
                with self.subTest(format=extension):
                    path = Path(directory, extension, f"NordwandMono-Regular.{extension}")
                    with TTFont(path) as font:
                        self.assertTrue(font["OS/2"].ulCodePageRange1 & 1)
                        ps_name = font["name"].getDebugName(6)
                        self.assertNotIn(" ", ps_name)
                        if "CFF " in font:
                            self.assertEqual(font["CFF "].cff.fontNames, [ps_name])

    def test_nerd_cleanup_repairs_empty_codepages(self):
        with tempfile.TemporaryDirectory() as directory:
            build_font(out_root=directory, ttf=False)
            path = Path(directory, "otf", "NordwandMono-Regular.otf")
            with TTFont(path) as font:
                # Simulate a patcher output made from the old release, whose
                # code-page declarations were empty despite its Latin glyphs.
                font["OS/2"].ulCodePageRange1 = 0
                font["OS/2"].ulCodePageRange2 = 0
                for record in font["name"].names:
                    if record.nameID in (1, 4):
                        record.string = "NordwandMono Nerd Font Mono Plus Font Awesome"
                    elif record.nameID == 6:
                        record.string = "NordwandMonoNFMA-Regular"
                font["CFF "].cff.fontNames = ["NordwandMonoNFMA-Regular"]
                original_cmap = dict(font.getBestCmap())
                original_metrics = dict(font["hmtx"].metrics)
                font.save(path)

            clean_font(path)

            cleaned_path = path.with_name("NordwandMonoNerdFont-Regular.otf")
            with TTFont(cleaned_path) as font:
                self.assertTrue(font["OS/2"].ulCodePageRange1 & 1)
                self.assertEqual(font["name"].getDebugName(1), "NordwandMono Nerd Font")
                self.assertEqual(font.getBestCmap(), original_cmap)
                self.assertEqual(font["hmtx"].metrics, original_metrics)
                self.assertEqual(font["post"].isFixedPitch, 1)
                self.assertEqual(font["CFF "].cff.topDictIndex[0].isFixedPitch, 1)


if __name__ == "__main__":
    unittest.main()
