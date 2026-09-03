import re
from pathlib import Path

import yaml

from libreevolve.core.config import Config
from libreevolve.problems.benchmarks.candidate_language_runner_boundary import (
    CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_SCHEMA,
    candidate_language_runner_boundary_record,
    render_candidate_language_runner_boundary_summary,
    validate_candidate_language_runner_boundary,
)


OCI_FIXTURE_CONFIG = (
    Path(__file__).parents[1]
    / "libreevolve"
    / "problems"
    / "examples"
    / "candidate_runner_python_oci"
    / "config.yaml"
)


def test_candidate_language_runner_boundary_accepts_partial_record():
    boundary = candidate_language_runner_boundary_record()

    validation = validate_candidate_language_runner_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "digest_pinned_oci_candidate_execution_partial"
    )
    assert validation.required_evidence_field_count == 28
    assert validation.missing_evidence_count == 10
    assert boundary["schema"] == CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_SCHEMA
    assert "does not claim AlphaEvolve-style arbitrary language" in (
        boundary["claim_boundary"]
    )


def test_candidate_language_runner_boundary_rejects_premature_runner_claim():
    boundary = candidate_language_runner_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "arbitrary_language_runner_evidence_recorded"
    boundary["missing_evidence"]["configured_non_python_language_runners"] = "recorded"
    boundary["required_evidence_fields"] = ["candidate_language"]

    validation = validate_candidate_language_runner_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_configured_non_python_language_runners" in codes
    assert "missing_required_evidence_field" in codes


def test_candidate_language_runner_boundary_rejects_non_string_evidence_key_without_raising():
    boundary = candidate_language_runner_boundary_record()
    boundary["missing_evidence"][17] = "invalid-key-fixture"

    validation = validate_candidate_language_runner_boundary(boundary)

    assert validation.ok is False
    assert "invalid_missing_evidence_key" in {
        issue.code for issue in validation.issues
    }


def test_render_candidate_language_runner_boundary_summary_reports_shape():
    summary = render_candidate_language_runner_boundary_summary(
        candidate_language_runner_boundary_record()
    )

    assert "AlphaEvolve candidate language runner boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | digest_pinned_oci_candidate_execution_partial |"
        in summary
    )
    assert "| required_evidence_field_count | 28 |" in summary
    assert "| missing_evidence_count | 10 |" in summary


def test_candidate_runner_python_oci_fixture_declares_complete_bounded_contract():
    raw_config = yaml.safe_load(OCI_FIXTURE_CONFIG.read_text(encoding="utf-8"))
    config = Config(**raw_config)

    language = config.candidate_language_runners[0]
    build = config.candidate_build_systems[0]
    environment = build["execution_environment"]

    assert language == {
        "language": "python_oci",
        "candidate_role": "task_primary_text",
        "file_patterns": ["solution.py"],
        "marker_grammar": "whole_file_text_v1",
        "runner_command": ["python", "{primary}"],
        "execution_status": "executable_local_subprocess",
        "notes": "Runs the candidate in the build system's digest-pinned OCI image.",
    }
    assert build["name"] == "python_bytecode_oci"
    assert build["build_files"] == ["solution.py", "toolchain.lock"]
    assert build["build_command"] == [
        "{toolchain}",
        "-m",
        "py_compile",
        "solution.py",
    ]
    assert build["artifact_patterns"] == ["__pycache__/*.pyc"]
    assert build["toolchain_candidates"] == ["python"]
    assert build["toolchain_version_command"] == ["{toolchain}", "--version"]
    assert build["execution_status"] == "executable_local_subprocess"
    assert environment["runtime_candidates"] == ["docker", "podman"]
    assert environment["pull_policy"] == "if_missing"
    assert environment["network"] == "none"
    assert environment["read_only_rootfs"] is True
    assert environment["tmpfs_mb"] == 64
    assert environment["memory_mb"] == 256
    assert environment["cpus"] == 1.0
    assert environment["pids_limit"] == 64
    assert re.fullmatch(
        r"docker\.io/library/python@sha256:[0-9a-f]{64}",
        environment["image"],
    )
    assert config.eval_stages == [
        {
            "name": "run_python_oci",
            "role": "main_test",
            "mode": "candidate_runner",
            "language_runner": "python_oci",
            "build_system": "python_bytecode_oci",
            "timeout_sec": 60,
        }
    ]
