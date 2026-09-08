"""Reserved-domain fixtures; no ownership, publication or deployment proof."""

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import runpy
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

SITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SITE))
import build as builder
from publication import parse_publication
from test_examples import fixture
from examples import prepare_example
from libreevolve.alpha_share_record import payload_sha256


def config(**changes):
    value = dict(origin="https://fixture.example.test", base_path="/preview/",
                 ownership_evidence="synthetic-private-evidence", authorization_reference="synthetic-private-approval",
                 public_example_sha256=None)
    value.update(changes)
    data = json.dumps(value).encode()
    return parse_publication(data, approved_sha256=hashlib.sha256(data).hexdigest(), approved_by="synthetic-private-operator")


class PublicationTests(unittest.TestCase):
    def test_receipt_write_failure_creates_no_release_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            publication = config()
            source = root / "config.json"
            source.write_bytes(publication.configuration_bytes)
            output = root / "release"
            argv = [str(SITE / "build.py"), "--output", str(output), "--base-path", "/preview/",
                    "--publication-config", str(source), "--publication-sha256", publication.approval_sha256,
                    "--publication-approved-by", "fixture-reviewer", "--publication-receipt", str(root / "receipt.json")]
            with patch.object(sys, "argv", argv), patch("examples.write_private_receipt", side_effect=OSError("simulated receipt failure")):
                with self.assertRaisesRegex(OSError, "simulated receipt failure"):
                    runpy.run_path(str(SITE / "build.py"), run_name="__main__")
            self.assertFalse(output.exists())

    def test_release_example_requires_exact_disclosure_digest_and_stays_noindex(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = fixture()
            source = root / "record.json"
            source.write_text(json.dumps(record))
            digest = payload_sha256(record)
            example = prepare_example(source, approved_sha256=digest, approved_by="private-example-reviewer", base="/preview/")
            refused = root / "refused"
            with self.assertRaises(ValueError):
                builder.build(refused, base="/preview/", example=example, publication=config())
            self.assertFalse(refused.exists())
            output = root / "accepted"
            builder.build(output, base="/preview/", example=example, publication=config(public_example_sha256=digest))
            page = (output / "preview/examples/synthetic-fixture/index.html").read_text()
            self.assertIn('content="noindex,nofollow"', page)
            self.assertIn("SYNTHETIC FIXTURE", page)
            self.assertNotIn('rel="canonical"', page)
            self.assertNotIn("synthetic-fixture", (output / "preview/sitemap.xml").read_text())
            for path in output.rglob("*"):
                if path.is_file():
                    self.assertNotIn("private-example-reviewer", path.read_text())

    def test_cli_requires_complete_approval_and_keeps_receipt_private(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            publication = config()
            source = root / "private-config.json"
            source.write_bytes(publication.configuration_bytes)
            output, receipt = root / "output", root / "receipt.json"
            command = [sys.executable, str(SITE / "build.py"), "--output", str(output), "--base-path", "/preview/",
                       "--publication-config", str(source)]
            rejected = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 2)
            self.assertFalse(output.exists())
            accepted = subprocess.run(command + ["--publication-sha256", publication.approval_sha256,
                                      "--publication-approved-by", "synthetic-private-operator",
                                      "--publication-receipt", str(receipt)], capture_output=True, text=True)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertIn("release_candidate", accepted.stdout)
            self.assertEqual(json.loads(receipt.read_text())["approved_by"], "synthetic-private-operator")
            for path in output.rglob("*"):
                if path.is_file():
                    self.assertNotIn("synthetic-private", path.read_text())

    def test_cli_receipt_inside_output_or_existing_is_rejected_without_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            publication = config()
            source = root / "config.json"
            source.write_bytes(publication.configuration_bytes)
            existing = root / "existing.json"
            existing.write_text("preserve fixture")
            for index, receipt in enumerate((existing, root / "output-1" / "receipt.json")):
                output = root / f"output-{index}"
                command = [sys.executable, str(SITE / "build.py"), "--output", str(output),
                           "--base-path", "/preview/", "--publication-config", str(source),
                           "--publication-sha256", publication.approval_sha256,
                           "--publication-approved-by", "fixture-reviewer", "--publication-receipt", str(receipt)]
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())
            self.assertEqual(existing.read_text(), "preserve fixture")

    def test_metadata_sitemap_privacy_and_no_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "release"
            with patch("socket.socket", side_effect=AssertionError("no network")), patch("subprocess.Popen", side_effect=AssertionError("no execution")):
                manifest = builder.build(output, base="/preview/", publication=config())
            self.assertEqual(manifest["mode"], "release_candidate")
            for page in output.rglob("*.html"):
                value = page.read_text()
                relative = page.parent.relative_to(output).as_posix() + "/"
                self.assertIn(f'rel="canonical" href="https://fixture.example.test/{relative}"', value)
                self.assertIn('property="og:url"', value)
                self.assertIn('type="application/ld+json"', value)
                self.assertNotIn("noindex", value)
            for path in output.rglob("*"):
                if path.is_file():
                    self.assertNotIn("synthetic-private", path.read_text())
            sitemap = ET.parse(output / "preview/sitemap.xml")
            self.assertEqual(len(sitemap.getroot()), 14)
            self.assertNotIn("examples/", (output / "preview/sitemap.xml").read_text())
            self.assertIn("Disallow: /preview/examples/", (output / "robots.txt").read_text())

    def test_malformed_origin_configuration_and_hash_rejected(self):
        for origin in ("https://single-label", "https://" + "a" * 64 + ".test", "https://-label.test", "https://label-.test", "https://one..test"):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                config(origin=origin)
        self.assertEqual(config(origin="https://two--hyphens.example.test").origin, "https://two--hyphens.example.test")
        duplicate = config().configuration_bytes.replace(b'"origin":', b'"origin":"https://different.example.test", "origin":', 1)
        with self.assertRaises(ValueError):
            parse_publication(duplicate, approved_sha256=hashlib.sha256(duplicate).hexdigest(), approved_by="reviewer")
        for origin in ("http://fixture.example.test", "https://user@fixture.example.test", "https://fixture.example.test/", "https://fixture.example.test:443", "https://127.0.0.1", "https://example.invalid", "https://fixture.example.test?x=1", "https://fixture.example.test#x", 'https://bad<host.test'):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                config(origin=origin)
        with self.assertRaises(ValueError):
            parse_publication(b"{}", approved_sha256="0" * 64, approved_by="reviewer")
        for changes in ({"ownership_evidence": ""}, {"unexpected": "private"}, {"base_path": "/../"}, {"public_example_sha256": "wrong"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                config(**changes)

    def test_modified_config_base_or_example_approval_rejected_before_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            for index, publication in enumerate((replace(config(), origin="https://other.example.test"), config(base_path="/"), config(public_example_sha256="a" * 64))):
                output = Path(tmp) / str(index)
                with self.subTest(index=index), self.assertRaises(ValueError):
                    builder.build(output, base="/preview/", publication=publication)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
