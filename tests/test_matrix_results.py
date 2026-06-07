import hashlib
import json

from libreevolve.problems.benchmarks.matrix_results import (
    MATRIX_ARTIFACT_INVENTORY_SCHEMA,
    MATRIX_RESULT_SCHEMA,
    matrix_result_artifact_inventory,
    render_matrix_result_summary,
    validate_matrix_result_report,
)


def _valid_report() -> dict:
    return {
        "schema": MATRIX_RESULT_SCHEMA,
        "target_suite": "alphaevolve_appendix_a",
        "target_id": "mm_4x4x4",
        "dimensions": [4, 4, 4],
        "seed_count": 4,
        "best_rank": 47,
        "hit_count": 2,
        "hit_fraction": 0.5,
        "coefficient_domain": "half_integer",
        "alphaevolve_comparable": True,
        "exactness_certificate": {
            "status": "verified",
            "method": "symbolic_tensor_identity",
            "certificate_sha256": "a" * 64,
        },
        "seed_results": [
            {"seed": 100, "rank": 47, "achieved_best_rank": True, "exact": True},
            {"seed": 101, "rank": 49, "achieved_best_rank": False, "exact": True},
            {"seed": 102, "rank": 47, "achieved_best_rank": True, "exact": True},
            {"seed": 103, "rank": 50, "achieved_best_rank": False, "exact": True},
        ],
        "artifacts": [
            {
                "kind": "algorithm",
                "path": "matrix/mm_4x4x4/algorithm.json",
                "sha256": "b" * 64,
                "bytes": 4096,
            },
            {
                "kind": "certificate",
                "path": "matrix/mm_4x4x4/certificate.json",
                "sha256": "a" * 64,
                "bytes": 2048,
            },
            {
                "kind": "notebook",
                "path": "matrix/mm_4x4x4/reproduce.ipynb",
                "sha256": "c" * 64,
                "bytes": 8192,
            },
        ],
    }


def test_matrix_result_report_validates_alphaevolve_publication_contract():
    report = _valid_report()

    validation = validate_matrix_result_report(report)

    assert validation.ok is True
    assert validation.alphaevolve_comparable is True
    assert validation.target_id == "mm_4x4x4"
    assert validation.seed_count == 4
    assert validation.best_rank == 47
    assert validation.hit_fraction == 0.5
    assert validation.issues == []


def test_matrix_result_report_loads_json_file(tmp_path):
    path = tmp_path / "matrix_report.json"
    path.write_text(json.dumps(_valid_report()), encoding="utf-8")

    validation = validate_matrix_result_report(path)

    assert validation.ok is True
    assert validation.target_id == "mm_4x4x4"


def test_matrix_result_artifact_inventory_verifies_declared_files(tmp_path):
    report = _valid_report()
    for artifact in report["artifacts"]:
        path = tmp_path / artifact["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        content = f"{artifact['kind']} artifact".encode("utf-8")
        path.write_bytes(content)
        artifact["sha256"] = hashlib.sha256(content).hexdigest()
        artifact["bytes"] = len(content)

    inventory = matrix_result_artifact_inventory(report, tmp_path)

    assert inventory["schema"] == MATRIX_ARTIFACT_INVENTORY_SCHEMA
    assert inventory["target_id"] == "mm_4x4x4"
    assert inventory["artifact_root_policy"] == (
        "safe_relative_report_paths_under_artifact_root"
    )
    assert inventory["ok"] is True
    assert inventory["artifact_count"] == 3
    assert inventory["verified_count"] == 3
    assert inventory["missing_count"] == 0
    assert inventory["mismatch_count"] == 0
    assert inventory["invalid_count"] == 0
    assert len(inventory["records_sha256"]) == 64
    assert {artifact["status"] for artifact in inventory["artifacts"]} == {
        "verified"
    }
    assert all("actual_sha256" in artifact for artifact in inventory["artifacts"])


def test_matrix_result_artifact_inventory_reports_missing_mismatch_and_unsafe_paths(tmp_path):
    report = _valid_report()
    first = report["artifacts"][0]
    first_path = tmp_path / first["path"]
    first_path.parent.mkdir(parents=True, exist_ok=True)
    first_path.write_text("wrong", encoding="utf-8")
    first["sha256"] = "b" * 64
    first["bytes"] = 999
    report["artifacts"][1]["path"] = "missing/certificate.json"
    report["artifacts"][2]["path"] = "../escape.ipynb"

    inventory = matrix_result_artifact_inventory(report, tmp_path)
    records = {artifact["kind"]: artifact for artifact in inventory["artifacts"]}

    assert inventory["ok"] is False
    assert inventory["mismatch_count"] == 1
    assert inventory["missing_count"] == 1
    assert inventory["invalid_count"] == 1
    assert records["algorithm"]["status"] == "hash_mismatch"
    assert "artifact_hash_mismatch" in records["algorithm"]["issues"]
    assert "artifact_bytes_mismatch" in records["algorithm"]["issues"]
    assert records["certificate"]["status"] == "missing_file"
    assert records["notebook"]["status"] == "unsafe_path"


def test_matrix_result_report_allows_exploratory_non_publication_domains():
    report = _valid_report()
    report["alphaevolve_comparable"] = False
    report["coefficient_domain"] = "rational"
    report["artifacts"] = [artifact for artifact in report["artifacts"] if artifact["kind"] != "notebook"]

    validation = validate_matrix_result_report(report)

    assert validation.ok is True
    assert validation.alphaevolve_comparable is False


def test_matrix_result_report_rejects_non_publication_domain_for_alphaevolve_claim():
    report = _valid_report()
    report["coefficient_domain"] = "float"
    report["exactness_certificate"]["status"] = "not_checked"
    report["seed_results"][0]["exact"] = False
    report["artifacts"] = [artifact for artifact in report["artifacts"] if artifact["kind"] != "notebook"]

    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_comparable is True
    assert "non_publication_coefficient_domain" in codes
    assert "paper_claim_exactness_not_verified" in codes
    assert "paper_claim_seed_not_exact" in codes
    assert "missing_publication_artifact" in codes


def test_matrix_result_report_requires_explicit_alphaevolve_comparable_flag():
    report = _valid_report()
    del report["alphaevolve_comparable"]

    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.alphaevolve_comparable is False
    assert "invalid_alphaevolve_comparable" in codes


def test_matrix_result_report_validates_known_appendix_a_target_dimensions():
    report = _valid_report()
    report["dimensions"] = [4, 4, 5]

    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "target_dimensions_mismatch" in codes

    report = _valid_report()
    report["target_id"] = "mm_missing"
    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "unknown_target_id" in codes


def test_matrix_result_report_rejects_inconsistent_hit_fraction_and_seed_hits():
    report = _valid_report()
    report["hit_fraction"] = 0.75
    report["seed_results"][1]["achieved_best_rank"] = True
    report["seed_results"][1]["rank"] = 49

    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_hit_fraction" in codes
    assert "inconsistent_seed_rank" in codes
    assert "invalid_seed_hit_count" in codes


def test_matrix_result_report_rejects_best_rank_inconsistent_with_seed_ranks():
    report = _valid_report()
    report["best_rank"] = 48
    report["hit_count"] = 1
    report["hit_fraction"] = 0.25
    report["seed_results"][0]["rank"] = 47
    report["seed_results"][0]["achieved_best_rank"] = False
    report["seed_results"][2]["rank"] = 48
    report["seed_results"][2]["achieved_best_rank"] = True

    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "inconsistent_best_rank" in codes


def test_matrix_result_report_rejects_best_rank_seed_without_hit_flag():
    report = _valid_report()
    report["hit_count"] = 1
    report["hit_fraction"] = 0.25
    report["seed_results"][2]["achieved_best_rank"] = False

    validation = validate_matrix_result_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "inconsistent_seed_hit_flag" in codes


def test_matrix_result_report_requires_safe_hashed_artifacts_and_verified_certificate():
    report = _valid_report()
    report["exactness_certificate"]["certificate_sha256"] = "not-a-hash"
    report["artifacts"] = [
        {
            "kind": "algorithm",
            "path": "C:/secret.json",
            "sha256": "not-a-hash",
            "bytes": 0,
        }
    ]

    validation = validate_matrix_result_report(report)
    codes = [issue.code for issue in validation.issues]

    assert validation.ok is False
    assert "invalid_certificate_hash" in codes
    assert "invalid_artifact_path" in codes
    assert "invalid_artifact_hash" in codes
    assert "invalid_artifact_bytes" in codes

    report["artifacts"][0]["path"] = "../secret.json"
    validation = validate_matrix_result_report(report)
    codes = [issue.code for issue in validation.issues]

    assert "invalid_artifact_path" in codes


def test_matrix_result_summary_renders_key_publication_fields():
    summary = render_matrix_result_summary(_valid_report())

    assert "Matrix result report: mm_4x4x4" in summary
    assert "| best_rank | 47 |" in summary
    assert "| seed_count | 4 |" in summary
    assert "| hit_fraction | 0.500 |" in summary
    assert "| coefficient_domain | half_integer |" in summary
    assert "| alphaevolve_comparable | True |" in summary
    assert "| exactness | verified |" in summary
    assert "| artifact_count | 3 |" in summary
