from libreevolve.problems.benchmarks.example_scope import (
    EXAMPLE_BENCHMARK_SCOPE_SCHEMA,
    example_benchmark_scope_records,
    render_example_benchmark_scope_summary,
    validate_example_benchmark_scope,
)


def test_example_scope_records_mark_shipped_examples_as_smoke_only():
    records = example_benchmark_scope_records()

    validation = validate_example_benchmark_scope(records)

    assert validation.ok is True
    assert validation.smoke_only is True
    assert validation.comparable_problem_ids == []
    assert {record["problem_id"] for record in records} == {
        "hello_world",
        "sorting",
        "workspace_math",
        "embedded_evaluate_math",
        "matrix_multiplication",
        "circle_packing",
    }
    assert {record["level"] for record in records} == {"smoke"}
    assert all(record["alphaevolve_comparable"] is False for record in records)


def test_example_scope_rejects_smoke_record_marked_alphaevolve_comparable():
    records = example_benchmark_scope_records()
    records[0]["alphaevolve_comparable"] = True

    validation = validate_example_benchmark_scope(records)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "smoke_marked_comparable" in codes


def test_example_scope_rejects_duplicate_problem_and_unsafe_path():
    records = example_benchmark_scope_records()
    records[1]["problem_id"] = records[0]["problem_id"]
    records[1]["path"] = "../outside"
    records[1]["required_upgrades"] = []

    validation = validate_example_benchmark_scope(records)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "duplicate_problem_id" in codes
    assert "invalid_path" in codes
    assert "invalid_required_upgrades" in codes


def test_example_scope_requires_paper_claims_to_be_comparable():
    records = [
        {
            "schema": EXAMPLE_BENCHMARK_SCOPE_SCHEMA,
            "problem_id": "paper_target",
            "path": "libreevolve/problems/benchmarks/paper_target",
            "level": "paper_claim",
            "alphaevolve_comparable": False,
            "current_role": "paper benchmark",
            "reason": "A paper-level target must not be scoped as non-comparable.",
            "required_upgrades": ["Mark comparable only after the full evidence contract is present."],
        }
    ]

    validation = validate_example_benchmark_scope(records)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "paper_claim_not_comparable" in codes


def test_example_scope_summary_renders_scope_table():
    summary = render_example_benchmark_scope_summary(example_benchmark_scope_records())

    assert "Example benchmark scope" in summary
    assert "| schema_status | ok |" in summary
    assert "| smoke_only | yes |" in summary
    assert "| comparable_problem_count | 0 |" in summary
    assert "| embedded_evaluate_math | smoke | no | embedded_entrypoint_fixture |" in summary
    assert "| matrix_multiplication | smoke | no | operation_counter_smoke_fixture |" in summary
