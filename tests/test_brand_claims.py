import json
from pathlib import Path
import tempfile
import unittest

from brand import check_claims


COMMIT = "a" * 40


def claim(
    claim_id="claim.preview",
    *,
    wording="Bounded local work is available in the engineering preview.",
    scope="This wording applies to the named preview lane.",
    status="draft",
    source_refs=None,
):
    return {
        "id": claim_id,
        "wording": wording,
        "scope": scope,
        "evidence_tier": "source",
        "source_refs": source_refs or [{"path": "README.md", "start_line": 1, "end_line": 10}],
        "status": status,
    }


def unit(
    unit_id="copy.preview",
    *,
    kind="product",
    text="Run bounded local work and inspect the saved result.",
    claim_ids=None,
    status="draft",
    usage_condition=None,
):
    value = {
        "id": unit_id,
        "surfaces": ["README"],
        "kind": kind,
        "text": text,
        "claim_ids": ["claim.preview"] if claim_ids is None else claim_ids,
        "status": status,
    }
    if usage_condition is not None:
        value["usage_condition"] = usage_condition
    return value


def documents(*, claim_value=None, unit_value=None, source_commit=COMMIT):
    return (
        {
            "schema_version": "1.0",
            "source_repository": "https://github.com/LibreEvolve/libreevolve",
            "source_commit": source_commit,
            "claims": [claim() if claim_value is None else claim_value],
        },
        {
            "schema_version": "1.0",
            "source_commit": source_commit,
            "units": [unit() if unit_value is None else unit_value],
        },
    )


class ClaimRegistryTests(unittest.TestCase):
    def assert_valid(self, claims, copy):
        self.assertEqual(check_claims.validate(claims, copy), [])

    def test_valid_draft_documents_and_optional_condition(self):
        claims, copy = documents()
        self.assert_valid(claims, copy)
        copy["units"][0]["usage_condition"] = "Use only after reviewing the named evidence."
        self.assert_valid(claims, copy)

    def test_outcome_requires_nonempty_usage_condition(self):
        claims, copy = documents(unit_value=unit(kind="outcome"))
        errors = check_claims.validate(claims, copy)
        self.assertTrue(any("usage_condition" in error for error in errors))
        copy["units"][0]["usage_condition"] = " "
        errors = check_claims.validate(claims, copy)
        self.assertTrue(any("usage_condition" in error and "empty" in error for error in errors))

    def test_present_non_outcome_usage_condition_must_still_be_text(self):
        claims, copy = documents()
        copy["units"][0]["usage_condition"] = None
        errors = check_claims.validate(claims, copy)
        self.assertTrue(any("usage_condition" in error and "string" in error for error in errors))

    def test_wrong_types_empty_texts_and_invalid_statuses(self):
        claims, copy = documents()
        claims["claims"][0]["wording"] = ""
        claims["claims"][0]["status"] = []
        copy["units"][0]["surfaces"] = []
        copy["units"][0]["text"] = 17
        copy["units"][0]["status"] = {}
        copy["units"][0]["kind"] = []
        errors = check_claims.validate(claims, copy)
        joined = "\n".join(errors)
        self.assertIn("wording", joined)
        self.assertIn("status", joined)
        self.assertIn("surfaces", joined)
        self.assertIn("text", joined)
        self.assertIn("kind", joined)

    def test_duplicate_ids_unknown_claims_and_missing_product_reference(self):
        claims, copy = documents()
        claims["claims"].append(claim())
        copy["units"][0]["claim_ids"] = ["missing.claim"]
        errors = check_claims.validate(claims, copy)
        joined = "\n".join(errors)
        self.assertIn("duplicate claim id", joined)
        self.assertIn("unknown claim id", joined)
        self.assertIn("require at least one known claim", joined)

    def test_commit_and_source_reference_validation(self):
        claims, copy = documents(source_commit=COMMIT)
        copy["source_commit"] = "b" * 40
        claims["claims"][0]["source_refs"] = [
            {"path": "../secret.txt", "start_line": 8, "end_line": 2},
            {"path": "/absolute.txt", "start_line": 0, "end_line": 1},
        ]
        errors = check_claims.validate(claims, copy)
        joined = "\n".join(errors)
        self.assertIn("source commits must match", joined)
        self.assertIn("safe repository-relative path", joined)
        self.assertIn("positive integer line number", joined)
        self.assertIn("start_line must not exceed", joined)

    def test_require_reviewed_rejects_drafts(self):
        claims, copy = documents()
        errors = check_claims.validate(claims, copy, require_reviewed=True)
        self.assertTrue(any("require-reviewed" in error for error in errors))
        claims["claims"][0]["status"] = "reviewed"
        copy["units"][0]["status"] = "reviewed"
        self.assert_valid(claims, copy)

    def test_forbidden_marketing_patterns(self):
        forbidden = (
            "Guaranteed improvement for every repository; secure sandbox; "
            "production-ready and free to use; hard dollar or token cap; "
            "hard token limit; 5 deterministic unit tests and 3 model providers."
        )
        claims, copy = documents(claim_value=claim(wording=forbidden))
        errors = check_claims.validate(claims, copy)
        joined = "\n".join(errors)
        self.assertIn("guaranteed-improvement", joined)
        self.assertIn("secure-sandbox", joined)
        self.assertIn("production-ready", joined)
        self.assertIn("free-use", joined)
        self.assertIn("hard dollar/token cap", joined)
        self.assertIn("historical numeric", joined)

    def test_explicit_limitations_are_not_forbidden_positive_claims(self):
        disclaimers = (
            "No guaranteed improvement is claimed.",
            "Candidate execution uses host access rather than a security sandbox.",
            "There is no hard token or dollar cap claim.",
            "A secure sandbox is not provided.",
            "Hard dollar cap may be unknown.",
            "Production-ready: not claimed.",
        )
        for disclaimer in disclaimers:
            with self.subTest(disclaimer=disclaimer):
                claims, copy = documents(claim_value=claim(wording=disclaimer))
                copy["units"][0]["text"] = disclaimer
                self.assert_valid(claims, copy)

    def test_unrelated_negation_and_contrast_do_not_excuse_positive_claims(self):
        texts = (
            "We are not a hosted service. Guaranteed improvement for every program.",
            "Production-ready, but not independently tested.",
            "No hosted service is offered; production-ready deployment is available.",
            "No-cost operation is provided.",
        )
        for text in texts:
            with self.subTest(text=text):
                claims, copy = documents(claim_value=claim(wording=text))
                copy["units"][0]["text"] = text
                errors = check_claims.validate(claims, copy)
                self.assertTrue(errors, text)

    def test_numeric_counts_are_not_excused_by_unrelated_negation(self):
        text = "No guaranteed improvement is claimed. We report 5 tests and 3 providers."
        claims, copy = documents(claim_value=claim(wording=text))
        errors = check_claims.validate(claims, copy)
        self.assertTrue(any("historical numeric" in error for error in errors))

    def test_duplicate_json_keys_and_nonfinite_numbers_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"schema_version":"1.0","schema_version":"1.0"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                check_claims.load_json(path)
            path.write_text('{"number":1e999}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-finite JSON number"):
                check_claims.load_json(path)
            path.write_text("NaN", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-finite JSON number"):
                check_claims.load_json(path)

    def test_cli_default_paths_are_relative_to_script_directory(self):
        args = check_claims.build_parser().parse_args([])
        self.assertEqual(args.claims, check_claims.DEFAULT_CLAIMS_PATH)
        self.assertEqual(args.copy_path, check_claims.DEFAULT_COPY_PATH)
        self.assertEqual(args.claims.parent, Path(check_claims.__file__).resolve().parent)

    def test_cli_validates_files_without_product_imports_or_network(self):
        claims, copy = documents()
        with tempfile.TemporaryDirectory() as directory:
            claims_path = Path(directory) / "claims.json"
            copy_path = Path(directory) / "copy.json"
            claims_path.write_text(json.dumps(claims), encoding="utf-8")
            copy_path.write_text(json.dumps(copy), encoding="utf-8")
            self.assertEqual(
                check_claims.main(["--claims", str(claims_path), "--copy", str(copy_path)]),
                0,
            )


if __name__ == "__main__":
    unittest.main()
