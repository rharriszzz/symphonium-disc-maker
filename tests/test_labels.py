import contextlib
import io
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from symphonium_disc_maker.cli import main
from symphonium_disc_maker.labels import build_label_sheet_svg

ROOT = Path(__file__).resolve().parents[1]
NS = {"svg": "http://www.w3.org/2000/svg"}


class LabelTests(unittest.TestCase):
    def test_print_and_cut_files_keep_the_same_layout(self):
        combined = ET.fromstring(build_label_sheet_svg("PACHELBEL", "Sampler"))
        cut = ET.fromstring(build_label_sheet_svg("PACHELBEL", "Sampler", mode="cut"))
        printed = ET.fromstring(build_label_sheet_svg("PACHELBEL", "Sampler", mode="print"))
        self.assertEqual(len(cut.findall(".//svg:circle", NS)), 40)
        self.assertEqual(len(printed.findall(".//svg:text", NS)), 40)
        self.assertEqual(cut.findall(".//svg:text", NS), [])
        self.assertEqual(printed.findall(".//svg:circle", NS), [])
        self.assertEqual(
            [el.attrib for el in cut.findall(".//svg:circle", NS)],
            [el.attrib for el in combined.findall(".//svg:circle", NS)],
        )
        self.assertEqual(
            [el.attrib for el in printed.findall(".//svg:text", NS)],
            [el.attrib for el in combined.findall(".//svg:text", NS)],
        )

    def test_text_stays_above_and_below_center_hole(self):
        root = ET.fromstring(build_label_sheet_svg("PACHELBEL", "Sampler"))
        hole = root.findall(".//svg:circle", NS)[1]
        cy, radius = float(hole.attrib["cy"]), float(hole.attrib["r"])
        title, subtitle = root.findall(".//svg:text", NS)[:2]
        self.assertLess(float(title.attrib["y"]) + 0.03, cy - radius)
        self.assertGreater(float(subtitle.attrib["y"]) - 0.075, cy + radius)

    def test_invalid_layouts_are_rejected(self):
        for kwargs in (
            {"columns": 0}, {"rows": -1}, {"label_diameter_in": 2.0},
            {"label_diameter_in": float("nan")}, {"center_hole_diameter_in": 1.5},
            {"mode": "unknown"},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                build_label_sheet_svg("Test", **kwargs)

    def test_special_characters_remain_valid_xml(self):
        root = ET.fromstring(build_label_sheet_svg('A & B <C>', '"Sampler"'))
        self.assertEqual(root.find(".//svg:text", NS).text, "A & B <C>")

    def test_cli_rejects_a_label_that_covers_note_holes(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "label.svg"
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exc:
                main(["labels", "--title", "Test", "--geometry", str(ROOT / "geometry.json"),
                      "--diameter", "1.8", "-o", str(output)])
            self.assertEqual(exc.exception.code, 2)
            self.assertFalse(output.exists())

    def test_cli_accepts_adjustable_center_hole_and_cut_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "label.svg"
            self.assertEqual(main([
                "labels", "--title", "Test", "--geometry", str(ROOT / "geometry.json"),
                "--center-hole", "0.25", "--mode", "cut", "--rows", "1",
                "--columns", "1", "-o", str(output),
            ]), 0)
            root = ET.fromstring(output.read_text())
            self.assertEqual(len(root.findall(".//svg:circle", NS)), 2)
            self.assertEqual(root.findall(".//svg:circle", NS)[1].attrib["r"], "0.1250")


if __name__ == "__main__":
    unittest.main()
