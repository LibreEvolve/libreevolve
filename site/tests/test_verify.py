"""Artifact inventory verification, not provenance attestation."""

import hashlib
import json
from pathlib import Path
import sys
import unittest

from _support import temporary_directory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify import verify


class VerifyTests(unittest.TestCase):
    def test_valid_modified_extra_missing_and_unsafe_artifacts(self):
        with temporary_directory() as tmp:
            root = Path(tmp)
            content = root / "index.html"
            content.write_bytes(b"fixture")
            manifest = root / "build-manifest.json"
            inventory = {"output_sha256": {"index.html": hashlib.sha256(b"fixture").hexdigest()}}
            manifest.write_text(json.dumps(inventory), encoding="utf-8")
            self.assertEqual(verify(root), 1)
            content.write_bytes(b"modified")
            with self.assertRaises(ValueError):
                verify(root)
            content.write_bytes(b"fixture")
            extra = root / "private-receipt.json"
            extra.write_text("private fixture", encoding="utf-8")
            with self.assertRaises(ValueError):
                verify(root)
            extra.unlink()
            content.unlink()
            with self.assertRaises(ValueError):
                verify(root)
            for name in ("../escape", "examples/..\\escape", "/absolute", "C:escape"):
                inventory["output_sha256"] = {name: "a" * 64}
                manifest.write_text(json.dumps(inventory), encoding="utf-8")
                with self.subTest(name=name), self.assertRaises(ValueError):
                    verify(root)


if __name__ == "__main__":
    unittest.main()
