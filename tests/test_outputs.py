import unittest
from pathlib import Path

from symphonium_disc_maker.geometry import load_geometry
from symphonium_disc_maker.arrangement import load_arrangement, normalize_arrangement
from symphonium_disc_maker.svg import build_svg
from symphonium_disc_maker.dxf import build_dxf

ROOT = Path(__file__).resolve().parents[1]

class OutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = load_geometry(ROOT / "geometry.json")
        cls.a = normalize_arrangement(
            load_arrangement(ROOT / "examples" / "pachelbel_sampler.json"),
            cls.g
        )

    def test_pachelbel_has_20_attacks(self):
        self.assertEqual(len(self.a["events"]), 20)

    def test_svg_contains_20_note_circles_plus_geometry(self):
        svg = build_svg(self.a, self.g)
        self.assertIn("<svg", svg)
        self.assertIn('id="cut"', svg)

    def test_dxf_is_mm_and_contains_entities(self):
        dxf = build_dxf(self.a, self.g)
        self.assertIn("$INSUNITS", dxf)
        self.assertIn("CIRCLE", dxf)
        self.assertIn("LINE", dxf)

if __name__ == "__main__":
    unittest.main()
