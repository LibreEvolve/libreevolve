"""Frozen record integration only; synthetic fixtures are never live evidence."""

from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SITE))
import build as builder
from examples import prepare_example, receipt_destination
from libreevolve.alpha_share_record import payload_sha256


def fixture():
    return dict(schema_version="libreevolve.public_result.v1", public_result_id="synthetic-fixture",
                product_status="engineering preview", evidence_class="synthetic_fixture",
                run_status="aborted", selected_source="unknown", candidate_retention="unknown",
                baseline=None, candidate=None, checks=[],
                observed_activity=dict(calls=None, elapsed_seconds=None),
                usage=dict(tokens=None, cost_usd=None, status="unknown"),
                public_provenance=dict(source_commit=None, candidate_sha256=None, validator_sha256=None),
                approved_source_url=None, limitations=["Synthetic fixture, not a measured experiment."])


class ExampleTests(unittest.TestCase):
    def write_record(self, directory, value=None):
        data = fixture() if value is None else value
        path = Path(directory) / "record.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path, payload_sha256(data)

    def test_frozen_render_and_site_keep_receipt_private(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = self.write_record(tmp)
            output = Path(tmp) / "site"
            with patch("subprocess.Popen", side_effect=AssertionError("no execution")), patch("socket.socket", side_effect=AssertionError("no network")):
                prepared = prepare_example(path, approved_sha256=digest, approved_by="private-fixture-reviewer", base="/preview/")
                manifest = builder.build(output, base="/preview/", example=prepared)
            self.assertEqual(prepared.private_receipt["approved_by"], "private-fixture-reviewer")
            self.assertEqual(manifest["example"]["payload_sha256"], digest)
            self.assertEqual(len(prepared.files), 4)
            for content in prepared.files.values():
                self.assertNotIn("private-fixture-reviewer", content)
            page = (output / "preview/examples/synthetic-fixture/index.html").read_text()
            self.assertIn("SYNTHETIC FIXTURE", page)
            self.assertIn('content="noindex,nofollow"', page)
            self.assertIn('href="/preview/experiments/"', page)
            self.assertIn("Run: aborted", page)
            self.assertIn("unknown", page)
            self.assertIn("Inspect synthetic fixture", (output / "preview/experiments/index.html").read_text())
            self.assertNotIn("private-fixture-reviewer", (output / "build-manifest.json").read_text())

    def test_exact_approval_private_fields_and_source_link_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = self.write_record(tmp)
            with self.assertRaises(ValueError):
                prepare_example(path, approved_sha256="0" * 64, approved_by="reviewer")
            data = fixture()
            data["approved_source_url"] = "https://github.com/LibreEvolve/libreevolve"
            path, digest = self.write_record(tmp, data)
            with self.assertRaises(ValueError):
                prepare_example(path, approved_sha256=digest, approved_by="reviewer")
            data["private_path"] = "/sensitive/example"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                prepare_example(path, approved_sha256=digest, approved_by="reviewer", approve_source_link=True)

    def test_invalid_candidate_does_not_turn_into_a_win(self):
        data = fixture()
        metric = dict(corpus_id="synthetic-corpus", corpus_sha256="a" * 64, split="training", case_count=1,
                      valid=True, total_bins=10, quality=0.5)
        data["baseline"] = metric
        data["candidate"] = dict(metric, valid=False, total_bins=0, quality=0)
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = self.write_record(tmp, data)
            prepared = prepare_example(path, approved_sha256=digest, approved_by="reviewer")
            text = prepared.files["examples/synthetic-fixture/result.txt"]
            self.assertIn("Candidate outcome: invalid", text)
            self.assertIn("Bin reduction (%): unknown", text)
            self.assertNotIn("100", text)

    def test_receipt_and_example_paths_are_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "site"
            output.mkdir()
            with self.assertRaises(ValueError):
                receipt_destination(output / "receipt.json", output)
            existing = Path(tmp) / "existing.json"
            existing.write_text("preserve")
            with self.assertRaises(ValueError):
                receipt_destination(existing, output)
            path, digest = self.write_record(tmp)
            prepared = prepare_example(path, approved_sha256=digest, approved_by="reviewer")
            with self.assertRaises(ValueError):
                builder.build(Path(tmp) / "mismatch", base="/preview/", example=prepared)
            malformed = replace(prepared, files={"../escape.html": "wrong"})
            with self.assertRaises(ValueError):
                builder.build(Path(tmp) / "unsafe", example=malformed)
            self.assertFalse((Path(tmp) / "unsafe").exists())

    def test_cli_requires_approval_and_writes_external_private_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = self.write_record(tmp)
            output, receipt = Path(tmp) / "site", Path(tmp) / "private-receipt.json"
            command = [sys.executable, str(SITE / "build.py"), "--output", str(output), "--example-record", str(path)]
            refused = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(refused.returncode, 2)
            self.assertFalse(output.exists())
            accepted = subprocess.run(command + ["--example-sha256", digest, "--approved-by", "private-cli-reviewer", "--example-receipt", str(receipt)], capture_output=True, text=True)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertEqual(json.loads(receipt.read_text())["approved_by"], "private-cli-reviewer")
            self.assertTrue((output / "examples/synthetic-fixture/index.html").is_file())
            for file in output.rglob("*"):
                if file.is_file():
                    self.assertNotIn("private-cli-reviewer", file.read_text())

    def test_modified_public_projection_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = self.write_record(tmp)
            prepared = prepare_example(path, approved_sha256=digest, approved_by="reviewer")
            altered = [
                replace(prepared, files={**prepared.files, "examples/synthetic-fixture/secret.txt": "private"}),
                replace(prepared, files={key.replace("synthetic-fixture", "another-id"): value for key, value in prepared.files.items()}),
                replace(prepared, summary_html="<p>forged</p>"),
                replace(prepared, public_identity={**prepared.public_identity, "private_actor": "private"}),
                replace(prepared, files={**prepared.files, "examples/..\\..\\escape.html": "private"}),
                replace(prepared, files={**prepared.files, "examples/synthetic-fixture/result.txt": "forged"}),
            ]
            for index, example in enumerate(altered):
                output = Path(tmp) / f"rejected-{index}"
                with self.subTest(index=index), self.assertRaises(ValueError):
                    builder.build(output, example=example)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
