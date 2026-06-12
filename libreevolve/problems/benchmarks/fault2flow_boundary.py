from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FAULT2FLOW_BOUNDARY_SCHEMA = "libreevolve.fault2flow_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2511.12916"
EXPECTED_SOURCE_TITLE = (
    "Fault2Flow: An AlphaEvolve-Optimized Human-in-the-Loop Multi-Agent "
    "System for Fault-to-Workflow Automation"
)
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2511.12916.pdf"
EXPECTED_SOURCE_FILE = "papers/2511.12916__Fault2Flow.pdf"
EXPECTED_SOURCE_SHA256 = (
    "7319d8cc2bba103c7e508a1017b79e59a9446cab21e229760ba6b0f83945b477"
)
EXPECTED_SOURCE_BYTES = 6489403
EXPECTED_BOUNDARY_STATUS = "workflow_automation_context_without_local_fault2flow_benchmark"
EXPECTED_COMPONENT_IDS = (
    "regulatory_pdf_ingestion",
    "mineru_markdown_extraction",
    "pasta_fault_tree_schema",
    "human_in_loop_expert_review",
    "mind_map_generation_agent",
    "fault_tree_translation_agent",
    "alphaevolve_reasoning_optimizer",
    "multi_island_elite_archive",
    "n8n_workflow_synthesis",
    "workflow_verification_agent",
    "transformer_fault_dataset_rows",
    "gpt5_judge_metric_records",
    "table1_baseline_comparison_rows",
    "data_ethics_and_placeholder_metadata_records",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "alphaevolve_relation",
    "workflow_fixture_policy",
    "regulatory_source_provenance",
    "document_understanding_records",
    "mineru_extraction_records",
    "mysql_storage_records",
    "milvus_vector_search_records",
    "plantuml_mind_map_records",
    "pasta_fault_tree_records",
    "expert_review_state_records",
    "alphaevolve_optimizer_records",
    "multi_island_archive_records",
    "n8n_workflow_schema_records",
    "workflow_activation_records",
    "verification_test_case_records",
    "failure_refinement_loop_records",
    "transformer_dataset_rows",
    "evaluation_metric_definitions",
    "gpt5_judge_records",
    "table1_result_rows",
    "token_usage_records",
    "human_annotation_ethics_records",
    "independent_checker_outputs",
)
EXPECTED_MISSING_EVIDENCE = {
    "regulatory_pdf_ingestion_runtime": "not_implemented_locally",
    "mineru_markdown_extraction": "not_implemented_locally",
    "plantuml_mind_map_schema": "not_implemented_locally",
    "pasta_fault_tree_schema": "not_implemented_locally",
    "expert_review_interface_records": "not_recorded_locally",
    "alphaevolve_reasoning_optimizer": "not_implemented_locally",
    "multi_island_archive_records": "not_recorded_locally",
    "readability_logical_validity_scores": "not_recorded_locally",
    "n8n_workflow_builder": "not_implemented_locally",
    "n8n_api_activation_records": "not_recorded_locally",
    "workflow_verification_agent": "not_implemented_locally",
    "synthesized_test_case_records": "not_recorded_locally",
    "failure_refinement_loop_records": "not_recorded_locally",
    "dl_t_722_2014_dataset_snapshot": "not_recorded_locally",
    "transformer_fault_case_rows": "not_recorded_locally",
    "gpt5_judge_outputs": "not_recorded_locally",
    "table1_result_reproduction": "not_recorded_locally",
    "token_usage_records": "not_recorded_locally",
    "human_annotation_ethics_records": "not_recorded_locally",
    "local_repository_or_workflow_snapshot": "not_recorded_locally",
}


@dataclass(frozen=True)
class Fault2FlowBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class Fault2FlowBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[Fault2FlowBoundaryIssue]


def fault2flow_boundary_record() -> dict[str, Any]:
    """Return the current Fault2Flow absence/readiness boundary."""

    return {
        "schema": FAULT2FLOW_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": [
            "Yafang Wang",
            "Yangjie Tian",
            "Xiaoyu Shen",
            "Gaoyang Zhang",
            "Jiaze Sun",
            "He Zhang",
            "Ruohua Xu",
            "Feng Zhao",
        ],
        "source_version": "v1",
        "source_submitted_date": "2025-11-17",
        "source_pdf_date": "2025-11-18",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://creativecommons.org/licenses/by-nc-nd/4.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2511.12916v1",
                "status": "source_version_reference_only",
            },
            {
                "url": "https://github.com/algorithmicsuperintelligence/openevolve",
                "status": "related_alphaevolve_implementation_reference_only",
            },
            {
                "url": "<no_dedicated_fault2flow_code_repository_extracted>",
                "status": "not_found_in_extracted_links",
            },
            {
                "url": "https://doi.org/XXXXXXX.XXXXXXX",
                "status": "placeholder_publication_metadata",
            },
        ],
        "framework_components": [
            {
                "component_id": "regulatory_pdf_ingestion",
                "paper_role": "ingest regulatory PDFs for power-grid fault diagnosis",
                "local_status": "not_implemented",
            },
            {
                "component_id": "mineru_markdown_extraction",
                "paper_role": "extract structured Markdown from regulatory documents",
                "local_status": "not_implemented",
            },
            {
                "component_id": "pasta_fault_tree_schema",
                "paper_role": "represent expert-reviewed fault trees in PASTA DSL",
                "local_status": "not_implemented",
            },
            {
                "component_id": "human_in_loop_expert_review",
                "paper_role": "record expert review of mind maps, trees, and workflows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "mind_map_generation_agent",
                "paper_role": "generate PlantUML mind maps from extracted rules",
                "local_status": "not_implemented",
            },
            {
                "component_id": "fault_tree_translation_agent",
                "paper_role": "translate reviewed mind maps into PASTA fault trees",
                "local_status": "not_implemented",
            },
            {
                "component_id": "alphaevolve_reasoning_optimizer",
                "paper_role": "optimize reasoning logic with a multi-island LLM search",
                "local_status": "not_implemented",
            },
            {
                "component_id": "multi_island_elite_archive",
                "paper_role": "exchange elite reasoning candidates across islands",
                "local_status": "not_recorded",
            },
            {
                "component_id": "n8n_workflow_synthesis",
                "paper_role": "emit executable n8n workflows from PASTA trees",
                "local_status": "not_implemented",
            },
            {
                "component_id": "workflow_verification_agent",
                "paper_role": "synthesize tests and refine failed workflows",
                "local_status": "not_implemented",
            },
            {
                "component_id": "transformer_fault_dataset_rows",
                "paper_role": "evaluate sixteen transformer fault-diagnosis cases",
                "local_status": "not_recorded",
            },
            {
                "component_id": "gpt5_judge_metric_records",
                "paper_role": "score readability and semantic fidelity using GPT-5",
                "local_status": "not_recorded",
            },
            {
                "component_id": "table1_baseline_comparison_rows",
                "paper_role": "compare end-to-end baselines with Fault2Flow variants",
                "local_status": "not_recorded",
            },
            {
                "component_id": "data_ethics_and_placeholder_metadata_records",
                "paper_role": "preserve annotation ethics and ACM placeholder caveats",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_fault2flow_runner": "<none>",
            "current_workflow_scope": "python_primary_generic_search_not_fault_to_workflow_automation",
            "regulatory_ingestion_ready": False,
            "mineru_extraction_ready": False,
            "pasta_schema_ready": False,
            "expert_review_ready": False,
            "alphaevolve_optimizer_ready": False,
            "multi_island_archive_ready": False,
            "n8n_workflow_builder_ready": False,
            "workflow_activation_ready": False,
            "verification_agent_ready": False,
            "dataset_rows_ready": False,
            "gpt5_judge_ready": False,
            "table1_reproduction_ready": False,
            "repository_runtime_verified": False,
        },
        "reported_result": {
            "dataset_cases": 16,
            "three_ratio_cases": 9,
            "characteristic_gas_cases": 7,
            "topological_consistency_fault2flow": 1.0,
            "e2erc_fault2flow": 1.0,
            "success_fault2flow": "16/0",
            "qwen3_80b_end2end_success": "14/2",
            "gpt_4_1_end2end_success": "12/4",
            "qwen3_80b_end2end_avg_tokens": 21334.21,
            "qwen3_80b_fault2flow_avg_tokens": 1799.83,
            "gpt_4_1_fault2flow_avg_tokens": 1887.62,
            "source_standard": "DL/T 722-2014",
            "judge_model": "GPT-5",
            "demo_model": "Qwen3-Next-80B-A3B-Instruct",
            "demo_temperature": 0.0,
            "publication_metadata_status": "contains_acm_placeholder_conference_and_doi",
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records Fault2Flow as AlphaEvolve-optimized workflow "
            "application context only. LibreEvolve currently does not claim "
            "regulatory PDF ingestion, MinerU extraction, PlantUML mind-map "
            "generation, PASTA fault-tree translation, human-in-the-loop expert "
            "review, AlphaEvolve reasoning optimization, multi-island archive "
            "provenance, n8n workflow synthesis or activation, workflow "
            "verification/refinement, transformer fault-diagnosis dataset rows, "
            "GPT-5 judge outputs, Table 1 reproduction, token ledgers, "
            "human-annotation ethics records, or local Fault2Flow repository/runtime "
            "snapshots."
        ),
    }


def validate_fault2flow_boundary(
    boundary: object | str | Path | None = None,
) -> Fault2FlowBoundaryValidation:
    data, read_issues = _load_boundary(
        fault2flow_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return Fault2FlowBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[Fault2FlowBoundaryIssue] = []
    for field, expected in (
        ("schema", FAULT2FLOW_BOUNDARY_SCHEMA),
        ("source_paper_id", EXPECTED_SOURCE_PAPER_ID),
        ("source_title", EXPECTED_SOURCE_TITLE),
        ("source_version", "v1"),
        ("source_submitted_date", "2025-11-17"),
        ("source_pdf_date", "2025-11-18"),
        ("source_url", EXPECTED_SOURCE_URL),
        ("source_file", EXPECTED_SOURCE_FILE),
        ("source_sha256", EXPECTED_SOURCE_SHA256),
        ("source_bytes", EXPECTED_SOURCE_BYTES),
        ("source_license", "http://creativecommons.org/licenses/by-nc-nd/4.0/"),
        ("boundary_status", EXPECTED_BOUNDARY_STATUS),
    ):
        if data.get(field) != expected:
            issues.append(
                Fault2FlowBoundaryIssue(
                    f"{field}_mismatch",
                    f"{field} must match the cached Fault2Flow source evidence",
                )
            )
    if data.get("claim_ready") is not False:
        issues.append(
            Fault2FlowBoundaryIssue(
                "claim_ready_overclaim",
                "Fault2Flow workflow automation is not claim-ready",
            )
        )
    _validate_source_links(data, issues)
    _validate_components(data, issues)
    _validate_local_evidence(data, issues)
    _validate_reported_result(data, issues)
    _validate_missing_evidence(data, issues)
    required = data.get("required_evidence_fields")
    if tuple(required or ()) != EXPECTED_REQUIRED_EVIDENCE_FIELDS:
        issues.append(
            Fault2FlowBoundaryIssue(
                "required_evidence_fields_mismatch",
                "required evidence fields must remain source-specific and complete",
            )
        )
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(
            Fault2FlowBoundaryIssue(
                "claim_boundary_missing",
                "claim_boundary must state that Fault2Flow parity is not claimed",
            )
        )
    return Fault2FlowBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status")
        if isinstance(data.get("boundary_status"), str)
        else None,
        component_count=len(data.get("framework_components") or []),
        required_evidence_field_count=len(required or []),
        missing_evidence_count=len(data.get("missing_evidence") or {}),
        issues=issues,
    )


def render_fault2flow_boundary_summary(
    boundary: object | str | Path | None = None,
) -> str:
    validation = validate_fault2flow_boundary(boundary)
    lines = [
        "# Fault2Flow boundary",
        "",
        "| field | value |",
        "| --- | --- |",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<missing>'} |",
        f"| component_count | {validation.component_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "## Issues"])
        lines.extend(f"- `{issue.code}`: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object,
) -> tuple[dict[str, Any] | None, list[Fault2FlowBoundaryIssue]]:
    if isinstance(boundary, Path):
        try:
            return json.loads(boundary.read_text(encoding="utf-8")), []
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, [
                Fault2FlowBoundaryIssue(
                    "read_error", f"Could not read Fault2Flow boundary: {exc}"
                )
            ]
    if isinstance(boundary, str):
        if boundary.strip().startswith("{"):
            try:
                data = json.loads(boundary)
            except json.JSONDecodeError as exc:
                return None, [
                    Fault2FlowBoundaryIssue(
                        "json_error", f"Could not parse Fault2Flow boundary: {exc}"
                    )
                ]
            if isinstance(data, dict):
                return data, []
            return None, [
                Fault2FlowBoundaryIssue(
                    "invalid_boundary_shape",
                    "Fault2Flow boundary JSON must be an object",
                )
            ]
        return _load_boundary(Path(boundary))
    if isinstance(boundary, dict):
        return boundary, []
    return None, [
        Fault2FlowBoundaryIssue(
            "invalid_boundary_type",
            "Fault2Flow boundary must be a dict, JSON string, or JSON path",
        )
    ]


def _validate_source_links(
    data: dict[str, Any], issues: list[Fault2FlowBoundaryIssue]
) -> None:
    source_links = data.get("source_links")
    if not isinstance(source_links, list) or not source_links:
        issues.append(
            Fault2FlowBoundaryIssue(
                "source_links_missing",
                "Fault2Flow boundary must record source and artifact links",
            )
        )
        return
    expected_urls = {
        "https://arxiv.org/abs/2511.12916v1",
        "https://github.com/algorithmicsuperintelligence/openevolve",
        "<no_dedicated_fault2flow_code_repository_extracted>",
        "https://doi.org/XXXXXXX.XXXXXXX",
    }
    urls = {link.get("url") for link in source_links if isinstance(link, dict)}
    if urls != expected_urls:
        issues.append(
            Fault2FlowBoundaryIssue(
                "source_links_mismatch",
                "source links must preserve Fault2Flow paper and artifact references",
            )
        )
    allowed_statuses = {
        "source_version_reference_only",
        "related_alphaevolve_implementation_reference_only",
        "not_found_in_extracted_links",
        "placeholder_publication_metadata",
    }
    for link in source_links:
        status = link.get("status") if isinstance(link, dict) else None
        if status not in allowed_statuses:
            issues.append(
                Fault2FlowBoundaryIssue(
                    "source_link_status_overclaim",
                    "Fault2Flow links are reference-only until local workflow evidence exists",
                )
            )


def _validate_components(
    data: dict[str, Any], issues: list[Fault2FlowBoundaryIssue]
) -> None:
    components = data.get("framework_components")
    if not isinstance(components, list):
        issues.append(
            Fault2FlowBoundaryIssue(
                "framework_components_missing", "framework_components must be a list"
            )
        )
        return
    ids = tuple(
        component.get("component_id")
        for component in components
        if isinstance(component, dict)
    )
    if ids != EXPECTED_COMPONENT_IDS:
        issues.append(
            Fault2FlowBoundaryIssue(
                "framework_component_ids_mismatch",
                "framework component ids must match the Fault2Flow evidence boundary",
            )
        )
    for component in components:
        status = component.get("local_status") if isinstance(component, dict) else None
        if status not in {"not_implemented", "not_recorded"}:
            issues.append(
                Fault2FlowBoundaryIssue(
                    "framework_component_overclaim",
                    "Fault2Flow components must remain not_implemented/not_recorded",
                )
            )


def _validate_local_evidence(
    data: dict[str, Any], issues: list[Fault2FlowBoundaryIssue]
) -> None:
    evidence = data.get("local_evidence")
    if not isinstance(evidence, dict):
        issues.append(
            Fault2FlowBoundaryIssue(
                "local_evidence_missing", "local_evidence must be a dict"
            )
        )
        return
    for field in (
        "regulatory_ingestion_ready",
        "mineru_extraction_ready",
        "pasta_schema_ready",
        "expert_review_ready",
        "alphaevolve_optimizer_ready",
        "multi_island_archive_ready",
        "n8n_workflow_builder_ready",
        "workflow_activation_ready",
        "verification_agent_ready",
        "dataset_rows_ready",
        "gpt5_judge_ready",
        "table1_reproduction_ready",
        "repository_runtime_verified",
    ):
        if evidence.get(field) is not False:
            issues.append(
                Fault2FlowBoundaryIssue(
                    f"local_evidence_{field}_overclaim",
                    f"{field} must remain false until local Fault2Flow evidence exists",
                )
            )


def _validate_reported_result(
    data: dict[str, Any], issues: list[Fault2FlowBoundaryIssue]
) -> None:
    result = data.get("reported_result")
    if not isinstance(result, dict):
        issues.append(
            Fault2FlowBoundaryIssue(
                "reported_result_missing", "reported_result must be a dict"
            )
        )
        return
    expected = {
        "dataset_cases": 16,
        "three_ratio_cases": 9,
        "characteristic_gas_cases": 7,
        "topological_consistency_fault2flow": 1.0,
        "e2erc_fault2flow": 1.0,
        "success_fault2flow": "16/0",
        "qwen3_80b_end2end_success": "14/2",
        "gpt_4_1_end2end_success": "12/4",
        "qwen3_80b_end2end_avg_tokens": 21334.21,
        "qwen3_80b_fault2flow_avg_tokens": 1799.83,
        "gpt_4_1_fault2flow_avg_tokens": 1887.62,
        "source_standard": "DL/T 722-2014",
        "judge_model": "GPT-5",
        "demo_model": "Qwen3-Next-80B-A3B-Instruct",
        "demo_temperature": 0.0,
        "publication_metadata_status": "contains_acm_placeholder_conference_and_doi",
    }
    for field, expected_value in expected.items():
        if result.get(field) != expected_value:
            issues.append(
                Fault2FlowBoundaryIssue(
                    f"reported_result_{field}_mismatch",
                    f"reported_result.{field} must match the source-reported Fault2Flow result",
                )
            )


def _validate_missing_evidence(
    data: dict[str, Any], issues: list[Fault2FlowBoundaryIssue]
) -> None:
    if data.get("missing_evidence") != EXPECTED_MISSING_EVIDENCE:
        issues.append(
            Fault2FlowBoundaryIssue(
                "missing_evidence_mismatch",
                "missing evidence must match the Fault2Flow absence boundary",
            )
        )
