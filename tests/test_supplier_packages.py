import hashlib
import json
from pathlib import Path
import unittest
import zipfile

from scripts.build_supplier_packages import audit_dxf

ROOT = Path(__file__).resolve().parents[1]


class SupplierPackageTests(unittest.TestCase):
    def setUp(self):
        self.geometry = json.loads((ROOT/"geometry.json").read_text())
        self.dxf = (ROOT/"prototype_pack/pachelbel_cut_mm.dxf").read_text()
        self.counts = {"CIRCLE": 22, "LINE": 572}

    def test_exported_dxf_has_closed_individual_contours_and_correct_sizes(self):
        audit, _, _ = audit_dxf(self.dxf, self.geometry, self.counts)
        self.assertEqual(audit["total_closed_contours"], 165)
        self.assertEqual(audit["closed_drive_contours"], 143)
        self.assertAlmostEqual(audit["outside_diameter_mm"], 177.8)
        self.assertAlmostEqual(audit["center_hole_diameter_mm"], 5.08)

    def test_wrong_units_are_rejected(self):
        bad = self.dxf.replace("$INSUNITS\n70\n4\n", "$INSUNITS\n70\n1\n")
        with self.assertRaisesRegex(ValueError, "millimeters"):
            audit_dxf(bad, self.geometry, self.counts)

    def test_broken_endpoint_is_rejected_even_with_correct_entity_counts(self):
        prefix, remainder = self.dxf.split("0\nLINE\n", 1)
        block, tail = remainder.split("0\nLINE\n", 1)
        values = block.splitlines()
        values[values.index("20")+1] = "0.123456"
        bad = prefix + "0\nLINE\n" + "\n".join(values) + "\n0\nLINE\n" + tail
        with self.assertRaisesRegex(ValueError, "open or branching"):
            audit_dxf(bad, self.geometry, self.counts)

    def test_duplicated_line_is_rejected_even_with_correct_entity_counts(self):
        prefix, remainder = self.dxf.split("0\nLINE\n", 1)
        first, remainder = remainder.split("0\nLINE\n", 1)
        _, remainder = remainder.split("0\nLINE\n", 1)
        bad = prefix + "0\nLINE\n" + first + "0\nLINE\n" + first + "0\nLINE\n" + remainder
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit_dxf(bad, self.geometry, self.counts)

    def test_committed_packages_contain_current_exact_cut_file_and_supplier_requests(self):
        folder = ROOT/"supplier_packages"
        manifest = json.loads((folder/"manifest.json").read_text())
        self.assertEqual(manifest["pack_manifest_sha256"],
                         hashlib.sha256((ROOT/"prototype_pack/manifest.json").read_bytes()).hexdigest())
        self.assertEqual(manifest["generator_sha256"],
                         hashlib.sha256((ROOT/"scripts/build_supplier_packages.py").read_bytes()).hexdigest())
        for name, expected in manifest["files"].items():
            self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(), expected)
        for supplier, info in manifest["packages"].items():
            with zipfile.ZipFile(folder/info["archive"]) as archive:
                self.assertEqual(set(archive.namelist()), {"pachelbel_cut_mm.dxf", "reference_drawing.pdf",
                    "quote_request.txt", "README.txt", "package_manifest.json"})
                self.assertIsNone(archive.testzip())
                self.assertEqual(archive.read("pachelbel_cut_mm.dxf"),
                                 (ROOT/"prototype_pack/pachelbel_cut_mm.dxf").read_bytes())
                self.assertEqual(archive.read("reference_drawing.pdf"), (folder/"reference_drawing.pdf").read_bytes())
                embedded = json.loads(archive.read("package_manifest.json"))
                self.assertEqual(embedded["files"], info["members"])
                for name, expected in embedded["files"].items():
                    self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), expected)
                request = archive.read("quote_request.txt").decode()
                material = "PETG at 0.020" if supplier == "xometry" else "polypropylene at 0.030"
                self.assertIn(material, request)
                self.assertIn("full thickness", request)
                self.assertNotIn("possibly wider rounded", request)
