import importlib.util
import math
import unittest

AVAILABLE = all(importlib.util.find_spec(name) for name in ("numpy", "scipy", "PIL"))
if AVAILABLE:
    import numpy as np
    from scripts.verify_response import central_width, ellipse_axes, rank_pitch_maps
    from scripts.measure_center_hole import measure_edges
    from scipy import ndimage


@unittest.skipUnless(AVAILABLE, "optional analysis dependencies unavailable")
class AnalysisTests(unittest.TestCase):
    def test_clear_arcs_recover_circle_despite_bottom_shadow(self):
        y, x = np.mgrid[:201, :201]
        # Known physical opening, deliberately displaced from the sampling
        # origin; a bottom shadow removes part of its visible white interior.
        radius = np.hypot(x-101, y-104)
        clear = ndimage.gaussian_filter((radius <= 60).astype(float), 1)*230 + 10
        shadow = np.clip((160-y)/4, 0, 1)
        image = 10 + (clear-10)*shadow
        fits, _, _ = measure_edges(image, (100, 100))
        for name in ("upper_arc", "opposed_side_arcs"):
            self.assertAlmostEqual(fits[name]["diameter_pixels"], 120, delta=.5)
            self.assertAlmostEqual(fits[name]["center_y_pixels"], 104, delta=.5)
        self.assertLess(fits["full_perimeter_shadow_biased"]["diameter_pixels"], 119)

    def test_threshold_width_ignores_bright_neighboring_holes(self):
        coordinates = np.arange(-10, 11, dtype=float)
        profile = np.where((abs(coordinates) <= 3) | (abs(coordinates) >= 7), 100., 0.)
        self.assertEqual(central_width(coordinates, profile, 50), 7)

    def test_rotated_ellipse_recovers_small_axis_difference(self):
        theta = np.linspace(0, 2*math.pi, 720, endpoint=False)
        rotation = .63
        x = 600 + 1001*np.cos(theta)*math.cos(rotation) - 1000*np.sin(theta)*math.sin(rotation)
        y = 900 + 1001*np.cos(theta)*math.sin(rotation) + 1000*np.sin(theta)*math.cos(rotation)
        result = ellipse_axes(x, y)
        self.assertAlmostEqual(result["axis_ratio"], 1.001, places=8)
        self.assertAlmostEqual(result["semimajor_pixels"], 1001, places=6)

    def test_map_search_recovers_known_start_and_phase_among_octave_alternatives(self):
        midis = [m for m in range(36, 106) if m % 12 in (0, 2, 4, 5, 7, 9, 11)]
        candidates = [m for m in midis if m <= 72]
        bins, phase, period = 1000, 175, 28.126
        folded = np.random.default_rng(2).normal(0, .01, (len(midis), bins))
        holes = []
        for track in range(1, 20):
            event = (43*track*track + 13*track) % bins
            holes.append({"track": track, "theta_radians": -2*math.pi*event/bins})
            folded[midis.index(60) + track-1, (phase+event) % bins] += 10
        result = rank_pitch_maps(folded, holes, candidates, midis, period)
        self.assertEqual(result[0]["start_pitch"], "C4")
        self.assertAlmostEqual(result[0]["phase_seconds"], phase/bins*period)
