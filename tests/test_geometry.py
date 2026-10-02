import json
import unittest
from pathlib import Path

from symphonium_disc_maker.geometry import load_geometry, track_radius, note_to_track, drive_hole_vertices

ROOT = Path(__file__).resolve().parents[1]

class GeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = load_geometry(ROOT / "geometry.json")

    def test_track_pitch(self):
        self.assertAlmostEqual(track_radius(self.g, 2) - track_radius(self.g, 1), 0.117921)

    def test_outer_track(self):
        expected = 0.94968 + 19 * 0.117921
        self.assertAlmostEqual(track_radius(self.g, 20), expected)

    def test_note_mapping(self):
        self.assertEqual(note_to_track(self.g, "C4"), 1)
        self.assertEqual(note_to_track(self.g, "A6"), 20)

    def test_legacy_square_geometry_remains_supported(self):
        legacy = {"drive_ring": {"hole_count": 4, "center_radius": 3, "hole_size": .1}}
        self.assertEqual(drive_hole_vertices(legacy, 0),
                         [(2.95, -.05), (3.05, -.05), (3.05, .05), (2.95, .05)])

if __name__ == "__main__":
    unittest.main()
