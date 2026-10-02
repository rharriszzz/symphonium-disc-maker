import importlib.util
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
import unittest

from symphonium_disc_maker.cli import main
from symphonium_disc_maker.labels import build_label_sheet_pdf

ROOT = Path(__file__).resolve().parents[1]
MATPLOTLIB = importlib.util.find_spec("matplotlib") is not None


@unittest.skipUnless(MATPLOTLIB, "optional print dependencies unavailable")
class PdfLabelTests(unittest.TestCase):
    def test_pdf_is_exactly_one_us_letter_page(self):
        pdf = build_label_sheet_pdf("PACHELBEL", "Sampler", calibration=True)
        self.assertTrue(pdf.startswith(b"%PDF-"))
        match = re.search(rb"/MediaBox\s*\[([^]]+)\]", pdf)
        self.assertIsNotNone(match)
        self.assertEqual([float(n) for n in match[1].split()], [0, 0, 612, 792])
        self.assertEqual(len(re.findall(rb"/Type /Page\b", pdf)), 1)

    @unittest.skipUnless(shutil.which("pdftoppm") and importlib.util.find_spec("PIL"),
                         "PDF raster scale check needs Poppler and Pillow")
    def test_rendered_circle_and_ruler_have_physical_dimensions(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path/"test.pdf").write_bytes(build_label_sheet_pdf(
                "", columns=1, rows=1, calibration=True))
            subprocess.run(["pdftoppm", "-singlefile", "-r", "144", "-png",
                            str(path/"test.pdf"), str(path/"test")], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            with Image.open(path/"test.png") as image:
                image = image.convert("L")
                self.assertEqual(image.size, (1224, 1584))
                circle_pixels = [x for x in range(image.width) if image.getpixel((x, 792)) < 200]
                self.assertAlmostEqual(circle_pixels[0], 612 - 108, delta=1.5)
                self.assertAlmostEqual(circle_pixels[-1], 612 + 108, delta=1.5)
                ruler_pixels = [x for x in range(70, 250) if image.getpixel((x, 1534)) < 200]
                self.assertAlmostEqual(ruler_pixels[-1] - ruler_pixels[0], 144, delta=2)

    def test_cli_pdf_output_supports_calibrated_fitting_test(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"test.pdf"
            self.assertEqual(main(["labels", "--title", "Test", "--geometry", str(ROOT/"geometry.json"),
                                   "--calibration", "-o", str(path)]), 0)
            self.assertTrue(path.read_bytes().startswith(b"%PDF-"))
