import unittest
import math
import xml.etree.ElementTree as ET
from pathlib import Path

from symphonium_disc_maker.geometry import load_geometry, track_radius
from symphonium_disc_maker.arrangement import load_arrangement, normalize_arrangement
from symphonium_disc_maker.svg import build_svg
from symphonium_disc_maker.dxf import build_dxf

ROOT = Path(__file__).resolve().parents[1]
NS = {"svg": "http://www.w3.org/2000/svg"}

def dxf_entities(text):
    values = text.splitlines()
    records = []
    current = None
    for i in range(0, len(values), 2):
        code, value = int(values[i]), values[i + 1]
        if code == 0:
            current = {0: value}
            records.append(current)
        elif current is not None:
            current[code] = value
    return records

def svg_drive_openings(text):
    root = ET.fromstring(text)
    center = float(root.attrib["viewBox"].split()[2]) / 2
    polygons = root.findall("svg:g[@id='cut']/svg:polygon", NS)
    return [
        [(float(x) - center, center - float(y))
         for x, y in (point.split(",") for point in polygon.attrib["points"].split())]
        for polygon in polygons
    ]

def note_centers(arrangement, geometry, start_angle, format):
    if format == "dxf":
        circles = [entity for entity in dxf_entities(build_dxf(
            arrangement, geometry, start_angle_degrees=start_angle, millimeters=False,
        )) if entity[0] == "CIRCLE"]
        return [(float(circle[10]), float(circle[20])) for circle in circles[2:]]
    root = ET.fromstring(build_svg(arrangement, geometry, start_angle_degrees=start_angle))
    center = float(root.attrib["viewBox"].split()[2]) / 2
    circles = root.findall("svg:g[@id='cut']/svg:circle", NS)
    return [(float(circle.attrib["cx"]) - center, center - float(circle.attrib["cy"]))
            for circle in circles[2:]]

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

    def assert_radial_openings(self, openings, scale, tolerance):
        self.assertEqual(len(openings), 143)
        radial_size = self.g["drive_ring"]["radial_size"] * scale
        tangential_size = self.g["drive_ring"]["tangential_size"] * scale
        radius = self.g["drive_ring"]["center_radius"] * scale
        for i, points in enumerate(openings):
            with self.subTest(hole=i):
                self.assertEqual(len(points), 4)
                cx = sum(x for x, _ in points) / 4
                cy = sum(y for _, y in points) / 4
                self.assertAlmostEqual(math.hypot(cx, cy), radius, delta=tolerance)
                angle = 2 * math.pi * i / 143
                self.assertAlmostEqual(cx, radius * math.cos(angle), delta=tolerance)
                self.assertAlmostEqual(cy, radius * math.sin(angle), delta=tolerance)
                radial = (cx / radius, cy / radius)
                for j in range(4):
                    x1, y1 = points[j]
                    x2, y2 = points[(j + 1) % 4]
                    dx, dy = x2 - x1, y2 - y1
                    side = radial_size if j % 2 == 0 else tangential_size
                    self.assertAlmostEqual(math.hypot(dx, dy), side, delta=tolerance)
                    along_radial = abs(dx * radial[0] + dy * radial[1])
                    along_tangent = abs(-dx * radial[1] + dy * radial[0])
                    self.assertAlmostEqual(along_radial, radial_size if j % 2 == 0 else 0, delta=tolerance)
                    self.assertAlmostEqual(along_tangent, 0 if j % 2 == 0 else tangential_size, delta=tolerance)

    def test_svg_drive_holes_follow_radial_tangential_axes(self):
        self.assert_radial_openings(svg_drive_openings(build_svg(self.a, self.g)), 1, 0.000002)

    def test_dxf_drive_holes_follow_radial_tangential_axes_in_both_units(self):
        for millimeters, scale in ((True, 25.4), (False, 1)):
            entities = dxf_entities(build_dxf(self.a, self.g, millimeters=millimeters))
            lines = [entity for entity in entities if entity[0] == "LINE"]
            self.assertEqual(len(lines), 572)
            openings = [
                [(float(line[10]), float(line[20])) for line in lines[i:i + 4]]
                for i in range(0, len(lines), 4)
            ]
            self.assert_radial_openings(openings, scale, 0.000002)
            for i, line in enumerate(lines):
                following = lines[(i // 4) * 4 + (i + 1) % 4]
                self.assertEqual((line[11], line[21]), (following[10], following[20]))

    def test_svg_and_dxf_drive_geometry_matches(self):
        openings = svg_drive_openings(build_svg(self.a, self.g))
        lines = [entity for entity in dxf_entities(build_dxf(self.a, self.g))
                 if entity[0] == "LINE"]
        for points, start in zip(openings, range(0, len(lines), 4)):
            for (x, y), line in zip(points, lines[start:start + 4]):
                self.assertAlmostEqual(x * 25.4, float(line[10]), delta=0.00002)
                self.assertAlmostEqual(y * 25.4, float(line[20]), delta=0.00002)

    def test_sampler_note_holes_are_spaced_18_degrees_including_wrap(self):
        circles = [entity for entity in dxf_entities(build_dxf(self.a, self.g))
                   if entity[0] == "CIRCLE"]
        self.assertEqual(len(circles), 22)
        self.assertAlmostEqual(float(circles[0][40]) * 2, 177.8)
        angles = sorted(math.degrees(math.atan2(float(c[20]), float(c[10]))) % 360
                        for c in circles[2:])
        for i, angle in enumerate(angles):
            self.assertAlmostEqual((angles[(i + 1) % 20] - angle) % 360, 18, delta=0.00001)

    def test_later_notes_lie_clockwise_on_top_face_in_both_formats(self):
        arrangement = normalize_arrangement({
            "revolution_seconds": 28.126,
            "events": [{"time_seconds": 0, "note": "C4"},
                       {"time_seconds": 28.126 / 4, "note": "C5"}],
        }, self.g)
        expected = [(track_radius(self.g, 1), 0), (0, -track_radius(self.g, 8))]
        for format in ("svg", "dxf"):
            with self.subTest(format=format):
                points = note_centers(arrangement, self.g, 0, format)
                self.assertEqual(len(points), 2)
                for (x, y), (ex, ey) in zip(points, expected):
                    self.assertAlmostEqual(x, ex, delta=0.0001)
                    self.assertAlmostEqual(y, ey, delta=0.0001)
        root = ET.fromstring(build_svg(arrangement, self.g, start_angle_degrees=0))
        center = float(root.attrib["viewBox"].split()[2]) / 2
        labels = root.findall("svg:g[@id='annotation']/svg:text", NS)
        self.assertEqual([label.text for label in labels], ["C4", "C5"])
        self.assertAlmostEqual(float(labels[0].attrib["y"]), center, delta=0.0001)
        self.assertAlmostEqual(float(labels[1].attrib["x"]), center, delta=0.0001)
        self.assertGreater(float(labels[1].attrib["y"]), center)

    def test_start_angle_rotates_music_without_changing_drive_holes(self):
        angle = math.radians(37)
        cosine, sine = math.cos(angle), math.sin(angle)
        for format in ("svg", "dxf"):
            before = note_centers(self.a, self.g, 17, format)
            after = note_centers(self.a, self.g, 54, format)
            for (x, y), (ax, ay) in zip(before, after):
                self.assertAlmostEqual(ax, x * cosine - y * sine, delta=0.0002)
                self.assertAlmostEqual(ay, x * sine + y * cosine, delta=0.0002)
        self.assertEqual(
            svg_drive_openings(build_svg(self.a, self.g, start_angle_degrees=17)),
            svg_drive_openings(build_svg(self.a, self.g, start_angle_degrees=54)),
        )
        drive_before = [entity for entity in dxf_entities(build_dxf(self.a, self.g, start_angle_degrees=17))
                        if entity[0] == "LINE"]
        drive_after = [entity for entity in dxf_entities(build_dxf(self.a, self.g, start_angle_degrees=54))
                       if entity[0] == "LINE"]
        self.assertEqual(drive_before, drive_after)

    def test_svg_and_dxf_note_centers_match(self):
        svg_points = note_centers(self.a, self.g, 230, "svg")
        dxf_points = note_centers(self.a, self.g, 230, "dxf")
        self.assertEqual(len(svg_points), 20)
        self.assertEqual(len(dxf_points), 20)
        for (x, y), (dx, dy) in zip(svg_points, dxf_points):
            self.assertAlmostEqual(x, dx, delta=0.0001)
            self.assertAlmostEqual(y, dy, delta=0.0001)

if __name__ == "__main__":
    unittest.main()
