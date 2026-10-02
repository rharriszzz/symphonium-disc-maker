import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PrototypePackTests(unittest.TestCase):
    def test_reviewable_pack_matches_current_inputs_sources_and_file_hashes(self):
        pack = ROOT / "prototype_pack"
        manifest = json.loads((pack/"manifest.json").read_text())
        for entry in manifest["inputs"].values():
            self.assertEqual(hashlib.sha256((ROOT/entry["path"]).read_bytes()).hexdigest(), entry["sha256"])
        for name, expected in manifest["generator_sources"].items():
            with self.subTest(source=name):
                self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), expected,
                                 "Regenerate prototype_pack after changing its sources.")
        for name, entry in manifest["files"].items():
            with self.subTest(artifact=name):
                contents = (pack/name).read_bytes()
                self.assertEqual(hashlib.sha256(contents).hexdigest(), entry["sha256"])
                self.assertEqual(len(contents), entry["bytes"])
        self.assertEqual((pack/"geometry.json").read_bytes(), (ROOT/"geometry.json").read_bytes())
        self.assertEqual((pack/"arrangement.json").read_bytes(),
                         (ROOT/"examples/pachelbel_sampler.json").read_bytes())
