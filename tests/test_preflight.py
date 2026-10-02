import copy
from pathlib import Path
import unittest

from symphonium_disc_maker.arrangement import load_arrangement, normalize_arrangement
from symphonium_disc_maker.geometry import load_geometry
from symphonium_disc_maker.preflight import polygon_distance, prototype_preflight

ROOT = Path(__file__).resolve().parents[1]


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.geometry = load_geometry(ROOT / "geometry.json")
        self.arrangement = normalize_arrangement(
            load_arrangement(ROOT / "examples/pachelbel_sampler.json"), self.geometry)

    def test_sampler_has_positive_clearances_and_expected_entities(self):
        result = prototype_preflight(self.arrangement, self.geometry)
        self.assertEqual(result["expected_dxf_counts"], {"CIRCLE": 22, "LINE": 572})
        self.assertEqual(result["tracks_present"], list(range(1, 21)))
        self.assertAlmostEqual(result["clearances_in"]["drive_to_drive"], .05601714, places=7)
        self.assertAlmostEqual(result["clearances_in"]["drive_to_outer_edge"], .07670422, places=7)
        self.assertAlmostEqual(result["clearances_in"]["label_to_innermost_possible_music_hole"], .14168)
        self.assertTrue(all(value > 0 for value in result["clearances_in"].values()))

    def test_crossing_polygons_with_no_contained_vertices_touch(self):
        horizontal = [(-2, -.1), (2, -.1), (2, .1), (-2, .1)]
        vertical = [(-.1, -2), (.1, -2), (.1, 2), (-.1, 2)]
        self.assertEqual(polygon_distance(horizontal, vertical), 0)

    def test_overlapping_drive_openings_are_rejected(self):
        self.geometry["drive_ring"]["tangential_size"] = .16
        with self.assertRaisesRegex(ValueError, "drive_to_drive"):
            prototype_preflight(self.arrangement, self.geometry)

    def test_duplicate_music_holes_are_rejected(self):
        duplicate = copy.deepcopy(self.arrangement)
        duplicate["events"].append(dict(duplicate["events"][0]))
        with self.assertRaisesRegex(ValueError, "music_to_music"):
            prototype_preflight(duplicate, self.geometry)

    def test_music_hole_inside_drive_opening_is_rejected(self):
        self.geometry["note_system"]["inner_track_center_radius"] = 3.373
        arrangement = normalize_arrangement({"events": [{"time_seconds": 0, "track": 1}]}, self.geometry)
        with self.assertRaisesRegex(ValueError, "music_to_drive"):
            prototype_preflight(arrangement, self.geometry, start_angle_degrees=0)

    def test_label_touching_music_ring_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "label_to_innermost_possible_music_hole"):
            prototype_preflight(self.arrangement, self.geometry, label_diameter_in=1.8)
