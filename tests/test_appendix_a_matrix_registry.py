import json

import pytest

from libreevolve.problems.benchmarks.appendix_a_matrix_registry import (
    BASELINE_CITATION_BOUNDARY_SCHEMA,
    CURATION_SCHEMA,
    EXCLUDED_TARGET_CURATION_BOUNDARY_SCHEMA,
    EXPECTED_TARGET_COUNT,
    LOCAL_RESOURCE_FRONTIER_SCHEMA,
    ROW_NOTE_ARTIFACT_BOUNDARY_SCHEMA,
    RESOURCE_FRONTIER_SCHEMA,
    ROW_NOTE_SCHEMA,
    SUBSET_SCOPE_ARTIFACT_BOUNDARY_SCHEMA,
    SUBSET_SCOPE_SCHEMA,
    TARGET_SUITE,
    appendix_a_matrix_baseline_citation_boundary_from_citations,
    appendix_a_matrix_baseline_citation_boundary_record,
    appendix_a_matrix_curation_record,
    appendix_a_matrix_excluded_target_curation_boundary_record,
    appendix_a_matrix_local_resource_frontier_record,
    appendix_a_matrix_resource_frontier_record,
    appendix_a_matrix_row_note_artifact_boundary_from_records,
    appendix_a_matrix_row_note_artifact_boundary_record,
    appendix_a_matrix_row_note_records,
    appendix_a_matrix_subset_scope_artifact_boundary_record,
    appendix_a_matrix_subset_scope_record,
    matrix_target_by_id,
    matrix_target_records,
    render_appendix_a_matrix_baseline_citation_boundary_summary,
    render_appendix_a_matrix_curation_summary,
    render_appendix_a_matrix_excluded_target_curation_boundary_summary,
    render_appendix_a_matrix_local_resource_frontier_summary,
    render_appendix_a_matrix_resource_frontier_summary,
    render_appendix_a_matrix_registry_summary,
    render_appendix_a_matrix_row_note_artifact_boundary_summary,
    render_appendix_a_matrix_row_note_summary,
    render_appendix_a_matrix_subset_scope_artifact_boundary_summary,
    render_appendix_a_matrix_subset_scope_summary,
    validate_appendix_a_matrix_baseline_citation_boundary,
    validate_appendix_a_matrix_curation,
    validate_appendix_a_matrix_excluded_target_curation_boundary,
    validate_appendix_a_matrix_local_resource_frontier,
    validate_appendix_a_matrix_resource_frontier,
    validate_appendix_a_matrix_registry,
    validate_appendix_a_matrix_row_note_artifact_boundary,
    validate_appendix_a_matrix_row_notes,
    validate_appendix_a_matrix_subset_scope_artifact_boundary,
    validate_appendix_a_matrix_subset_scope,
)


def test_appendix_a_matrix_registry_validates_table3_targets():
    report = validate_appendix_a_matrix_registry()

    assert report.ok is True
    assert report.target_count == EXPECTED_TARGET_COUNT == 54
    assert report.matched_count == 38
    assert report.surpassed_count == 14
    assert report.fell_behind_count == 2
    assert report.issues == []


def test_appendix_a_matrix_registry_exposes_target_lookup():
    target = matrix_target_by_id("mm_4x4x4")

    assert target == {
        "id": "mm_4x4x4",
        "dimensions": [4, 4, 4],
        "best_known_rank": 49,
        "alphaevolve_rank": 48,
        "outcome": "surpassed",
        "exact_algorithm": True,
    }
    assert matrix_target_by_id("mm_missing") is None
    assert len(matrix_target_records()) == 54


def test_appendix_a_matrix_registry_rejects_malformed_targets(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": TARGET_SUITE,
                "targets": [
                    {
                        "id": "mm_4x4x4",
                        "dimensions": [4, 4, 4],
                        "best_known_rank": 49,
                        "alphaevolve_rank": 49,
                        "outcome": "surpassed",
                        "exact_algorithm": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    report = validate_appendix_a_matrix_registry(path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_target_count" in codes
    assert "invalid_surpassed_rank" in codes
    assert "missing_exact_algorithm" in codes
    assert "invalid_outcome_counts" in codes


def test_appendix_a_matrix_registry_summary_renders_counts():
    summary = render_appendix_a_matrix_registry_summary()

    assert "AlphaEvolve Appendix A matrix target registry" in summary
    assert "| target_count | 54 |" in summary
    assert "| matched | 38 |" in summary
    assert "| surpassed | 14 |" in summary
    assert "| fell_behind | 2 |" in summary


def test_appendix_a_matrix_curation_validates_selection_and_symmetry_policy():
    record = appendix_a_matrix_curation_record()
    report = validate_appendix_a_matrix_curation(record)

    assert report.ok is True
    assert record["schema"] == CURATION_SCHEMA
    assert report.included_target_count == EXPECTED_TARGET_COUNT == 54
    assert report.outside_rough_rule_count == 1
    assert report.omitted_equivalent_count == 155
    assert report.issues == []
    assert record["selection_policy"]["p_cutoff_policy"] == "reasonable_cutoff_not_numerically_specified_in_paper"
    assert record["symmetry_policy"]["canonical_order"] == "m <= n <= p"


def test_appendix_a_matrix_curation_rejects_policy_drift():
    record = appendix_a_matrix_curation_record()
    record["selection_policy"]["rough_m_max"] = 6
    record["symmetry_policy"]["canonical_order"] = "as_reported"
    record["source_pdf_page"] = 33

    report = validate_appendix_a_matrix_curation(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_selection_rough_m_max" in codes
    assert "invalid_canonical_order" in codes
    assert "invalid_source_pdf_page" in codes


def test_appendix_a_matrix_curation_rejects_missing_target_and_omission():
    record = appendix_a_matrix_curation_record()
    record["included_targets"] = record["included_targets"][:-1]
    record["omitted_equivalent_targets"] = record["omitted_equivalent_targets"][:-1]

    report = validate_appendix_a_matrix_curation(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "missing_included_target" in codes
    assert "missing_omitted_equivalent_target" in codes


def test_appendix_a_matrix_curation_rejects_bad_inclusion_record():
    record = appendix_a_matrix_curation_record()
    record["included_targets"][0]["selection_bucket"] = "reported_outside_rough_rule"
    record["included_targets"][0]["canonical_representative"] = False
    record["included_targets"][0]["dimensions"] = [2, 2, 3]

    report = validate_appendix_a_matrix_curation(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_selection_bucket" in codes
    assert "missing_canonical_representative" in codes
    assert "included_target_dimension_mismatch" in codes


def test_appendix_a_matrix_curation_summary_renders_counts():
    summary = render_appendix_a_matrix_curation_summary()

    assert "AlphaEvolve Appendix A matrix target-suite curation" in summary
    assert "| included_target_count | 54 |" in summary
    assert "| omitted_equivalent_count | 155 |" in summary
    assert "| outside_rough_rule_count | 1 |" in summary


def _excluded_target() -> dict:
    return {
        "excluded_target_id": "mm_6x6x7",
        "dimensions": [6, 6, 7],
        "canonical_order": "m <= n <= p",
        "exclusion_class": "outside_rough_mn_rule",
        "exclusion_reason": "outside the paper's rough 2 <= m,n <= 5 reported-size rule",
        "source_basis": "Appendix A rough target-suite selection statement",
        "source_pdf_page": 34,
        "rough_rule_relation": "m and n exceed the rough reported range",
        "p_cutoff_relation": "not selected under the paper's unspecified reasonable p cutoff",
        "symmetry_equivalence_status": "non_equivalent_to_reported_sorted_representatives",
        "local_attempt_ref": "not_attempted_locally",
        "resource_frontier_ref": "appendix_a_resource_frontier:paper_beyond_5x5x5_single_gpu_1000_seeds",
        "artifact_paths": ["matrix/curation/excluded/mm_6x6x7.json"],
        "artifact_sha256": "d" * 64,
    }


def test_appendix_a_matrix_excluded_target_curation_boundary_accepts_current_absence():
    report = validate_appendix_a_matrix_excluded_target_curation_boundary()

    assert report.ok is True
    assert report.curation_status == "not_recorded_locally"
    assert report.excluded_target_count == 0
    assert report.required_field_count == 14
    assert report.issues == []


def test_appendix_a_matrix_excluded_target_curation_boundary_rejects_absence_with_records():
    boundary = appendix_a_matrix_excluded_target_curation_boundary_record()
    boundary["excluded_non_equivalent_targets"] = [_excluded_target()]
    boundary["claim_boundary"] = "Excluded targets are justified."

    report = validate_appendix_a_matrix_excluded_target_curation_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "unexpected_excluded_targets" in codes
    assert "missing_claim_boundary" in codes


def test_appendix_a_matrix_excluded_target_curation_boundary_requires_records_when_recorded():
    boundary = appendix_a_matrix_excluded_target_curation_boundary_record()
    boundary["curation_status"] = "recorded"
    boundary["coverage_policy"] = {
        "status": "partial_with_scope",
        "scope": "matrix sizes m,n,p <= 7 outside the reported table",
    }

    report = validate_appendix_a_matrix_excluded_target_curation_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "missing_excluded_targets" in codes


def test_appendix_a_matrix_excluded_target_curation_boundary_accepts_recorded_rows():
    boundary = {
        "schema": EXCLUDED_TARGET_CURATION_BOUNDARY_SCHEMA,
        "curation_schema": CURATION_SCHEMA,
        "source_paper_id": "2506.13131",
        "source_section": "AlphaEvolve Appendix A",
        "source_pdf_page": 34,
        "target_suite": TARGET_SUITE,
        "curation_status": "recorded",
        "required_excluded_target_fields": list(appendix_a_matrix_excluded_target_curation_boundary_record()["required_excluded_target_fields"]),
        "excluded_non_equivalent_targets": [_excluded_target()],
        "coverage_policy": {
            "status": "partial_with_scope",
            "scope": "fixture coverage for one non-equivalent target outside the reported table",
        },
        "claim_boundary": "Local metadata records excluded target justifications for the declared scope.",
    }

    report = validate_appendix_a_matrix_excluded_target_curation_boundary(boundary)

    assert report.ok is True
    assert report.curation_status == "recorded"
    assert report.excluded_target_count == 1
    assert report.issues == []


def test_appendix_a_matrix_excluded_target_curation_boundary_rejects_invalid_rows():
    boundary = appendix_a_matrix_excluded_target_curation_boundary_record()
    boundary["curation_status"] = "recorded"
    boundary["coverage_policy"] = {
        "status": "partial_with_scope",
        "scope": "invalid fixture coverage",
    }
    target = _excluded_target()
    target["excluded_target_id"] = "mm_2x4x5"
    target["dimensions"] = [5, 4, 2]
    target["exclusion_class"] = "unknown"
    target["symmetry_equivalence_status"] = "axis_permutation_equivalent"
    target["artifact_paths"] = ["../escape.json"]
    target["artifact_sha256"] = "not-a-digest"
    boundary["excluded_non_equivalent_targets"] = [target]

    report = validate_appendix_a_matrix_excluded_target_curation_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "excluded_target_in_registry" in codes
    assert "excluded_target_id_dimension_mismatch" in codes
    assert "excluded_target_not_canonical" in codes
    assert "invalid_exclusion_class" in codes
    assert "invalid_symmetry_equivalence_status" in codes
    assert "invalid_excluded_target_artifact_path" in codes
    assert "invalid_excluded_target_artifact_sha256" in codes


def test_appendix_a_matrix_excluded_target_curation_boundary_rejects_symmetry_equivalent_rows():
    boundary = appendix_a_matrix_excluded_target_curation_boundary_record()
    boundary["curation_status"] = "recorded"
    boundary["coverage_policy"] = {
        "status": "partial_with_scope",
        "scope": "invalid symmetry fixture coverage",
    }
    target = _excluded_target()
    target["excluded_target_id"] = "mm_4x2x5"
    target["dimensions"] = [4, 2, 5]
    boundary["excluded_non_equivalent_targets"] = [target]

    report = validate_appendix_a_matrix_excluded_target_curation_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "excluded_target_is_symmetry_equivalent" in codes


def test_appendix_a_matrix_excluded_target_curation_boundary_summary_renders_counts():
    summary = render_appendix_a_matrix_excluded_target_curation_boundary_summary()

    assert "AlphaEvolve Appendix A matrix excluded-target curation boundary" in summary
    assert "| curation_status | not_recorded_locally |" in summary
    assert "| excluded_target_count | 0 |" in summary


def test_appendix_a_matrix_baseline_citation_boundary_accepts_current_absence():
    report = validate_appendix_a_matrix_baseline_citation_boundary()

    assert report.ok is True
    assert report.citation_status == "not_recorded_locally"
    assert report.citation_count == 0
    assert report.required_field_count == 11
    assert report.issues == []


def test_appendix_a_matrix_baseline_citation_boundary_rejects_absence_with_citations():
    boundary = appendix_a_matrix_baseline_citation_boundary_record()
    boundary["baseline_citations"] = [_baseline_citation(matrix_target_records()[0])]
    boundary["claim_boundary"] = "Citations exist."

    report = validate_appendix_a_matrix_baseline_citation_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "unexpected_baseline_citations" in codes
    assert "missing_claim_boundary" in codes


def test_appendix_a_matrix_baseline_citation_boundary_requires_all_targets_when_recorded():
    boundary = appendix_a_matrix_baseline_citation_boundary_record()
    boundary["citation_status"] = "recorded"

    report = validate_appendix_a_matrix_baseline_citation_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "missing_baseline_citations" in codes


def test_appendix_a_matrix_baseline_citation_boundary_accepts_recorded_rows():
    citations = [_baseline_citation(target) for target in matrix_target_records()]
    boundary = appendix_a_matrix_baseline_citation_boundary_from_citations(citations)

    report = validate_appendix_a_matrix_baseline_citation_boundary(boundary)

    assert boundary["schema"] == BASELINE_CITATION_BOUNDARY_SCHEMA
    assert boundary["target_suite"] == TARGET_SUITE
    assert report.ok is True
    assert report.citation_status == "recorded"
    assert report.citation_count == EXPECTED_TARGET_COUNT
    assert report.issues == []
    assert boundary["baseline_citations"][0]["target_id"] == matrix_target_records()[0]["id"]
    assert (
        boundary["baseline_citations"][0]["report_baseline_source_ref"]
        == f"baseline:{matrix_target_records()[0]['id']}:ref95"
    )


def test_appendix_a_matrix_baseline_citation_boundary_rejects_invalid_citation_fields():
    target = matrix_target_records()[0]
    boundary = appendix_a_matrix_baseline_citation_boundary_record()
    boundary["citation_status"] = "recorded"
    citation = _baseline_citation(target)
    citation["dimensions"] = [9, 9, 9]
    citation["best_known_rank"] = -1
    citation["cited_reference_id"] = "999"
    citation["source_artifact_path"] = "../escape.json"
    citation["source_artifact_sha256"] = "not-a-digest"
    citation["applicability_caveats"] = ""
    boundary["baseline_citations"] = [citation]

    report = validate_appendix_a_matrix_baseline_citation_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_baseline_dimensions" in codes
    assert "invalid_baseline_rank" in codes
    assert "invalid_cited_reference_id" in codes
    assert "invalid_source_artifact_path" in codes
    assert "invalid_source_artifact_sha256" in codes
    assert "missing_applicability_caveats" in codes


def test_appendix_a_matrix_baseline_citation_boundary_rejects_source_ref_mismatch():
    target = matrix_target_records()[0]
    boundary = appendix_a_matrix_baseline_citation_boundary_record()
    boundary["citation_status"] = "recorded"
    citation = _baseline_citation(target)
    citation["report_baseline_source_ref"] = "baseline:wrong-target:ref94"
    boundary["baseline_citations"] = [
        citation,
        *[_baseline_citation(row) for row in matrix_target_records()[1:]],
    ]

    report = validate_appendix_a_matrix_baseline_citation_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_report_baseline_source_ref" in codes


def test_appendix_a_matrix_baseline_citation_boundary_summary_renders_counts():
    summary = render_appendix_a_matrix_baseline_citation_boundary_summary()

    assert "AlphaEvolve Appendix A matrix baseline-citation boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| citation_status | not_recorded_locally |" in summary
    assert "| citation_count | 0 |" in summary


def test_appendix_a_matrix_resource_frontier_validates_paper_oom_boundary():
    record = appendix_a_matrix_resource_frontier_record()
    report = validate_appendix_a_matrix_resource_frontier(record)

    assert report.ok is True
    assert record["schema"] == RESOURCE_FRONTIER_SCHEMA
    assert report.attempted_scope_count == 1
    assert report.local_artifact_count == 0
    assert report.issues == []
    observation = record["frontier_observations"][0]
    assert observation["target_scope"] == "sizes_beyond_5x5x5"
    assert observation["seed_count"] == 1000
    assert observation["accelerator_profile"] == "single_gpu_accelerator"
    assert observation["resource_status"] == "often_out_of_memory"
    assert observation["local_execution_evidence"] is False


def test_appendix_a_matrix_resource_frontier_rejects_overclaimed_local_artifacts():
    record = appendix_a_matrix_resource_frontier_record()
    observation = record["frontier_observations"][0]
    observation["local_execution_evidence"] = True
    observation["local_artifacts"] = [{"path": "runs/matrix_oom.json"}]

    report = validate_appendix_a_matrix_resource_frontier(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert report.local_artifact_count == 1
    assert "local_execution_overclaim" in codes
    assert "unexpected_local_artifacts" in codes


def test_appendix_a_matrix_resource_frontier_rejects_source_drift():
    record = appendix_a_matrix_resource_frontier_record()
    record["source_pdf_page"] = 35
    observation = record["frontier_observations"][0]
    observation["seed_count"] = 100
    observation["source_phrase"] = "larger sizes were expensive"

    report = validate_appendix_a_matrix_resource_frontier(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_source_pdf_page" in codes
    assert "invalid_seed_count" in codes
    assert "missing_source_phrase" in codes


def test_appendix_a_matrix_resource_frontier_summary_renders_counts():
    summary = render_appendix_a_matrix_resource_frontier_summary()

    assert "AlphaEvolve Appendix A matrix resource frontier" in summary
    assert "| attempted_scope_count | 1 |" in summary
    assert "| local_artifact_count | 0 |" in summary


def test_appendix_a_matrix_local_resource_frontier_validates_absence_boundary():
    record = appendix_a_matrix_local_resource_frontier_record()

    report = validate_appendix_a_matrix_local_resource_frontier(record)

    assert report.ok is True
    assert record["schema"] == LOCAL_RESOURCE_FRONTIER_SCHEMA
    assert record["local_frontier_status"] == "not_executed_locally"
    assert report.attempted_scope_count == 0
    assert report.local_artifact_count == 0
    assert "gpu_memory_bytes" in record["required_attempt_fields"]
    assert "oom_or_exhaustion_diagnostics" in record["required_attempt_fields"]
    assert report.issues == []


def test_appendix_a_matrix_local_resource_frontier_rejects_attempts_under_absence_boundary():
    record = appendix_a_matrix_local_resource_frontier_record()
    record["local_attempts"] = [
        {
            "attempt_id": "larger_mm_probe",
            "target_id": "mm_6x6x6",
            "dimensions": [6, 6, 6],
            "seed_count": 10,
            "accelerator_profile": "local_cpu_only",
            "gpu_memory_bytes": 0,
            "resource_status": "resource_exhausted",
            "oom_or_exhaustion_diagnostics": "fixture diagnostic",
            "artifact_paths": ["runs/matrix/frontier.json"],
            "artifact_sha256": ["0" * 64],
        }
    ]

    report = validate_appendix_a_matrix_local_resource_frontier(record)

    assert report.ok is False
    assert "unexpected_local_attempts" in {issue.code for issue in report.issues}


def test_appendix_a_matrix_local_resource_frontier_rejects_invalid_recorded_attempts():
    record = appendix_a_matrix_local_resource_frontier_record()
    record["local_frontier_status"] = "attempts_recorded"
    record["local_attempts"] = [
        {
            "attempt_id": "larger_mm_probe",
            "target_id": "not-a-target",
            "dimensions": [6, 6],
            "seed_count": 0,
            "accelerator_profile": "",
            "gpu_memory_bytes": -1,
            "resource_status": "unknown",
            "oom_or_exhaustion_diagnostics": "",
            "artifact_paths": ["tmp/frontier.json"],
            "artifact_sha256": ["not-a-digest"],
        }
    ]
    record["excluded_target_policy"] = {
        "status": "defined",
        "boundary": "No local larger-target matrix scaling attempts are complete.",
    }

    report = validate_appendix_a_matrix_local_resource_frontier(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_local_target_id" in codes
    assert "invalid_local_dimensions" in codes
    assert "invalid_local_seed_count" in codes
    assert "missing_local_accelerator_profile" in codes
    assert "invalid_local_gpu_memory_bytes" in codes
    assert "invalid_local_resource_status" in codes
    assert "missing_local_oom_diagnostics" in codes
    assert "invalid_local_artifact_paths" in codes
    assert "invalid_local_artifact_hashes" in codes


def test_appendix_a_matrix_local_resource_frontier_summary_renders_absence_counts():
    summary = render_appendix_a_matrix_local_resource_frontier_summary()

    assert "AlphaEvolve Appendix A local matrix resource frontier" in summary
    assert "| local_frontier_status | not_executed_locally |" in summary
    assert "| attempted_scope_count | 0 |" in summary
    assert "| local_artifact_count | 0 |" in summary


def _subset_by_id(record: dict, subset_id: str) -> dict:
    return next(subset for subset in record["subsets"] if subset["subset_id"] == subset_id)


def _subset_scope_artifact(subset_id: str = "main_text_mnp_le_5") -> dict:
    evidence = appendix_a_matrix_subset_scope_record()
    subset = _subset_by_id(evidence, subset_id)
    return {
        "subset_scope_id": subset_id,
        "source_table": subset["source_table"],
        "source_pdf_page": subset["source_pdf_page"],
        "source_phrase": subset["source_phrase"],
        "inclusion_predicate": subset["inclusion_predicate"],
        "row_count": subset["row_count"],
        "outcome_counts": dict(subset["outcome_counts"]),
        "out_of_scope_target_ids": list(subset["out_of_scope_target_ids"]),
        "fell_behind_target_ids": list(subset["fell_behind_target_ids"]),
        "subset_scope_evidence": evidence,
        "artifact_paths": [f"tables/{subset_id}_subset_scope.json"],
        "artifact_sha256": "a" * 64,
    }


def _row_note_artifact() -> dict:
    evidence = appendix_a_matrix_row_note_records()
    note = evidence["row_notes"][0]
    return {
        "note_id": note["note_id"],
        "note_type": note["note_type"],
        "target_id": note["target_id"],
        "dimensions": list(note["dimensions"]),
        "alphaevolve_rank": note["alphaevolve_rank"],
        "concurrent_rank": note["concurrent_rank"],
        "cited_reference_id": note["cited_reference_id"],
        "relationship_to_alphaevolve": note["relationship_to_alphaevolve"],
        "source_table": note["source_table"],
        "source_pdf_page": note["source_pdf_page"],
        "note_text": note["note_text"],
        "exclusive_priority_claim_safe": note["exclusive_priority_claim_safe"],
        "docs_caveat": note["docs_caveat"],
        "row_note_evidence": evidence,
        "artifact_paths": ["tables/mm_4x5x6_row_note.json"],
        "artifact_sha256": "b" * 64,
    }


def _baseline_citation(target: dict) -> dict:
    return {
        "target_id": target["id"],
        "dimensions": list(target["dimensions"]),
        "best_known_rank": target["best_known_rank"],
        "cited_reference_id": "95",
        "source_table": "Appendix A Table 3",
        "source_pdf_page": 34,
        "source_artifact_path": f"papers/alphaevolve/baselines/{target['id']}.json",
        "source_artifact_sha256": "c" * 64,
        "applicability_caveats": "baseline rank citation requires paper source verification",
        "finite_field_or_characteristic_scope": "as_cited_by_alphaevolve_table",
        "report_baseline_source_ref": f"baseline:{target['id']}:ref95",
    }


def test_appendix_a_matrix_subset_scope_validates_table2_and_full_table_boundaries():
    record = appendix_a_matrix_subset_scope_record()
    report = validate_appendix_a_matrix_subset_scope(record)
    full = _subset_by_id(record, "appendix_a_full")
    main_text = _subset_by_id(record, "main_text_mnp_le_5")
    table2 = _subset_by_id(record, "table_2_selected")

    assert report.ok is True
    assert record["schema"] == SUBSET_SCOPE_SCHEMA
    assert report.subset_count == 3
    assert report.main_text_target_count == 20
    assert report.full_table_target_count == EXPECTED_TARGET_COUNT == 54
    assert report.full_table_fell_behind_count == 2
    assert report.issues == []
    assert full["outcome_counts"] == {"matched": 38, "surpassed": 14, "fell_behind": 2}
    assert full["all_matched_or_surpassed"] is False
    assert full["fell_behind_target_ids"] == ["mm_4x4x9", "mm_6x6x6"]
    assert main_text["outcome_counts"] == {"matched": 17, "surpassed": 3, "fell_behind": 0}
    assert main_text["all_matched_or_surpassed"] is True
    assert set(full["fell_behind_target_ids"]).issubset(main_text["out_of_scope_target_ids"])
    assert table2["row_count"] == 16
    assert table2["outcome_counts"] == {"matched": 2, "surpassed": 14, "fell_behind": 0}
    assert table2["target_ids"][0] == "mm_2x4x5"
    assert table2["target_ids"][-1] == "mm_5x5x5"


def test_appendix_a_matrix_subset_scope_rejects_full_table_overclaim():
    record = appendix_a_matrix_subset_scope_record()
    full = _subset_by_id(record, "appendix_a_full")
    full["all_matched_or_surpassed"] = True
    full["fell_behind_target_ids"] = []
    full["outcome_counts"]["fell_behind"] = 0

    report = validate_appendix_a_matrix_subset_scope(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_outcome_counts" in codes
    assert "invalid_all_matched_or_surpassed" in codes
    assert "invalid_fell_behind_target_ids" in codes
    assert "full_table_overclaims_all_matched" in codes


def test_appendix_a_matrix_subset_scope_rejects_main_text_fell_behind_drift():
    record = appendix_a_matrix_subset_scope_record()
    main_text = _subset_by_id(record, "main_text_mnp_le_5")
    main_text["target_ids"].append("mm_4x4x9")
    main_text["row_count"] += 1
    main_text["outcome_counts"]["fell_behind"] = 1
    main_text["all_matched_or_surpassed"] = False
    main_text["fell_behind_target_ids"] = ["mm_4x4x9"]

    report = validate_appendix_a_matrix_subset_scope(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "target_ids_mismatch" in codes
    assert "invalid_row_count" in codes
    assert "invalid_outcome_counts" in codes
    assert "invalid_all_matched_or_surpassed" in codes
    assert "invalid_fell_behind_target_ids" in codes
    assert "main_text_subset_has_fell_behind" in codes


def test_appendix_a_matrix_subset_scope_rejects_table2_membership_and_source_drift():
    record = appendix_a_matrix_subset_scope_record()
    table2 = _subset_by_id(record, "table_2_selected")
    table2["target_ids"][0] = "mm_2x2x2"
    table2["source_pdf_page"] = 10
    table2["source_phrase"] = "selected matrix examples"

    report = validate_appendix_a_matrix_subset_scope(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "target_ids_mismatch" in codes
    assert "invalid_source_pdf_page" in codes
    assert "missing_table2_source_phrase" in codes


def test_appendix_a_matrix_subset_scope_summary_renders_counts():
    summary = render_appendix_a_matrix_subset_scope_summary()

    assert "AlphaEvolve matrix subset-scope evidence" in summary
    assert "| subset_count | 3 |" in summary
    assert "| main_text_target_count | 20 |" in summary
    assert "| full_table_target_count | 54 |" in summary
    assert "| full_table_fell_behind_count | 2 |" in summary


def test_appendix_a_matrix_subset_scope_artifact_boundary_accepts_current_absence():
    report = validate_appendix_a_matrix_subset_scope_artifact_boundary()

    assert report.ok is True
    assert report.artifact_status == "not_emitted_by_local_report_export"
    assert report.emitted_artifact_count == 0
    assert report.required_field_count == 12
    assert report.issues == []


def test_appendix_a_matrix_subset_scope_artifact_boundary_rejects_absence_with_artifacts():
    boundary = appendix_a_matrix_subset_scope_artifact_boundary_record()
    boundary["emitted_artifacts"] = [_subset_scope_artifact()]
    boundary["claim_boundary"] = "Artifacts exist."

    report = validate_appendix_a_matrix_subset_scope_artifact_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "unexpected_emitted_artifacts" in codes
    assert "missing_claim_boundary" in codes


def test_appendix_a_matrix_subset_scope_artifact_boundary_requires_emitted_records():
    boundary = appendix_a_matrix_subset_scope_artifact_boundary_record()
    boundary["artifact_status"] = "emitted"

    report = validate_appendix_a_matrix_subset_scope_artifact_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "missing_subset_scope_artifacts" in codes


def test_appendix_a_matrix_subset_scope_artifact_boundary_accepts_emitted_records():
    boundary = {
        "schema": SUBSET_SCOPE_ARTIFACT_BOUNDARY_SCHEMA,
        "subset_scope_schema": SUBSET_SCOPE_SCHEMA,
        "source_paper_id": "2506.13131",
        "target_suite": TARGET_SUITE,
        "artifact_status": "emitted",
        "local_export_scope": "matrix_subset_scope_report_export",
        "required_artifact_fields": list(appendix_a_matrix_subset_scope_artifact_boundary_record()["required_artifact_fields"]),
        "emitted_artifacts": [
            _subset_scope_artifact("appendix_a_full"),
            _subset_scope_artifact("main_text_mnp_le_5"),
            _subset_scope_artifact("table_2_selected"),
        ],
        "claim_boundary": "Local export emitted subset-scope artifacts.",
    }

    report = validate_appendix_a_matrix_subset_scope_artifact_boundary(boundary)

    assert report.ok is True
    assert report.artifact_status == "emitted"
    assert report.emitted_artifact_count == 3
    assert report.issues == []


def test_appendix_a_matrix_subset_scope_artifact_boundary_rejects_invalid_nested_scope():
    boundary = appendix_a_matrix_subset_scope_artifact_boundary_record()
    boundary["artifact_status"] = "emitted"
    artifact = _subset_scope_artifact()
    artifact["artifact_paths"] = ["tables/subset.json", "../escape.json"]
    artifact["artifact_sha256"] = "not-a-digest"
    artifact["subset_scope_evidence"]["subsets"] = []
    boundary["emitted_artifacts"] = [artifact]

    report = validate_appendix_a_matrix_subset_scope_artifact_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_artifact_path" in codes
    assert "invalid_artifact_sha256" in codes
    assert "invalid_nested_subset_scope_invalid_subsets" in codes


def test_appendix_a_matrix_subset_scope_artifact_boundary_summary_renders_counts():
    summary = render_appendix_a_matrix_subset_scope_artifact_boundary_summary()

    assert "AlphaEvolve matrix subset-scope artifact boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| artifact_status | not_emitted_by_local_report_export |" in summary
    assert "| emitted_artifact_count | 0 |" in summary


def test_appendix_a_matrix_row_notes_validate_concurrent_work_caveat():
    record = appendix_a_matrix_row_note_records()
    report = validate_appendix_a_matrix_row_notes(record)
    note = record["row_notes"][0]

    assert report.ok is True
    assert record["schema"] == ROW_NOTE_SCHEMA
    assert report.note_count == 1
    assert report.concurrent_work_note_count == 1
    assert report.affected_target_count == 1
    assert report.issues == []
    assert note["target_id"] == "mm_4x5x6"
    assert note["dimensions"] == [4, 5, 6]
    assert note["alphaevolve_rank"] == 90
    assert note["concurrent_rank"] == 90
    assert note["cited_reference_id"] == "49"
    assert note["relationship_to_alphaevolve"] == "independently_matched_alphaevolve_rank"
    assert note["exclusive_priority_claim_safe"] is False


def test_appendix_a_matrix_row_notes_reject_target_rank_and_reference_drift():
    record = appendix_a_matrix_row_note_records()
    note = record["row_notes"][0]
    note["target_id"] = "mm_4x4x4"
    note["dimensions"] = [4, 4, 4]
    note["alphaevolve_rank"] = 91
    note["concurrent_rank"] = 89
    note["cited_reference_id"] = "48"
    note["relationship_to_alphaevolve"] = "superseded_alphaevolve"

    report = validate_appendix_a_matrix_row_notes(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_note_target_id" in codes
    assert "invalid_note_dimensions" in codes
    assert "alphaevolve_rank_mismatch" in codes
    assert "invalid_concurrent_rank" in codes
    assert "invalid_cited_reference_id" in codes
    assert "invalid_relationship" in codes


def test_appendix_a_matrix_row_notes_reject_source_and_text_drift():
    record = appendix_a_matrix_row_note_records()
    note = record["row_notes"][0]
    record["source_pdf_page"] = 33
    note["source_table"] = "Table 2"
    note["source_pdf_page"] = 33
    note["note_text"] = "Another group improved a row."

    report = validate_appendix_a_matrix_row_notes(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_source_pdf_page" in codes
    assert "invalid_source_table" in codes
    assert "invalid_note_source_pdf_page" in codes
    assert "missing_concurrent_note_text" in codes


def test_appendix_a_matrix_row_notes_reject_exclusive_priority_overclaim():
    record = appendix_a_matrix_row_note_records()
    note = record["row_notes"][0]
    note["exclusive_priority_claim_safe"] = True
    note["docs_caveat"] = "AlphaEvolve owns the exclusive SOTA priority."

    report = validate_appendix_a_matrix_row_notes(record)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_exclusive_priority_flag" in codes
    assert "missing_exclusive_priority_caveat" in codes


def test_appendix_a_matrix_row_note_summary_renders_counts():
    summary = render_appendix_a_matrix_row_note_summary()

    assert "AlphaEvolve Appendix A matrix row-note evidence" in summary
    assert "| note_count | 1 |" in summary
    assert "| concurrent_work_note_count | 1 |" in summary
    assert "| affected_target_count | 1 |" in summary


def test_appendix_a_matrix_row_note_artifact_boundary_accepts_current_absence():
    report = validate_appendix_a_matrix_row_note_artifact_boundary()

    assert report.ok is True
    assert report.artifact_status == "not_emitted_by_local_report_export"
    assert report.emitted_artifact_count == 0
    assert report.required_field_count == 16
    assert report.issues == []


def test_appendix_a_matrix_row_note_artifact_boundary_rejects_absence_with_artifacts():
    boundary = appendix_a_matrix_row_note_artifact_boundary_record()
    boundary["emitted_artifacts"] = [_row_note_artifact()]
    boundary["claim_boundary"] = "Artifacts exist."

    report = validate_appendix_a_matrix_row_note_artifact_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "unexpected_emitted_artifacts" in codes
    assert "missing_claim_boundary" in codes


def test_appendix_a_matrix_row_note_artifact_boundary_requires_emitted_records():
    boundary = appendix_a_matrix_row_note_artifact_boundary_record()
    boundary["artifact_status"] = "emitted"

    report = validate_appendix_a_matrix_row_note_artifact_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "missing_row_note_artifacts" in codes


def test_appendix_a_matrix_row_note_artifact_boundary_accepts_emitted_record():
    boundary = appendix_a_matrix_row_note_artifact_boundary_from_records(
        artifact_sha256_by_note_id={
            "concurrent_work_rank90_mm_4x5x6": "b" * 64,
        }
    )

    report = validate_appendix_a_matrix_row_note_artifact_boundary(boundary)

    artifact = boundary["emitted_artifacts"][0]
    assert boundary["schema"] == ROW_NOTE_ARTIFACT_BOUNDARY_SCHEMA
    assert boundary["row_note_schema"] == ROW_NOTE_SCHEMA
    assert report.ok is True
    assert report.artifact_status == "emitted"
    assert report.emitted_artifact_count == 1
    assert report.issues == []
    assert artifact["note_id"] == "concurrent_work_rank90_mm_4x5x6"
    assert artifact["target_id"] == "mm_4x5x6"
    assert artifact["cited_reference_id"] == "49"
    assert artifact["artifact_paths"] == ["tables/mm_4x5x6_row_note.json"]
    assert artifact["artifact_sha256"] == "b" * 64


def test_appendix_a_matrix_row_note_artifact_boundary_builder_rejects_invalid_evidence():
    record = appendix_a_matrix_row_note_records()
    record["row_notes"] = []

    with pytest.raises(ValueError, match="row-note evidence is invalid"):
        appendix_a_matrix_row_note_artifact_boundary_from_records(record)


def test_appendix_a_matrix_row_note_artifact_boundary_rejects_invalid_nested_note():
    boundary = appendix_a_matrix_row_note_artifact_boundary_record()
    boundary["artifact_status"] = "emitted"
    artifact = _row_note_artifact()
    artifact["artifact_paths"] = ["tables/row_note.json", "../escape.json"]
    artifact["artifact_sha256"] = "not-a-digest"
    artifact["row_note_evidence"]["row_notes"] = []
    boundary["emitted_artifacts"] = [artifact]

    report = validate_appendix_a_matrix_row_note_artifact_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_artifact_path" in codes
    assert "invalid_artifact_sha256" in codes
    assert "invalid_nested_row_note_invalid_row_notes" in codes


def test_appendix_a_matrix_row_note_artifact_boundary_rejects_nested_link_mismatch():
    boundary = appendix_a_matrix_row_note_artifact_boundary_from_records(
        artifact_sha256_by_note_id={
            "concurrent_work_rank90_mm_4x5x6": "b" * 64,
        }
    )
    artifact = boundary["emitted_artifacts"][0]
    artifact["row_note_evidence"]["row_notes"][0]["target_id"] = "mm_4x4x4"

    report = validate_appendix_a_matrix_row_note_artifact_boundary(boundary)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "invalid_nested_row_note_invalid_note_target_id" in codes
    assert "invalid_artifact_nested_target_id" in codes


def test_appendix_a_matrix_row_note_artifact_boundary_summary_renders_counts():
    summary = render_appendix_a_matrix_row_note_artifact_boundary_summary()

    assert "AlphaEvolve Appendix A matrix row-note artifact boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| artifact_status | not_emitted_by_local_report_export |" in summary
    assert "| emitted_artifact_count | 0 |" in summary
