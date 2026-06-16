from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import logging
import os
import re
import stat
import subprocess
import tempfile
import unicodedata
from contextlib import redirect_stderr
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from pypdf import PdfReader

from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.problems.benchmarks.ablation_registry import (
    REGISTRY_PATH as ABLATION_REGISTRY_PATH,
    validate_ablation_registry,
)
from libreevolve.problems.benchmarks.acknowledgement_role_provenance_boundary import (
    acknowledgement_role_provenance_boundary_record,
    validate_acknowledgement_role_provenance_boundary,
)
from libreevolve.problems.benchmarks.alphaevolve_2026_impact_boundary import (
    EXPECTED_IMPACT_BOUNDARY_FILE,
    alphaevolve_2026_impact_boundary_record,
    validate_alphaevolve_2026_impact_boundary,
)
from libreevolve.problems.benchmarks.arxiv_abstract_snapshot import (
    alphaevolve_arxiv_abstract_snapshot_record,
    validate_alphaevolve_arxiv_abstract_snapshot,
)
from libreevolve.problems.benchmarks.alphaevolve_datacite_doi_boundary import (
    alphaevolve_datacite_doi_boundary_record,
    validate_alphaevolve_datacite_doi_boundary,
)
from libreevolve.problems.benchmarks.alphaevolve_datacite_full_response_boundary import (
    alphaevolve_datacite_full_response_boundary_record,
    validate_alphaevolve_datacite_full_response_boundary,
)
from libreevolve.problems.benchmarks.alphaevolve_doi_landing_resolution_boundary import (
    alphaevolve_doi_landing_resolution_boundary_record,
    validate_alphaevolve_doi_landing_resolution_boundary,
)
from libreevolve.problems.benchmarks.alphaevolve_tex_source_boundary import (
    alphaevolve_tex_source_boundary_record,
    validate_alphaevolve_tex_source_boundary,
)
from libreevolve.problems.benchmarks.alphaevolve_tex_archive_retention_boundary import (
    alphaevolve_tex_archive_retention_boundary_record,
    validate_alphaevolve_tex_archive_retention_boundary,
)
from libreevolve.problems.benchmarks.alphaevolve_license_page_boundary import (
    alphaevolve_license_page_boundary_record,
    validate_alphaevolve_license_page_boundary,
)
from libreevolve.problems.benchmarks.alphaevolve_license_page_html_retention_boundary import (
    alphaevolve_license_page_html_retention_boundary_record,
    validate_alphaevolve_license_page_html_retention_boundary,
)
from libreevolve.problems.benchmarks.alphaevolve_current_version_boundary import (
    alphaevolve_current_version_boundary_record,
    validate_alphaevolve_current_version_boundary,
)
from libreevolve.problems.benchmarks.alphaevolve_cached_pdf_header_consistency_boundary import (
    alphaevolve_cached_pdf_header_consistency_boundary_record,
    validate_alphaevolve_cached_pdf_header_consistency_boundary,
)
from libreevolve.problems.benchmarks.alphaevolve_metadata_extraction_script_boundary import (
    alphaevolve_metadata_extraction_script_boundary_record,
    validate_alphaevolve_metadata_extraction_script_boundary,
)
from libreevolve.problems.benchmarks.alphaevolve_source_refresh_gate_boundary import (
    alphaevolve_source_refresh_gate_boundary_record,
    validate_alphaevolve_source_refresh_gate_boundary,
)
from libreevolve.problems.benchmarks.alphaevolve_source_refresh_run_boundary import (
    alphaevolve_source_refresh_run_boundary_record,
    validate_alphaevolve_source_refresh_run_boundary,
)
from libreevolve.problems.benchmarks.alphaevolve_source_refresh_promotion_boundary import (
    alphaevolve_source_refresh_promotion_boundary_record,
    validate_alphaevolve_source_refresh_promotion_boundary,
)
from libreevolve.problems.benchmarks.alphaevolve_raw_http_headers_boundary import (
    alphaevolve_raw_http_headers_boundary_record,
    validate_alphaevolve_raw_http_headers_boundary,
)
from libreevolve.problems.benchmarks.autoconvolution_boundary import (
    autoconvolution_boundary_record,
    validate_autoconvolution_boundary,
)
from libreevolve.problems.benchmarks.bilateral_trade_boundary import (
    bilateral_trade_boundary_record,
    validate_bilateral_trade_boundary,
)
from libreevolve.problems.benchmarks.bruhat_intervals_boundary import (
    bruhat_intervals_boundary_record,
    validate_bruhat_intervals_boundary,
)
from libreevolve.problems.benchmarks.benchmark_fixture_readiness_boundary import (
    benchmark_fixture_readiness_boundary_record,
    validate_benchmark_fixture_readiness_boundary,
)
from libreevolve.problems.benchmarks.systems_result_readiness_boundary import (
    systems_result_readiness_boundary_record,
    validate_systems_result_readiness_boundary,
)
from libreevolve.problems.benchmarks.collaborator_feedback_provenance_boundary import (
    collaborator_feedback_provenance_boundary_record,
    validate_collaborator_feedback_provenance_boundary,
)
from libreevolve.problems.benchmarks.problem_formulation_provenance_boundary import (
    problem_formulation_provenance_boundary_record,
    validate_problem_formulation_provenance_boundary,
)
from libreevolve.problems.benchmarks.programmatic_representation_boundary import (
    programmatic_representation_boundary_record,
    validate_programmatic_representation_boundary,
)
from libreevolve.problems.benchmarks.qualitative_feedback_boundary import (
    qualitative_feedback_boundary_record,
    validate_qualitative_feedback_boundary,
)
from libreevolve.problems.benchmarks.feedback_calibration_boundary import (
    feedback_calibration_boundary_record,
    validate_feedback_calibration_boundary,
)
from libreevolve.problems.benchmarks.llm_role_scheduler_boundary import (
    llm_role_scheduler_boundary_record,
    validate_llm_role_scheduler_boundary,
)
from libreevolve.problems.benchmarks.llm_budget_policy_boundary import (
    llm_budget_policy_boundary_record,
    validate_llm_budget_policy_boundary,
)
from libreevolve.problems.benchmarks.llm_stochastic_reproducibility_boundary import (
    llm_stochastic_reproducibility_boundary_record,
    validate_llm_stochastic_reproducibility_boundary,
)
from libreevolve.problems.benchmarks.fast_strong_model_mix_boundary import (
    fast_strong_model_mix_boundary_record,
    validate_fast_strong_model_mix_boundary,
)
from libreevolve.problems.benchmarks.provider_cancellation_boundary import (
    provider_cancellation_boundary_record,
    validate_provider_cancellation_boundary,
)
from libreevolve.problems.benchmarks.provider_pricing_boundary import (
    provider_pricing_boundary_record,
    validate_provider_pricing_boundary,
)
from libreevolve.problems.benchmarks.provider_diagnostics_replay_boundary import (
    provider_diagnostics_replay_boundary_record,
    validate_provider_diagnostics_replay_boundary,
)
from libreevolve.problems.benchmarks.critique_reviewer_pool_boundary import (
    critique_reviewer_pool_boundary_record,
    validate_critique_reviewer_pool_boundary,
)
from libreevolve.problems.benchmarks.prompt_section_packing_boundary import (
    prompt_section_packing_boundary_record,
    validate_prompt_section_packing_boundary,
)
from libreevolve.problems.benchmarks.stochastic_prompt_format_boundary import (
    stochastic_prompt_format_boundary_record,
    validate_stochastic_prompt_format_boundary,
)
from libreevolve.problems.benchmarks.documentation_truthfulness_boundary import (
    documentation_truthfulness_boundary_record,
    validate_documentation_truthfulness_boundary,
)
from libreevolve.problems.benchmarks.documentation_claim_inventory import (
    documentation_claim_inventory_record,
    validate_documentation_claim_inventory,
)
from libreevolve.problems.benchmarks.roadmap_readiness_boundary import (
    roadmap_readiness_boundary_record,
    validate_roadmap_readiness_boundary,
)
from libreevolve.problems.benchmarks.roadmap_claim_evidence_boundary import (
    roadmap_claim_evidence_boundary_record,
    validate_roadmap_claim_evidence_boundary,
)
from libreevolve.problems.benchmarks.todo_ledger_ownership_boundary import (
    todo_ledger_ownership_boundary_record,
    validate_todo_ledger_ownership_boundary,
)
from libreevolve.problems.benchmarks.todo_canonical_gap_boundary import (
    todo_canonical_gap_boundary_record,
    validate_todo_canonical_gap_boundary,
)
from libreevolve.problems.benchmarks.roadmap_source_span_disposition_boundary import (
    roadmap_source_span_disposition_boundary_record,
    validate_roadmap_source_span_disposition_boundary,
)
from libreevolve.problems.benchmarks.roadmap_source_span_coverage_boundary import (
    roadmap_source_span_coverage_boundary_record,
    validate_roadmap_source_span_coverage_boundary,
)
from libreevolve.problems.benchmarks.roadmap_non_goal_contradiction_boundary import (
    roadmap_non_goal_contradiction_boundary_record,
    validate_roadmap_non_goal_contradiction_boundary,
)
from libreevolve.problems.benchmarks.roadmap_non_goal_drift_boundary import (
    roadmap_non_goal_drift_boundary_record,
    validate_roadmap_non_goal_drift_boundary,
)
from libreevolve.problems.benchmarks.roadmap_good_first_followups_boundary import (
    roadmap_good_first_followups_boundary_record,
    validate_roadmap_good_first_followups_boundary,
)
from libreevolve.problems.benchmarks.roadmap_good_first_freshness_boundary import (
    roadmap_good_first_freshness_boundary_record,
    validate_roadmap_good_first_freshness_boundary,
)
from libreevolve.problems.benchmarks.roadmap_phase_sequence_boundary import (
    roadmap_phase_sequence_boundary_record,
    validate_roadmap_phase_sequence_boundary,
)
from libreevolve.problems.benchmarks.roadmap_phase_freshness_boundary import (
    roadmap_phase_freshness_boundary_record,
    validate_roadmap_phase_freshness_boundary,
)
from libreevolve.problems.benchmarks.roadmap_operational_maturity_boundary import (
    roadmap_operational_maturity_boundary_record,
    validate_roadmap_operational_maturity_boundary,
)
from libreevolve.problems.benchmarks.roadmap_operational_readiness_boundary import (
    roadmap_operational_readiness_boundary_record,
    validate_roadmap_operational_readiness_boundary,
)
from libreevolve.problems.benchmarks.roadmap_representative_benchmark_portfolio_boundary import (
    roadmap_representative_benchmark_portfolio_boundary_record,
    validate_roadmap_representative_benchmark_portfolio_boundary,
)
from libreevolve.problems.benchmarks.roadmap_benchmark_portfolio_readiness_boundary import (
    roadmap_benchmark_portfolio_readiness_boundary_record,
    validate_roadmap_benchmark_portfolio_readiness_boundary,
)
from libreevolve.problems.benchmarks.roadmap_plugin_extensibility_boundary import (
    roadmap_plugin_extensibility_boundary_record,
    validate_roadmap_plugin_extensibility_boundary,
)
from libreevolve.problems.benchmarks.roadmap_plugin_readiness_boundary import (
    roadmap_plugin_readiness_boundary_record,
    validate_roadmap_plugin_readiness_boundary,
)
from libreevolve.problems.benchmarks.roadmap_backend_scheduling_critique_boundary import (
    roadmap_backend_scheduling_critique_boundary_record,
    validate_roadmap_backend_scheduling_critique_boundary,
)
from libreevolve.problems.benchmarks.roadmap_backend_control_plane_readiness_boundary import (
    roadmap_backend_control_plane_readiness_boundary_record,
    validate_roadmap_backend_control_plane_readiness_boundary,
)
from libreevolve.problems.benchmarks.roadmap_async_resumable_runtime_boundary import (
    roadmap_async_resumable_runtime_boundary_record,
    validate_roadmap_async_resumable_runtime_boundary,
)
from libreevolve.problems.benchmarks.roadmap_async_runtime_readiness_boundary import (
    roadmap_async_runtime_readiness_boundary_record,
    validate_roadmap_async_runtime_readiness_boundary,
)
from libreevolve.problems.benchmarks.roadmap_prompt_context_system_boundary import (
    roadmap_prompt_context_system_boundary_record,
    validate_roadmap_prompt_context_system_boundary,
)
from libreevolve.problems.benchmarks.roadmap_evaluation_cascade_boundary import (
    roadmap_evaluation_cascade_boundary_record,
    validate_roadmap_evaluation_cascade_boundary,
)
from libreevolve.problems.benchmarks.roadmap_candidate_workspace_fidelity_boundary import (
    roadmap_candidate_workspace_fidelity_boundary_record,
    validate_roadmap_candidate_workspace_fidelity_boundary,
)
from libreevolve.problems.benchmarks.roadmap_multi_objective_search_boundary import (
    roadmap_multi_objective_search_boundary_record,
    validate_roadmap_multi_objective_search_boundary,
)
from libreevolve.problems.benchmarks.implementation_evidence_map_boundary import (
    implementation_evidence_map_boundary_record,
    validate_implementation_evidence_map_boundary,
)
from libreevolve.problems.benchmarks.release_artifact_reproducibility_boundary import (
    release_artifact_reproducibility_boundary_record,
    validate_release_artifact_reproducibility_boundary,
)
from libreevolve.problems.benchmarks.related_work_taxonomy_boundary import (
    related_work_taxonomy_boundary_record,
    validate_related_work_taxonomy_boundary,
)
from libreevolve.problems.benchmarks.task_specification_boundary import (
    task_specification_boundary_record,
    validate_task_specification_boundary,
)
from libreevolve.problems.benchmarks.fault2flow_boundary import (
    fault2flow_boundary_record,
    validate_fault2flow_boundary,
)
from libreevolve.problems.benchmarks.global_nlp_optimization_boundary import (
    global_nlp_optimization_boundary_record,
    validate_global_nlp_optimization_boundary,
)
from libreevolve.problems.benchmarks.ablation_exhibits import (
    figure8_artifact_boundary_record,
    validate_figure8_artifact_boundary,
)
from libreevolve.problems.benchmarks.archagent_boundary import (
    archagent_boundary_record,
    validate_archagent_boundary,
)
from libreevolve.problems.benchmarks.automated_evaluator_scope_boundary import (
    automated_evaluator_scope_boundary_record,
    validate_automated_evaluator_scope_boundary,
)
from libreevolve.problems.benchmarks.appendix_a_matrix_registry import (
    REGISTRY_PATH as APPENDIX_A_MATRIX_REGISTRY_PATH,
    appendix_a_matrix_baseline_citation_boundary_record,
    appendix_a_matrix_curation_record,
    appendix_a_matrix_excluded_target_curation_boundary_record,
    appendix_a_matrix_local_resource_frontier_record,
    appendix_a_matrix_resource_frontier_record,
    appendix_a_matrix_row_note_artifact_boundary_record,
    appendix_a_matrix_subset_scope_artifact_boundary_record,
    validate_appendix_a_matrix_baseline_citation_boundary,
    validate_appendix_a_matrix_curation,
    validate_appendix_a_matrix_excluded_target_curation_boundary,
    validate_appendix_a_matrix_local_resource_frontier,
    validate_appendix_a_matrix_resource_frontier,
    validate_appendix_a_matrix_registry,
    validate_appendix_a_matrix_row_note_artifact_boundary,
    validate_appendix_a_matrix_subset_scope_artifact_boundary,
)
from libreevolve.problems.benchmarks.appendix_b_registry import (
    REGISTRY_PATH as APPENDIX_B_REGISTRY_PATH,
    validate_appendix_b_registry,
)
from libreevolve.problems.benchmarks.candidate_abstraction import (
    candidate_abstraction_boundary_record,
    validate_candidate_abstraction_boundary,
)
from libreevolve.problems.benchmarks.candidate_abstraction_bias import (
    candidate_abstraction_bias_matrix_record,
    validate_candidate_abstraction_bias_matrix,
)
from libreevolve.problems.benchmarks.candidate_language_runner_boundary import (
    candidate_language_runner_boundary_record,
    validate_candidate_language_runner_boundary,
)
from libreevolve.problems.benchmarks.ci_workflow_coverage_boundary import (
    ci_workflow_coverage_boundary_record,
    validate_ci_workflow_coverage_boundary,
)
from libreevolve.problems.benchmarks.config_validation_boundary import (
    config_validation_boundary_record,
    validate_config_validation_boundary,
)
from libreevolve.problems.benchmarks.causalevolve_boundary import (
    causalevolve_boundary_record,
    validate_causalevolve_boundary,
)
from libreevolve.problems.benchmarks.deepevolve_boundary import (
    deepevolve_boundary_record,
    validate_deepevolve_boundary,
)
from libreevolve.problems.benchmarks.distributed_pipeline_topology_boundary import (
    distributed_pipeline_topology_boundary_record,
    validate_distributed_pipeline_topology_boundary,
)
from libreevolve.problems.benchmarks.workspace_materialization_boundary import (
    validate_workspace_materialization_boundary,
    workspace_materialization_boundary_record,
)
from libreevolve.problems.benchmarks.codebase_scale_benchmark_boundary import (
    codebase_scale_benchmark_boundary_record,
    validate_codebase_scale_benchmark_boundary,
)
from libreevolve.problems.benchmarks.sorting_network_rediscovery_boundary import (
    sorting_network_rediscovery_boundary_record,
    validate_sorting_network_rediscovery_boundary,
)
from libreevolve.problems.benchmarks.table1_capability_exhibit_boundary import (
    table1_capability_exhibit_boundary_record,
    validate_table1_capability_exhibit_boundary,
)
from libreevolve.problems.benchmarks.self_improvement_distillation_boundary import (
    self_improvement_distillation_boundary_record,
    validate_self_improvement_distillation_boundary,
)
from libreevolve.problems.benchmarks.self_improvement_cadence_boundary import (
    self_improvement_cadence_boundary_record,
    validate_self_improvement_cadence_boundary,
)
from libreevolve.problems.benchmarks.codeevolve_boundary import (
    codeevolve_boundary_record,
    validate_codeevolve_boundary,
)
from libreevolve.problems.benchmarks.combinatorics_berczy_boundary import (
    combinatorics_berczy_boundary_record,
    validate_combinatorics_berczy_boundary,
)
from libreevolve.problems.benchmarks.evaluation_cascade_boundary import (
    evaluation_cascade_boundary_record,
    validate_evaluation_cascade_boundary,
)
from libreevolve.problems.benchmarks.cascade_hypothesis_test_boundary import (
    cascade_hypothesis_test_boundary_record,
    validate_cascade_hypothesis_test_boundary,
)
from libreevolve.problems.benchmarks.evaluator_oracle_boundary import (
    evaluator_oracle_boundary_record,
    validate_evaluator_oracle_boundary,
)
from libreevolve.problems.benchmarks.embedded_evaluator_boundary import (
    embedded_evaluator_boundary_record,
    validate_embedded_evaluator_boundary,
)
from libreevolve.problems.benchmarks.figure3_supervised_exhibit_boundary import (
    figure3_supervised_exhibit_boundary_record,
    validate_figure3_supervised_exhibit_boundary,
)
from libreevolve.problems.benchmarks.figure6_scheduling_exhibit_boundary import (
    figure6_scheduling_exhibit_boundary_record,
    validate_figure6_scheduling_exhibit_boundary,
)
from libreevolve.problems.benchmarks.figure7_pallas_tiling_exhibit_boundary import (
    figure7_pallas_tiling_exhibit_boundary_record,
    validate_figure7_pallas_tiling_exhibit_boundary,
)
from libreevolve.problems.benchmarks.example_scope import (
    example_benchmark_scope_records,
    validate_example_benchmark_scope,
)
from libreevolve.problems.benchmarks.existing_codebase_integration import (
    existing_codebase_integration_boundary_record,
    validate_existing_codebase_integration_boundary,
)
from libreevolve.problems.benchmarks.math_outcomes import (
    alphaevolve_math_heuristic_handoff_boundary,
    alphaevolve_math_heuristic_stage_sequence_boundary,
    alphaevolve_math_outcome_boundary,
    alphaevolve_math_starting_construction_boundary,
    validate_math_heuristic_handoff_boundary,
    validate_math_heuristic_stage_sequence_boundary,
    validate_math_outcome_boundary,
    validate_math_starting_construction_boundary,
)
from libreevolve.problems.benchmarks.follow_on_sources import (
    EXPECTED_FOLLOW_ON_REPOSITORY_RIGHTS_MANIFEST_FILE,
    EXPECTED_FOLLOW_ON_RUNTIME_ABSENCE_MANIFEST_FILE,
    EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE,
    EXPECTED_FOLLOW_ON_TAO_BLOG_MANIFEST_FILE,
    alphaevolve_follow_on_math_source_record,
    validate_alphaevolve_follow_on_repository_rights_manifest,
    validate_alphaevolve_follow_on_runtime_absence_manifest,
    validate_alphaevolve_follow_on_source_manifest,
    validate_alphaevolve_follow_on_tao_blog_manifest,
    validate_alphaevolve_follow_on_math_source,
)
from libreevolve.problems.benchmarks.follow_on_coverage import (
    alphaevolve_follow_on_problem_coverage_record,
    validate_alphaevolve_follow_on_problem_coverage,
)
from libreevolve.problems.benchmarks.theoretical_cs_sources import (
    EXPECTED_THEORETICAL_CS_SOURCE_MANIFEST_FILE,
    validate_alphaevolve_theoretical_cs_source_manifest,
)
from libreevolve.problems.benchmarks.official_deepmind_blog import (
    EXPECTED_OFFICIAL_BLOG_MANIFEST_FILE,
    validate_alphaevolve_official_blog_manifest,
)
from libreevolve.problems.benchmarks.paper_source_versions import (
    EXPECTED_SOURCE_VERSION_MANIFEST_FILE,
    alphaevolve_source_pdf_version_record,
    validate_alphaevolve_source_pdf_version_manifest,
    validate_alphaevolve_source_pdf_version,
)
from libreevolve.problems.benchmarks.paper_source_rights import (
    EXPECTED_SOURCE_RIGHTS_MANIFEST_FILE,
    alphaevolve_source_pdf_rights_record,
    validate_alphaevolve_source_pdf_rights_manifest,
    validate_alphaevolve_source_pdf_rights,
)
from libreevolve.problems.benchmarks.paper_source_identity import (
    PAPER_SOURCE_IDENTITY_MANIFEST_FILE,
    validate_paper_source_identity_manifest,
)
from libreevolve.problems.benchmarks.process_exhibit_boundary import (
    process_exhibit_boundary_record,
    validate_process_exhibit_boundary,
)
from libreevolve.problems.benchmarks.proposal_lifecycle_audit import (
    proposal_lifecycle_audit_boundary_record,
    validate_proposal_lifecycle_audit_boundary,
)
from libreevolve.problems.benchmarks.incorrect_suggestion_audit_boundary import (
    incorrect_suggestion_audit_boundary_record,
    validate_incorrect_suggestion_audit_boundary,
)
from libreevolve.problems.benchmarks.initial_program_idea_provenance_boundary import (
    initial_program_idea_provenance_boundary_record,
    validate_initial_program_idea_provenance_boundary,
)
from libreevolve.problems.benchmarks.initial_program_seed_variants import (
    initial_program_seed_variant_matrix_record,
    validate_initial_program_seed_variant_matrix,
)
from libreevolve.problems.benchmarks.initial_program_validity_boundary import (
    initial_program_validity_boundary_record,
    validate_initial_program_validity_boundary,
)
from libreevolve.problems.benchmarks.repeated_sampling_baseline_boundary import (
    repeated_sampling_baseline_boundary_record,
    validate_repeated_sampling_baseline_boundary,
)
from libreevolve.problems.benchmarks.sampling_balance_boundary import (
    sampling_balance_boundary_record,
    validate_sampling_balance_boundary,
)
from libreevolve.problems.benchmarks.sample_efficiency_boundary import (
    sample_efficiency_boundary_record,
    validate_sample_efficiency_boundary,
)
from libreevolve.problems.benchmarks.parallel_evaluation_readiness_boundary import (
    parallel_evaluation_readiness_boundary_record,
    validate_parallel_evaluation_readiness_boundary,
)
from libreevolve.problems.benchmarks.expensive_evaluation_budget_boundary import (
    expensive_evaluation_budget_boundary_record,
    validate_expensive_evaluation_budget_boundary,
)
from libreevolve.problems.benchmarks.natural_language_preamble_boundary import (
    natural_language_preamble_boundary_record,
    validate_natural_language_preamble_boundary,
)
from libreevolve.problems.benchmarks.prompt_example_copy_boundary import (
    prompt_example_copy_boundary_record,
    validate_prompt_example_copy_boundary,
)
from libreevolve.problems.benchmarks.mutation_consistency_boundary import (
    mutation_consistency_boundary_record,
    validate_mutation_consistency_boundary,
)
from libreevolve.problems.benchmarks.mutation_operator_boundary import (
    mutation_operator_boundary_record,
    validate_mutation_operator_boundary,
)
from libreevolve.problems.benchmarks.adaptive_mutation_mode_boundary import (
    adaptive_mutation_mode_boundary_record,
    validate_adaptive_mutation_mode_boundary,
)
from libreevolve.problems.benchmarks.initial_pool_divergence_boundary import (
    initial_pool_divergence_boundary_record,
    validate_initial_pool_divergence_boundary,
)
from libreevolve.problems.benchmarks.duplicate_work_policy_boundary import (
    duplicate_work_policy_boundary_record,
    validate_duplicate_work_policy_boundary,
)
from libreevolve.problems.benchmarks.ramsey_numbers_boundary import (
    ramsey_numbers_boundary_record,
    validate_ramsey_numbers_boundary,
)
from libreevolve.problems.benchmarks.sums_differences_boundary import (
    sums_differences_boundary_record,
    validate_sums_differences_boundary,
)
from libreevolve.problems.benchmarks.sums_differences_sequence_boundary import (
    sums_differences_sequence_boundary_record,
    validate_sums_differences_sequence_boundary,
)
from libreevolve.problems.benchmarks.system_contribution_provenance_boundary import (
    system_contribution_provenance_boundary_record,
    validate_system_contribution_provenance_boundary,
)
from libreevolve.problems.benchmarks.ucb1_boundary import (
    ucb1_boundary_record,
    validate_ucb1_boundary,
)
from libreevolve.problems.benchmarks.whole_run_source_workspace_integrity_boundary import (
    validate_whole_run_source_workspace_integrity_boundary,
    whole_run_source_workspace_integrity_boundary_record,
)
from libreevolve.problems.benchmarks.paper_bibliography import (
    EXPECTED_REFERENCES_BIBLIOGRAPHY_FILE,
    alphaevolve_references_section_record,
    validate_alphaevolve_references_bibliography,
    validate_alphaevolve_references_section,
)
from libreevolve.problems.benchmarks.companion_sources import (
    EXPECTED_COMPANION_SOURCE_MANIFEST_FILE,
    validate_alphaevolve_companion_source_manifest,
)
from libreevolve.problems.benchmarks.controller_backtracking_boundary import (
    controller_backtracking_boundary_record,
    validate_controller_backtracking_boundary,
)
from libreevolve.problems.benchmarks.paper_artifact_roles import (
    alphaevolve_paper_artifact_linkage_record,
    alphaevolve_paper_artifact_role_records,
    validate_paper_artifact_linkage,
    validate_paper_artifact_roles,
)
from libreevolve.problems.benchmarks.paper_author_metadata_boundary import (
    paper_author_metadata_boundary_record,
    validate_paper_author_metadata_boundary,
)
from libreevolve.problems.benchmarks.matrix_exhibits import (
    figure4_matrix_discovery_artifact_boundary_record,
    figure9_matrix_diff_artifact_boundary_record,
    matrix_rank_table_artifact_boundary_record,
    validate_figure4_matrix_discovery_artifact_boundary,
    validate_figure9_matrix_diff_artifact_boundary,
    validate_matrix_rank_table_artifact_boundary,
)
from libreevolve.problems.benchmarks.matrix_results import (
    matrix_baseline_component_runtime_boundary_record,
    matrix_cascade_run_runtime_boundary_record,
    matrix_headline_historicity_runtime_boundary_record,
    matrix_near_integrality_runtime_boundary_record,
    matrix_scalar_field_runtime_boundary_record,
    matrix_suite_publication_artifact_boundary_record,
    matrix_sweep_space_runtime_boundary_record,
    matrix_tensor_rank_runtime_boundary_record,
    validate_strassen_2x2_publication_bundle,
    validate_matrix_baseline_component_runtime_boundary,
    validate_matrix_cascade_run_runtime_boundary,
    validate_matrix_headline_historicity_runtime_boundary,
    validate_matrix_near_integrality_runtime_boundary,
    validate_matrix_scalar_field_runtime_boundary,
    validate_matrix_suite_publication_artifact_boundary,
    validate_matrix_sweep_space_runtime_boundary,
    validate_matrix_tensor_rank_runtime_boundary,
)
from libreevolve.problems.benchmarks.map_elites_illumination_boundary import (
    map_elites_illumination_boundary_record,
    validate_map_elites_illumination_boundary,
)
from libreevolve.problems.benchmarks.map_elites_descriptor_boundary import (
    map_elites_descriptor_boundary_record,
    validate_map_elites_descriptor_boundary,
)
from libreevolve.problems.benchmarks.objective_archive_boundary import (
    objective_archive_boundary_record,
    validate_objective_archive_boundary,
)
from libreevolve.problems.benchmarks.archive_event_replay_boundary import (
    archive_event_replay_boundary_record,
    validate_archive_event_replay_boundary,
)
from libreevolve.problems.benchmarks.controller_pending_work_resume_boundary import (
    controller_pending_work_resume_boundary_record,
    validate_controller_pending_work_resume_boundary,
)
from libreevolve.problems.benchmarks.lineage_replay_boundary import (
    lineage_replay_boundary_record,
    validate_lineage_replay_boundary,
)
from libreevolve.problems.benchmarks.runtime_rng_replay_boundary import (
    runtime_rng_replay_boundary_record,
    validate_runtime_rng_replay_boundary,
)
from libreevolve.problems.benchmarks.validator_execution_boundary import (
    validate_validator_execution_boundary,
    validator_execution_boundary_record,
)
from libreevolve.problems.benchmarks.validator_artifact_promotion_boundary import (
    validate_validator_artifact_promotion_boundary,
    validator_artifact_promotion_boundary_record,
)
from libreevolve.problems.benchmarks.metric_diverse_prompt_boundary import (
    metric_diverse_prompt_boundary_record,
    validate_metric_diverse_prompt_boundary,
)
from libreevolve.problems.benchmarks.proposal_score_boundary import (
    proposal_score_boundary_record,
    validate_proposal_score_boundary,
)
from libreevolve.problems.benchmarks.proposal_diversity_boundary import (
    proposal_diversity_boundary_record,
    validate_proposal_diversity_boundary,
)
from libreevolve.problems.benchmarks.failure_memory_boundary import (
    failure_memory_boundary_record,
    validate_failure_memory_boundary,
)
from libreevolve.problems.benchmarks.program_output_boundary import (
    program_output_boundary_record,
    validate_program_output_boundary,
)
from libreevolve.problems.benchmarks.artifact_index_boundary import (
    artifact_index_boundary_record,
    validate_artifact_index_boundary,
)
from libreevolve.problems.benchmarks.gigaevo_boundary import (
    gigaevo_framework_boundary_record,
    validate_gigaevo_framework_boundary,
)
from libreevolve.problems.benchmarks.gemini_self_training_loop_boundary import (
    gemini_self_training_loop_boundary_record,
    validate_gemini_self_training_loop_boundary,
)
from libreevolve.problems.benchmarks.hardware_rtl_eda_evidence_boundary import (
    hardware_rtl_eda_evidence_boundary_record,
    validate_hardware_rtl_eda_evidence_boundary,
)
from libreevolve.problems.benchmarks.hardware_rewrite_artifact_boundary import (
    hardware_rewrite_artifact_boundary_record,
    validate_hardware_rewrite_artifact_boundary,
)
from libreevolve.problems.benchmarks.hardware_contribution_attribution_boundary import (
    hardware_contribution_attribution_boundary_record,
    validate_hardware_contribution_attribution_boundary,
)
from libreevolve.problems.benchmarks.compiler_ir_reference_check_boundary import (
    compiler_ir_reference_check_boundary_record,
    validate_compiler_ir_reference_check_boundary,
)
from libreevolve.problems.benchmarks.compiler_adoption_path_boundary import (
    compiler_adoption_path_boundary_record,
    validate_compiler_adoption_path_boundary,
)
from libreevolve.problems.benchmarks.compiler_stack_context_boundary import (
    compiler_stack_context_boundary_record,
    validate_compiler_stack_context_boundary,
)
from libreevolve.problems.benchmarks.gemini_provider_parity_boundary import (
    gemini_provider_parity_boundary_record,
    validate_gemini_provider_parity_boundary,
)
from libreevolve.problems.benchmarks.kernel_tiling_shape_corpus_boundary import (
    kernel_tiling_shape_corpus_boundary_record,
    validate_kernel_tiling_shape_corpus_boundary,
)
from libreevolve.problems.benchmarks.pallas_workflow_baseline_boundary import (
    pallas_workflow_baseline_boundary_record,
    validate_pallas_workflow_baseline_boundary,
)
from libreevolve.problems.benchmarks.improvevolve_boundary import (
    improvevolve_boundary_record,
    validate_improvevolve_boundary,
)
from libreevolve.problems.benchmarks.madevolve_boundary import (
    madevolve_boundary_record,
    validate_madevolve_boundary,
)
from libreevolve.problems.benchmarks.magellan_boundary import (
    magellan_boundary_record,
    validate_magellan_boundary,
)
from libreevolve.problems.benchmarks.multiagent_learning_boundary import (
    multiagent_learning_boundary_record,
    validate_multiagent_learning_boundary,
)
from libreevolve.problems.benchmarks.thetaevolve_boundary import (
    thetaevolve_boundary_record,
    validate_thetaevolve_boundary,
)
from libreevolve.problems.benchmarks.title_page_affiliation_boundary import (
    title_page_affiliation_boundary_record,
    validate_title_page_affiliation_boundary,
)
from libreevolve.problems.benchmarks.ttt_discover_boundary import (
    ttt_discover_boundary_record,
    validate_ttt_discover_boundary,
)


REQUIRED_FIELDS = ("id", "title", "url", "file", "ok", "bytes", "sha256", "message")
ARXIV_ABSTRACT_SNAPSHOT_FILE = "papers/arxiv_abstract_snapshot.json"
ALPHAEVOLVE_CURRENT_VERSION_BOUNDARY_FILE = "papers/alphaevolve_current_version_boundary.json"
ALPHAEVOLVE_CACHED_PDF_HEADER_CONSISTENCY_BOUNDARY_FILE = "papers/alphaevolve_cached_pdf_header_consistency_boundary.json"
ALPHAEVOLVE_METADATA_EXTRACTION_SCRIPT_BOUNDARY_FILE = "papers/alphaevolve_metadata_extraction_script_boundary.json"
ALPHAEVOLVE_SOURCE_REFRESH_GATE_BOUNDARY_FILE = "papers/alphaevolve_source_refresh_gate_boundary.json"
ALPHAEVOLVE_SOURCE_REFRESH_RUN_BOUNDARY_FILE = "papers/alphaevolve_source_refresh_run_2026-06-14.json"
ALPHAEVOLVE_SOURCE_REFRESH_PROMOTION_BOUNDARY_FILE = "papers/alphaevolve_source_refresh_promotion_boundary.json"
ALPHAEVOLVE_RAW_HTTP_HEADERS_BOUNDARY_FILE = "papers/alphaevolve_raw_http_headers_boundary.json"
ALPHAEVOLVE_DATACITE_DOI_BOUNDARY_FILE = "papers/alphaevolve_datacite_doi_boundary.json"
ALPHAEVOLVE_DATACITE_FULL_RESPONSE_BOUNDARY_FILE = "papers/alphaevolve_datacite_full_response_boundary.json"
ALPHAEVOLVE_DOI_LANDING_RESOLUTION_BOUNDARY_FILE = "papers/alphaevolve_doi_landing_resolution_boundary.json"
ALPHAEVOLVE_TEX_SOURCE_BOUNDARY_FILE = "papers/alphaevolve_tex_source_boundary.json"
ALPHAEVOLVE_TEX_ARCHIVE_RETENTION_BOUNDARY_FILE = "papers/alphaevolve_tex_archive_retention_boundary.json"
ALPHAEVOLVE_LICENSE_PAGE_BOUNDARY_FILE = "papers/alphaevolve_license_page_boundary.json"
ALPHAEVOLVE_LICENSE_PAGE_HTML_RETENTION_BOUNDARY_FILE = "papers/alphaevolve_license_page_html_retention_boundary.json"
APPENDIX_A_CURATION_FILE = "papers/appendix_a_matrix_curation.json"
APPENDIX_A_EXCLUDED_TARGET_CURATION_FILE = "papers/appendix_a_matrix_excluded_target_curation.json"
APPENDIX_A_RESOURCE_FRONTIER_FILE = "papers/appendix_a_matrix_resource_frontier.json"
APPENDIX_A_LOCAL_RESOURCE_FRONTIER_FILE = "papers/appendix_a_matrix_local_resource_frontier.json"
APPENDIX_A_SUBSET_SCOPE_ARTIFACTS_FILE = "papers/appendix_a_matrix_subset_scope_artifacts.json"
APPENDIX_A_ROW_NOTE_ARTIFACTS_FILE = "papers/appendix_a_matrix_row_note_artifacts.json"
MATRIX_SUITE_PUBLICATION_ARTIFACTS_FILE = "papers/matrix_suite_publication_artifacts.json"
MATRIX_RANK_TABLE_ARTIFACTS_FILE = "papers/matrix_rank_table_artifacts.json"
FIGURE9_MATRIX_DIFF_ARTIFACTS_FILE = "papers/figure9_matrix_diff_artifacts.json"
FIGURE4_MATRIX_DISCOVERY_ARTIFACTS_FILE = "papers/figure4_matrix_discovery_artifacts.json"
FIGURE8_ABLATION_ARTIFACTS_FILE = "papers/figure8_ablation_artifacts.json"
BENCHMARK_FIXTURE_READINESS_BOUNDARY_FILE = "papers/benchmark_fixture_readiness_boundary.json"
SYSTEMS_RESULT_READINESS_BOUNDARY_FILE = "papers/systems_result_readiness_boundary.json"
ACKNOWLEDGEMENT_ROLE_PROVENANCE_BOUNDARY_FILE = "papers/acknowledgement_role_provenance_boundary.json"
PAPER_AUTHOR_METADATA_BOUNDARY_FILE = "papers/paper_author_metadata_boundary.json"
TITLE_PAGE_AFFILIATION_BOUNDARY_FILE = "papers/title_page_affiliation_boundary.json"
SYSTEM_CONTRIBUTION_PROVENANCE_BOUNDARY_FILE = "papers/system_contribution_provenance_boundary.json"
INITIAL_PROGRAM_IDEA_PROVENANCE_BOUNDARY_FILE = "papers/initial_program_idea_provenance_boundary.json"
INITIAL_PROGRAM_SEED_VARIANT_MATRIX_FILE = "papers/initial_program_seed_variant_matrix.json"
INITIAL_PROGRAM_VALIDITY_BOUNDARY_FILE = "papers/initial_program_validity_boundary.json"
COLLABORATOR_FEEDBACK_PROVENANCE_BOUNDARY_FILE = "papers/collaborator_feedback_provenance_boundary.json"
PROBLEM_FORMULATION_PROVENANCE_BOUNDARY_FILE = "papers/problem_formulation_provenance_boundary.json"
PROGRAMMATIC_REPRESENTATION_BOUNDARY_FILE = "papers/programmatic_representation_boundary.json"
QUALITATIVE_FEEDBACK_BOUNDARY_FILE = "papers/qualitative_feedback_boundary.json"
FEEDBACK_CALIBRATION_BOUNDARY_FILE = "papers/feedback_calibration_boundary.json"
LLM_ROLE_SCHEDULER_BOUNDARY_FILE = "papers/llm_role_scheduler_boundary.json"
LLM_BUDGET_POLICY_BOUNDARY_FILE = "papers/llm_budget_policy_boundary.json"
LLM_STOCHASTIC_REPRODUCIBILITY_BOUNDARY_FILE = "papers/llm_stochastic_reproducibility_boundary.json"
FAST_STRONG_MODEL_MIX_BOUNDARY_FILE = "papers/fast_strong_model_mix_boundary.json"
PROVIDER_CANCELLATION_BOUNDARY_FILE = "papers/provider_cancellation_boundary.json"
PROVIDER_PRICING_BOUNDARY_FILE = "papers/provider_pricing_boundary.json"
PROVIDER_DIAGNOSTICS_REPLAY_BOUNDARY_FILE = "papers/provider_diagnostics_replay_boundary.json"
CRITIQUE_REVIEWER_POOL_BOUNDARY_FILE = "papers/critique_reviewer_pool_boundary.json"
PROMPT_SECTION_PACKING_BOUNDARY_FILE = "papers/prompt_section_packing_boundary.json"
STOCHASTIC_PROMPT_FORMAT_BOUNDARY_FILE = "papers/stochastic_prompt_format_boundary.json"
DOCUMENTATION_TRUTHFULNESS_BOUNDARY_FILE = "papers/documentation_truthfulness_boundary.json"
DOCUMENTATION_CLAIM_INVENTORY_FILE = "papers/documentation_claim_inventory.json"
ROADMAP_READINESS_BOUNDARY_FILE = "papers/roadmap_readiness_boundary.json"
ROADMAP_CLAIM_EVIDENCE_BOUNDARY_FILE = "papers/roadmap_claim_evidence_boundary.json"
TODO_LEDGER_OWNERSHIP_BOUNDARY_FILE = "papers/todo_ledger_ownership_boundary.json"
TODO_CANONICAL_GAP_BOUNDARY_FILE = "papers/todo_canonical_gap_boundary.json"
ROADMAP_SOURCE_SPAN_DISPOSITION_BOUNDARY_FILE = "papers/roadmap_source_span_disposition_boundary.json"
ROADMAP_SOURCE_SPAN_COVERAGE_BOUNDARY_FILE = "papers/roadmap_source_span_coverage_boundary.json"
ROADMAP_NON_GOAL_CONTRADICTION_BOUNDARY_FILE = "papers/roadmap_non_goal_contradiction_boundary.json"
ROADMAP_NON_GOAL_DRIFT_BOUNDARY_FILE = "papers/roadmap_non_goal_drift_boundary.json"
ROADMAP_GOOD_FIRST_FOLLOWUPS_BOUNDARY_FILE = "papers/roadmap_good_first_followups_boundary.json"
ROADMAP_GOOD_FIRST_FRESHNESS_BOUNDARY_FILE = "papers/roadmap_good_first_freshness_boundary.json"
ROADMAP_PHASE_SEQUENCE_BOUNDARY_FILE = "papers/roadmap_phase_sequence_boundary.json"
ROADMAP_PHASE_FRESHNESS_BOUNDARY_FILE = "papers/roadmap_phase_freshness_boundary.json"
ROADMAP_OPERATIONAL_MATURITY_BOUNDARY_FILE = "papers/roadmap_operational_maturity_boundary.json"
ROADMAP_OPERATIONAL_READINESS_BOUNDARY_FILE = "papers/roadmap_operational_readiness_boundary.json"
ROADMAP_REPRESENTATIVE_BENCHMARK_PORTFOLIO_BOUNDARY_FILE = "papers/roadmap_representative_benchmark_portfolio_boundary.json"
ROADMAP_BENCHMARK_PORTFOLIO_READINESS_BOUNDARY_FILE = "papers/roadmap_benchmark_portfolio_readiness_boundary.json"
ROADMAP_PLUGIN_EXTENSIBILITY_BOUNDARY_FILE = "papers/roadmap_plugin_extensibility_boundary.json"
ROADMAP_PLUGIN_READINESS_BOUNDARY_FILE = "papers/roadmap_plugin_readiness_boundary.json"
ROADMAP_BACKEND_SCHEDULING_CRITIQUE_BOUNDARY_FILE = "papers/roadmap_backend_scheduling_critique_boundary.json"
ROADMAP_BACKEND_CONTROL_PLANE_READINESS_BOUNDARY_FILE = "papers/roadmap_backend_control_plane_readiness_boundary.json"
ROADMAP_ASYNC_RESUMABLE_RUNTIME_BOUNDARY_FILE = "papers/roadmap_async_resumable_runtime_boundary.json"
ROADMAP_ASYNC_RUNTIME_READINESS_BOUNDARY_FILE = "papers/roadmap_async_runtime_readiness_boundary.json"
ROADMAP_PROMPT_CONTEXT_SYSTEM_BOUNDARY_FILE = "papers/roadmap_prompt_context_system_boundary.json"
ROADMAP_EVALUATION_CASCADE_BOUNDARY_FILE = "papers/roadmap_evaluation_cascade_boundary.json"
ROADMAP_CANDIDATE_WORKSPACE_FIDELITY_BOUNDARY_FILE = "papers/roadmap_candidate_workspace_fidelity_boundary.json"
ROADMAP_MULTI_OBJECTIVE_SEARCH_BOUNDARY_FILE = "papers/roadmap_multi_objective_search_boundary.json"
IMPLEMENTATION_EVIDENCE_MAP_BOUNDARY_FILE = "papers/implementation_evidence_map_boundary.json"
BENCHMARK_COVERAGE_INVENTORY_FILE = "papers/benchmark_coverage_inventory.json"
STATUS_CLAIM_INVENTORY_FILE = "papers/status_claim_inventory.json"
RELEASE_ARTIFACT_REPRODUCIBILITY_BOUNDARY_FILE = "papers/release_artifact_reproducibility_boundary.json"
RELATED_WORK_TAXONOMY_BOUNDARY_FILE = "papers/related_work_taxonomy_boundary.json"
TASK_SPECIFICATION_BOUNDARY_FILE = "papers/task_specification_boundary.json"
NATURAL_LANGUAGE_PREAMBLE_BOUNDARY_FILE = "papers/natural_language_preamble_boundary.json"
PROMPT_EXAMPLE_COPY_BOUNDARY_FILE = "papers/prompt_example_copy_boundary.json"
MUTATION_CONSISTENCY_BOUNDARY_FILE = "papers/mutation_consistency_boundary.json"
MUTATION_OPERATOR_BOUNDARY_FILE = "papers/mutation_operator_boundary.json"
ADAPTIVE_MUTATION_MODE_BOUNDARY_FILE = "papers/adaptive_mutation_mode_boundary.json"
INITIAL_POOL_DIVERGENCE_BOUNDARY_FILE = "papers/initial_pool_divergence_boundary.json"
DUPLICATE_WORK_POLICY_BOUNDARY_FILE = "papers/duplicate_work_policy_boundary.json"
EXISTING_CODEBASE_INTEGRATION_BOUNDARY_FILE = "papers/existing_codebase_integration_boundary.json"
CANDIDATE_ABSTRACTION_BOUNDARY_FILE = "papers/candidate_abstraction_boundary.json"
CANDIDATE_ABSTRACTION_BIAS_MATRIX_FILE = "papers/candidate_abstraction_bias_matrix.json"
CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_FILE = "papers/candidate_language_runner_boundary.json"
CI_WORKFLOW_COVERAGE_BOUNDARY_FILE = "papers/ci_workflow_coverage_boundary.json"
CONFIG_VALIDATION_BOUNDARY_FILE = "papers/config_validation_boundary.json"
EVALUATOR_ORACLE_BOUNDARY_FILE = "papers/evaluator_oracle_boundary.json"
AUTOMATED_EVALUATOR_SCOPE_BOUNDARY_FILE = "papers/automated_evaluator_scope_boundary.json"
EMBEDDED_EVALUATOR_BOUNDARY_FILE = "papers/embedded_evaluator_boundary.json"
FIGURE3_SUPERVISED_EXHIBIT_BOUNDARY_FILE = "papers/figure3_supervised_exhibit_boundary.json"
FIGURE6_SCHEDULING_EXHIBIT_BOUNDARY_FILE = "papers/figure6_scheduling_exhibit_boundary.json"
FIGURE7_PALLAS_TILING_EXHIBIT_BOUNDARY_FILE = "papers/figure7_pallas_tiling_exhibit_boundary.json"
PROCESS_EXHIBIT_BOUNDARY_FILE = "papers/process_exhibit_boundary.json"
PROPOSAL_LIFECYCLE_AUDIT_BOUNDARY_FILE = "papers/proposal_lifecycle_audit_boundary.json"
INCORRECT_SUGGESTION_AUDIT_BOUNDARY_FILE = "papers/incorrect_suggestion_audit_boundary.json"
REPEATED_SAMPLING_BASELINE_BOUNDARY_FILE = "papers/repeated_sampling_baseline_boundary.json"
SAMPLING_BALANCE_BOUNDARY_FILE = "papers/sampling_balance_boundary.json"
SAMPLE_EFFICIENCY_BOUNDARY_FILE = "papers/sample_efficiency_boundary.json"
PARALLEL_EVALUATION_READINESS_BOUNDARY_FILE = "papers/parallel_evaluation_readiness_boundary.json"
EXPENSIVE_EVALUATION_BUDGET_BOUNDARY_FILE = "papers/expensive_evaluation_budget_boundary.json"
DISTRIBUTED_PIPELINE_TOPOLOGY_BOUNDARY_FILE = "papers/distributed_pipeline_topology_boundary.json"
WORKSPACE_MATERIALIZATION_BOUNDARY_FILE = "papers/workspace_materialization_boundary.json"
WHOLE_RUN_SOURCE_WORKSPACE_INTEGRITY_BOUNDARY_FILE = "papers/whole_run_source_workspace_integrity_boundary.json"
CODEBASE_SCALE_BENCHMARK_BOUNDARY_FILE = "papers/codebase_scale_benchmark_boundary.json"
SORTING_NETWORK_REDISCOVERY_BOUNDARY_FILE = "papers/sorting_network_rediscovery_boundary.json"
TABLE1_CAPABILITY_EXHIBIT_BOUNDARY_FILE = "papers/table1_capability_exhibit_boundary.json"
SELF_IMPROVEMENT_DISTILLATION_BOUNDARY_FILE = "papers/self_improvement_distillation_boundary.json"
SELF_IMPROVEMENT_CADENCE_BOUNDARY_FILE = "papers/self_improvement_cadence_boundary.json"
EVALUATION_CASCADE_BOUNDARY_FILE = "papers/evaluation_cascade_boundary.json"
CASCADE_HYPOTHESIS_TEST_BOUNDARY_FILE = "papers/cascade_hypothesis_test_boundary.json"
CONTROLLER_BACKTRACKING_BOUNDARY_FILE = "papers/controller_backtracking_boundary.json"
MATRIX_HEADLINE_HISTORICITY_ARTIFACTS_FILE = "papers/matrix_headline_historicity_artifacts.json"
APPENDIX_A_BASELINE_CITATIONS_FILE = "papers/appendix_a_matrix_baseline_citations.json"
MATRIX_BASELINE_COMPONENT_RUNTIME_FILE = "papers/matrix_baseline_component_runtime_boundary.json"
MATRIX_CASCADE_RUN_RUNTIME_FILE = "papers/matrix_cascade_run_runtime_boundary.json"
MATRIX_NEAR_INTEGRALITY_RUNTIME_FILE = "papers/matrix_near_integrality_runtime_boundary.json"
MATRIX_SCALAR_FIELD_RUNTIME_FILE = "papers/matrix_scalar_field_runtime_boundary.json"
MATRIX_SWEEP_SPACE_RUNTIME_FILE = "papers/matrix_sweep_space_runtime_boundary.json"
MATRIX_TENSOR_RANK_RUNTIME_FILE = "papers/matrix_tensor_rank_runtime_boundary.json"
MAP_ELITES_ILLUMINATION_BOUNDARY_FILE = "papers/map_elites_illumination_boundary.json"
MAP_ELITES_DESCRIPTOR_BOUNDARY_FILE = "papers/map_elites_descriptor_boundary.json"
OBJECTIVE_ARCHIVE_BOUNDARY_FILE = "papers/objective_archive_boundary.json"
ARCHIVE_EVENT_REPLAY_BOUNDARY_FILE = "papers/archive_event_replay_boundary.json"
CONTROLLER_PENDING_WORK_RESUME_BOUNDARY_FILE = "papers/controller_pending_work_resume_boundary.json"
LINEAGE_REPLAY_BOUNDARY_FILE = "papers/lineage_replay_boundary.json"
RUNTIME_RNG_REPLAY_BOUNDARY_FILE = "papers/runtime_rng_replay_boundary.json"
VALIDATOR_EXECUTION_BOUNDARY_FILE = "papers/validator_execution_boundary.json"
VALIDATOR_ARTIFACT_PROMOTION_BOUNDARY_FILE = "papers/validator_artifact_promotion_boundary.json"
METRIC_DIVERSE_PROMPT_BOUNDARY_FILE = "papers/metric_diverse_prompt_boundary.json"
PROPOSAL_SCORE_BOUNDARY_FILE = "papers/proposal_score_boundary.json"
PROPOSAL_DIVERSITY_BOUNDARY_FILE = "papers/proposal_diversity_boundary.json"
FAILURE_MEMORY_BOUNDARY_FILE = "papers/failure_memory_boundary.json"
PROGRAM_OUTPUT_BOUNDARY_FILE = "papers/program_output_boundary.json"
ARTIFACT_INDEX_BOUNDARY_FILE = "papers/artifact_index_boundary.json"
GEMINI_PROVIDER_PARITY_BOUNDARY_FILE = "papers/gemini_provider_parity_boundary.json"
GEMINI_SELF_TRAINING_LOOP_BOUNDARY_FILE = "papers/gemini_self_training_loop_boundary.json"
HARDWARE_RTL_EDA_EVIDENCE_BOUNDARY_FILE = "papers/hardware_rtl_eda_evidence_boundary.json"
HARDWARE_REWRITE_ARTIFACT_BOUNDARY_FILE = "papers/hardware_rewrite_artifact_boundary.json"
HARDWARE_CONTRIBUTION_ATTRIBUTION_BOUNDARY_FILE = "papers/hardware_contribution_attribution_boundary.json"
COMPILER_IR_REFERENCE_CHECK_BOUNDARY_FILE = "papers/compiler_ir_reference_check_boundary.json"
COMPILER_ADOPTION_PATH_BOUNDARY_FILE = "papers/compiler_adoption_path_boundary.json"
COMPILER_STACK_CONTEXT_BOUNDARY_FILE = "papers/compiler_stack_context_boundary.json"
GIGAEVO_FRAMEWORK_BOUNDARY_FILE = "papers/gigaevo_framework_boundary.json"
KERNEL_TILING_SHAPE_CORPUS_BOUNDARY_FILE = "papers/kernel_tiling_shape_corpus_boundary.json"
PALLAS_WORKFLOW_BASELINE_BOUNDARY_FILE = "papers/pallas_workflow_baseline_boundary.json"
CODEEVOLVE_BOUNDARY_FILE = "papers/codeevolve_boundary.json"
THETAEVOLVE_BOUNDARY_FILE = "papers/thetaevolve_boundary.json"
TTT_DISCOVER_BOUNDARY_FILE = "papers/ttt_discover_boundary.json"
IMPROVEVOLVE_BOUNDARY_FILE = "papers/improvevolve_boundary.json"
MADEVOLVE_BOUNDARY_FILE = "papers/madevolve_boundary.json"
CAUSALEVOLVE_BOUNDARY_FILE = "papers/causalevolve_boundary.json"
DEEPEVOLVE_BOUNDARY_FILE = "papers/deepevolve_boundary.json"
MAGELLAN_BOUNDARY_FILE = "papers/magellan_boundary.json"
ARCHAGENT_BOUNDARY_FILE = "papers/archagent_boundary.json"
MULTIAGENT_LEARNING_BOUNDARY_FILE = "papers/multiagent_learning_boundary.json"
RAMSEY_NUMBERS_BOUNDARY_FILE = "papers/ramsey_numbers_boundary.json"
COMBINATORICS_BERCZY_BOUNDARY_FILE = "papers/combinatorics_berczy_boundary.json"
BRUHAT_INTERVALS_BOUNDARY_FILE = "papers/bruhat_intervals_boundary.json"
FAULT2FLOW_BOUNDARY_FILE = "papers/fault2flow_boundary.json"
GLOBAL_NLP_OPTIMIZATION_BOUNDARY_FILE = "papers/global_nlp_optimization_boundary.json"
AUTOCONVOLUTION_BOUNDARY_FILE = "papers/autoconvolution_boundary.json"
SUMS_DIFFERENCES_BOUNDARY_FILE = "papers/sums_differences_boundary.json"
SUMS_DIFFERENCES_SEQUENCE_BOUNDARY_FILE = "papers/sums_differences_sequence_boundary.json"
UCB1_BOUNDARY_FILE = "papers/ucb1_boundary.json"
ALPHAEVOLVE_2026_IMPACT_BOUNDARY_FILE = EXPECTED_IMPACT_BOUNDARY_FILE
BILATERAL_TRADE_BOUNDARY_FILE = "papers/bilateral_trade_boundary.json"
EXAMPLE_BENCHMARK_SCOPE_FILE = "papers/example_benchmark_scope.json"
MATH_OUTCOME_BOUNDARY_FILE = "papers/math_outcome_boundary.json"
MATH_STARTING_CONSTRUCTION_BOUNDARY_FILE = "papers/math_starting_construction_boundary.json"
MATH_HEURISTIC_HANDOFF_BOUNDARY_FILE = "papers/math_heuristic_handoff_boundary.json"
MATH_HEURISTIC_STAGE_SEQUENCE_BOUNDARY_FILE = "papers/math_heuristic_stage_sequence_boundary.json"
PAPER_ARTIFACT_ROLES_FILE = "papers/paper_artifact_roles.json"
PAPER_ARTIFACT_LINKAGE_FILE = "papers/paper_artifact_linkage.json"
SHA256_RE = re.compile(r"[0-9a-f]{64}")
ALLOWED_TRACKED_PAPER_PDFS = {
    (
        "2506.13131",
        "papers/2506.13131__AlphaEvolve.pdf",
        "f092c8cbd65da89951ee6496374da9a54963f9035758c25ac6e4625f506df9ad",
    )
}
PAPER_ID_RE = re.compile(r"(?:\d{4}\.\d{5}|[a-z0-9][a-z0-9-]{0,94}[a-z0-9])")
ARXIV_ID_RE = re.compile(r"\d{4}\.\d{5}(?:v\d+)?")
PAPER_FILE_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,159}\.pdf")
README_BADGE_RE = re.compile(r"local%20paper%20cache-([A-Za-z0-9]+)(?=-|[?\"'>\s])")
README_COUNT_RE = re.compile(
    r"\b(?:cache of|contains)\s+(\d+)\s+"
    r"(?:papers|(?:locally\s+cached\s+)?pdfs?)\b",
    flags=re.IGNORECASE,
)
LOCAL_PAPER_CACHE_SECTION_RE = re.compile(
    r"<summary><h2>Local Paper Cache\b.*?</details>",
    flags=re.IGNORECASE | re.DOTALL,
)
TODO_COVERAGE_PATH_RE = re.compile(r"`(docs/todo/(?:Completed/)?[A-Za-z0-9_.-]+\.md)`")
COMPLETED_TODO_ITEM_RE = re.compile(r"(?m)^- \[x\] ")
ACTIVE_TODO_GAP_CONTEXT_RE = re.compile(r"(?m)^  - (?:Current gap|Remaining gap|Current evidence):")
ACTIVE_TODO_REQUIRED_RESULT_RE = re.compile(r"(?m)^  - Required result:")
BENCHMARK_IMPLEMENTED_NOT_IMPLEMENTED_RE = re.compile(r"\bnot implemented\b", flags=re.IGNORECASE)
BENCHMARK_IMPLEMENTED_LIMITATION_BOUNDARY_RE = re.compile(
    r"\b(?:but|still|not|no|without|lacks?|missing|remain(?:s)? open|out of scope|smoke-only)\b",
    flags=re.IGNORECASE,
)
LOCAL_ARTIFACT_PATH_RE = re.compile(
    r"`(?:libreevolve/|tests/|README\.md|ROADMAP\.md|papers/|docs/)[^`]+`"
)
BENCHMARK_IMPLEMENTED_LOCAL_ARTIFACT_RE = LOCAL_ARTIFACT_PATH_RE
SOURCE_SPECIFIC_ABSENCE_RE = re.compile(
    r"\bno\s+source-specific\s+([A-Za-z/]+)\s+TODO\b",
    flags=re.IGNORECASE,
)
JSON_DUPLICATE_KEYS_FIELD = "__libreevolve_duplicate_keys__"
MAX_TITLE_CHARS = 240
MAX_DOWNLOAD_MESSAGE_CHARS = 512
PDF_HASH_CHUNK_SIZE = 1024 * 1024
PAPER_DOWNLOAD_CHUNK_SIZE = 1024 * 1024
PAPER_DOWNLOAD_TIMEOUT_SECONDS = 60.0
PAPER_DOWNLOAD_USER_AGENT = "LibreEvolve paper-cache rehydrate/0.1"
ALLOWED_PAPER_URL_HOSTS = frozenset(
    {
        "arxiv.org",
        "www.arxiv.org",
        "web.engr.oregonstate.edu",
    }
)
WINDOWS_RESERVED_NAMES = frozenset(
    {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{index}" for index in range(1, 10)),
        *(f"LPT{index}" for index in range(1, 10)),
    }
)
ACTIVE_TODO_LEDGER_PATHS = (
    "docs/todo/code.md",
    "docs/todo/papers.md",
    "docs/todo/roadmap.md",
    "docs/todo/readme.md",
)
SOURCE_SPECIFIC_TODO_TARGET_PATHS = {
    "code": "docs/todo/code.md",
    "paper": "docs/todo/papers.md",
    "papers": "docs/todo/papers.md",
    "roadmap": "docs/todo/roadmap.md",
    "readme": "docs/todo/readme.md",
}
STATUS_TABLE_HEADER = ("ID", "Title", "Role", "Current LibreEvolve status")
ALLOWED_STATUS_TABLE_ROLES = frozenset(
    {
        "Agentic code-evolution inspiration",
        "AlphaEvolve MARL algorithm-discovery result context",
        "AlphaEvolve compiler-optimization application context",
        "AlphaEvolve complexity-theory result context",
        "AlphaEvolve computer-architecture application context",
        "AlphaEvolve HCI/user-study context",
        "AlphaEvolve healthy-evolution oversight context",
        "AlphaEvolve mechanism-design result context",
        "AlphaEvolve radar/resource-allocation application context",
        "AlphaEvolve-optimized workflow application context",
        "Agent harness-plus-weight self-improvement context",
        "Agentic harness observability context",
        "AI harness runtime-substrate context",
        "Adaptive auto-harness deployment context",
        "Asynchronous-stage orchestration context",
        "Autonomous multi-agent evolution context",
        "Causal-guidance inspiration",
        "Constructive math benchmark candidate",
        "Context-memory framework context",
        "Cost-aware search-architecture context",
        "Domain evolution inspiration",
        "Foundational archive algorithm",
        "Foundational bandit policy",
        "Framework inspiration",
        "Harnessed meta-editing context",
        "Harness-capability disentanglement context",
        "Inference-time trajectory-alignment context",
        "Learning-signal optimization context",
        "Long-horizon MLE framework context",
        "Long-horizon consistency framework context",
        "Memory-architecture evolution context",
        "Meta-evolution framework context",
        "Modular search inspiration",
        "Multimodal trajectory-distillation context",
        "Optimization benchmark comparator",
        "Outer-loop harness-code optimization context",
        "Primary specification target",
        "Retrieval/debug loop inspiration",
        "Retrospective harness optimization context",
        "Self-evolving reward-rubric context",
        "Test-time discovery context",
        "Test-time training inspiration",
        "Trace-diagnostic evaluation context",
        "Trace-grounded harness repair context",
        "Verifier-free co-evolution context",
    }
)
ALLOWED_STATUS_TABLE_STATUS_PREFIXES = (
    "Background only",
    "Implemented as ",
    "Not implemented as described:",
    "Not implemented; potential future benchmark",
    "Only ",
    "Partially implemented:",
    "Static prompt guidance exists ",
)
STATUS_TABLE_ROLE_STATUS_PREFIXES = {
    "Agentic code-evolution inspiration": ("Not implemented as described:",),
    "AlphaEvolve MARL algorithm-discovery result context": ("Background only",),
    "AlphaEvolve compiler-optimization application context": ("Background only",),
    "AlphaEvolve complexity-theory result context": ("Background only",),
    "AlphaEvolve computer-architecture application context": ("Background only",),
    "AlphaEvolve HCI/user-study context": ("Background only",),
    "AlphaEvolve healthy-evolution oversight context": ("Background only",),
    "AlphaEvolve mechanism-design result context": ("Background only",),
    "AlphaEvolve radar/resource-allocation application context": ("Background only",),
    "AlphaEvolve-optimized workflow application context": ("Background only",),
    "Agent harness-plus-weight self-improvement context": ("Background only",),
    "Agentic harness observability context": ("Background only",),
    "AI harness runtime-substrate context": ("Background only",),
    "Adaptive auto-harness deployment context": ("Background only",),
    "Asynchronous-stage orchestration context": ("Background only",),
    "Autonomous multi-agent evolution context": ("Background only",),
    "Causal-guidance inspiration": ("Only ",),
    "Constructive math benchmark candidate": ("Not implemented; potential future benchmark",),
    "Context-memory framework context": ("Background only",),
    "Cost-aware search-architecture context": ("Background only",),
    "Domain evolution inspiration": ("Background only",),
    "Foundational archive algorithm": ("Implemented as ",),
    "Foundational bandit policy": ("Implemented as ",),
    "Framework inspiration": ("Not implemented as described:",),
    "Harnessed meta-editing context": ("Background only",),
    "Harness-capability disentanglement context": ("Background only",),
    "Inference-time trajectory-alignment context": ("Background only",),
    "Learning-signal optimization context": ("Background only",),
    "Long-horizon MLE framework context": ("Background only",),
    "Long-horizon consistency framework context": ("Background only",),
    "Memory-architecture evolution context": ("Background only",),
    "Meta-evolution framework context": ("Background only",),
    "Modular search inspiration": ("Static prompt guidance exists ",),
    "Multimodal trajectory-distillation context": ("Background only",),
    "Optimization benchmark comparator": ("Not implemented; potential future benchmark",),
    "Outer-loop harness-code optimization context": ("Background only",),
    "Primary specification target": ("Partially implemented:",),
    "Retrieval/debug loop inspiration": ("Only ",),
    "Retrospective harness optimization context": ("Background only",),
    "Self-evolving reward-rubric context": ("Background only",),
    "Test-time discovery context": ("Background only",),
    "Test-time training inspiration": ("Only ",),
    "Trace-diagnostic evaluation context": ("Background only",),
    "Trace-grounded harness repair context": ("Background only",),
    "Verifier-free co-evolution context": ("Background only",),
}
STATUS_TABLE_STATUSES_REQUIRING_COMPLETED_EVIDENCE = (
    "Implemented as ",
    "Only ",
    "Partially implemented:",
    "Static prompt guidance exists ",
)
STATUS_TABLE_ALPHAEVOLVE_COMPARABLE_RE = re.compile(r"\bAlphaEvolve-comparable\b", flags=re.IGNORECASE)
STATUS_TABLE_ALPHAEVOLVE_COMPARABLE_BOUNDARY_RE = re.compile(
    r"\b(?:not|no|without|before claiming|requires?|remain(?:s)? open|missing|lacks?)\b"
    r"[^.]{0,160}\bAlphaEvolve-comparable\b"
    r"|\bAlphaEvolve-comparable\b[^.]{0,160}"
    r"\b(?:not|no|without|requires?|remain(?:s)? open|missing|lacks?)\b",
    flags=re.IGNORECASE,
)
STATUS_TABLE_NEGATIVE_IMPLEMENTATION_PREFIXES = (
    "Background only",
    "Not implemented; potential future benchmark",
)
STATUS_TABLE_BACKGROUND_ONLY_PREFIXES = ("Background only",)
STATUS_TABLE_FUTURE_BENCHMARK_PREFIXES = ("Not implemented; potential future benchmark",)
STATUS_TABLE_IMPLEMENTED_STATUS_PREFIXES = ("Implemented as ",)
STATUS_TABLE_LIMITED_STATUS_PREFIXES = ("Only ",)
STATUS_TABLE_PARTIAL_STATUS_PREFIXES = ("Partially implemented:",)
STATUS_TABLE_LIMITATION_BOUNDARY_RE = re.compile(
    r"\b(?:no|not|without|but|while|lacks?|missing|remain(?:s)? open|out of scope|unsupported)\b",
    flags=re.IGNORECASE,
)
STATUS_TABLE_STATIC_GUIDANCE_PREFIXES = ("Static prompt guidance exists ",)
STATUS_TABLE_STATIC_GUIDANCE_EXECUTION_BOUNDARY_RE = re.compile(
    r"\bfalse\s+execution/enforcement\b"
    r"|\b(?:no|not|without)\b[^.]{0,160}"
    r"\b(?:executed|execution|enforced|enforcement)\b",
    flags=re.IGNORECASE,
)
STATUS_TABLE_POSITIVE_IMPLEMENTATION_RE = re.compile(
    r"\b(?:implemented\s+(?:as|local|smoke|support)|implementation\s+exists|"
    r"support\s+exists|is\s+implemented|are\s+implemented|now\s+supports|supports)\b",
    flags=re.IGNORECASE,
)
STATUS_TABLE_NOT_IMPLEMENTED_AS_DESCRIBED_PREFIXES = ("Not implemented as described:",)
STATUS_CLAIM_INVENTORY_SCHEMA = "libreevolve.paper_index_status_claim_inventory.v1"
STATUS_LEDGER_FILE = "docs/status.md"
STATUS_CLAIM_INVENTORY_STATUS = "phrase_evidence_link_inventory_without_semantic_verifier"
STATUS_CLAIM_INVENTORY_MISSING_EVIDENCE = {
    "status_cell_semantic_verifier": "not_recorded_locally",
    "implemented_benchmark_bullet_semantic_verifier": "not_recorded_locally",
    "absence_sentence_freshness_matrix": "not_recorded_locally",
}
STATUS_CLAIM_INVENTORY_README_SUMMARY_PATTERNS = (
    (
        "unique_local_artifact_count",
        re.compile(r"`?(\d+)`?\s+unique referenced local artifact paths"),
    ),
    (
        "local_artifact_mention_record_count",
        re.compile(r"`?(\d+)`?\s+row-level artifact mention records"),
    ),
    (
        "phrase_local_artifact_mention_record_count",
        re.compile(r"`?(\d+)`?\s+phrase-level artifact mention records"),
    ),
    (
        "unique_todo_evidence_path_count",
        re.compile(r"`?(\d+)`?\s+unique referenced TODO evidence paths"),
    ),
    (
        "todo_evidence_path_mention_count",
        re.compile(r"`?(\d+)`?\s+TODO evidence path mention records"),
    ),
    (
        "todo_content_matched_source_token_count",
        re.compile(r"`?(\d+)`?\s+matched TODO content source tokens"),
    ),
    (
        "todo_content_row_specific_block_record_count",
        re.compile(r"`?(\d+)`?\s+row-specific TODO block hashes/source offsets"),
    ),
    (
        "todo_content_artifact_mention_record_count",
        re.compile(r"`?(\d+)`?\s+TODO content artifact mention source-offset records"),
    ),
    (
        "phrase_todo_content_block_record_count",
        re.compile(r"`?(\d+)`?\s+phrase-level TODO block records"),
    ),
    (
        "absence_phrase_count",
        re.compile(r"`?(\d+)`?\s+status-cell absence-signal phrases"),
    ),
    (
        "absence_signal_record_count",
        re.compile(
            r"status-cell\s+absence-signal phrases with\s+`?(\d+)`?\s+source-offset records"
        ),
    ),
)
STATUS_ABSENCE_SIGNAL_RE = re.compile(
    r"\b(?:no|not|without|missing|lacks?|absence|absent|unimplemented|unsupported)\b"
    r"|\bnot\s+implemented\b|\bnot\s+yet\b|\bout\s+of\s+scope\b|\bremain(?:s)?\s+open\b",
    flags=re.IGNORECASE,
)
BENCHMARK_COVERAGE_INVENTORY_SCHEMA = "libreevolve.paper_index_benchmark_coverage_inventory.v1"
BENCHMARK_COVERAGE_INVENTORY_STATUS = "implemented_bullet_inventory_without_semantic_verifier"
BENCHMARK_COVERAGE_MISSING_EVIDENCE = {
    "benchmark_bullet_semantic_verifier": "not_recorded_locally",
    "benchmark_bullet_freshness_matrix": "not_recorded_locally",
    "benchmark_result_reproduction_links": "not_recorded_locally",
}
BENCHMARK_COVERAGE_README_SUMMARY_PATTERNS = (
    (
        "source_id_mention_count",
        re.compile(r"`?(\d+)`?\s+referenced manifest source IDs"),
    ),
    (
        "source_token_match_record_count",
        re.compile(r"across\s+`?(\d+)`?\s+source-token match records"),
    ),
    (
        "unique_local_artifact_count",
        re.compile(r"`?(\d+)`?\s+unique referenced local artifact paths"),
    ),
    (
        "missing_local_artifact_path_count",
        re.compile(r"(zero|`?\d+`?)\s+missing referenced local artifacts", flags=re.IGNORECASE),
    ),
)


@dataclass(frozen=True)
class PaperManifestIssue:
    code: str
    message: str
    row_id: str | None = None


@dataclass(frozen=True)
class ReadmeCountSource:
    source: str
    kind: str
    value: int
    phrase: str


@dataclass(frozen=True)
class PaperAvailability:
    row_id: str
    file: str
    download_ok: bool
    download_message: str
    local_status: str
    git_tracked: bool | None


@dataclass(frozen=True)
class PaperManifestReport:
    ok: bool
    row_count: int
    local_present_count: int
    local_missing_count: int
    local_unique_file_count: int
    availability: list[PaperAvailability]
    issues: list[PaperManifestIssue]


@dataclass(frozen=True)
class PaperRehydrateResult:
    row_id: str
    file: str
    status: str
    bytes: int | None
    sha256: str | None
    message: str


@dataclass(frozen=True)
class PaperRehydrateReport:
    ok: bool
    row_count: int
    verified_existing_count: int
    downloaded_count: int
    failed_count: int
    results: list[PaperRehydrateResult]
    issues: list[PaperManifestIssue]


def validate_paper_manifest(
    root: str | Path = ".",
    *,
    require_local_pdfs: bool = False,
) -> PaperManifestReport:
    root_path = Path(root)
    json_rows, issues = _load_json_manifest(root_path / "papers" / "download_manifest.json", root_path)
    csv_rows, csv_issues = _load_csv_manifest(root_path / "papers" / "download_manifest.csv", root_path)
    issues.extend(csv_issues)

    if len(json_rows) != len(csv_rows):
        issues.append(
            PaperManifestIssue(
                "manifest_count_mismatch",
                f"JSON has {len(json_rows)} rows but CSV has {len(csv_rows)} rows",
            )
        )

    csv_by_id: dict[str, dict[str, Any]] = {}
    for row in csv_rows:
        row_id = str(row.get("id", ""))
        if row_id in csv_by_id:
            issues.append(
                PaperManifestIssue(
                    "duplicate_csv_id",
                    "duplicate CSV paper id",
                    _safe_manifest_label(row_id),
                )
            )
            continue
        csv_by_id[row_id] = row
    git_tracked_files = _git_tracked_files(root_path)
    seen_ids: set[str] = set()
    seen_files: dict[str, str] = {}
    seen_sha256: dict[str, str] = {}
    manifest_file_keys: set[str] = set()
    present_file_keys: set[str] = set()
    local_present_count = 0
    local_missing_count = 0
    availability: list[PaperAvailability] = []

    for index, row in enumerate(json_rows):
        row_id = str(row.get("id", f"row-{index}"))
        row_label = _safe_manifest_label(row_id)
        issues.extend(_validate_row_schema(row, row_label))
        if row_id in seen_ids:
            issues.append(PaperManifestIssue("duplicate_id", "duplicate paper id", row_label))
        seen_ids.add(row_id)

        csv_row = csv_by_id.get(row_id)
        if csv_row is None:
            issues.append(PaperManifestIssue("missing_csv_row", "missing matching CSV row", row_label))
        elif _canonical_row(row) != _canonical_row(csv_row):
            issues.append(PaperManifestIssue("csv_json_mismatch", "CSV row does not match JSON row", row_label))

        sha256 = row.get("sha256")
        if not isinstance(sha256, str) or SHA256_RE.fullmatch(sha256) is None:
            issues.append(
                PaperManifestIssue(
                    "invalid_sha256",
                    "sha256 must be a canonical lowercase 64-hex digest",
                    row_label,
                )
            )
        elif sha256 in seen_sha256:
            issues.append(
                PaperManifestIssue(
                    "duplicate_sha256",
                    f"sha256 also appears in row {seen_sha256[sha256]}",
                    row_label,
                )
            )
        else:
            seen_sha256[sha256] = row_label

        file_value = row.get("file")
        if isinstance(file_value, str):
            paper_path = root_path / file_value
            if not _is_safe_paper_path(file_value):
                issues.append(
                    PaperManifestIssue(
                        "invalid_file_path",
                        "file must be a safe papers/<name>.pdf path",
                        row_label,
                    )
                )
            elif (file_key := _normalized_paper_file_key(file_value)) in seen_files:
                manifest_file_keys.add(file_key)
                issues.append(
                    PaperManifestIssue(
                        "duplicate_file_path",
                        f"file path also appears in row {seen_files[file_key]}",
                        row_label,
                    )
                )
            elif paper_path.exists():
                seen_files[file_key] = row_label
                manifest_file_keys.add(file_key)
                present_file_keys.add(file_key)
                local_present_count += 1
                availability_record = _availability(row, file_value, "present", git_tracked_files)
                availability.append(availability_record)
                if (
                    availability_record.git_tracked is True
                    and not _is_allowed_tracked_paper_pdf(row, file_value)
                ):
                    issues.append(
                        PaperManifestIssue(
                            "tracked_pdf",
                            f"{file_value}: local paper PDFs must stay untracked",
                            row_label,
                        )
                    )
                issues.extend(_validate_local_pdf(row, paper_path, row_label))
            else:
                seen_files[file_key] = row_label
                manifest_file_keys.add(file_key)
                local_missing_count += 1
                availability.append(
                    _availability(row, file_value, "missing", git_tracked_files)
                )
                if require_local_pdfs:
                    issues.append(PaperManifestIssue("missing_pdf", f"missing local PDF {file_value}", row_label))

        if row.get("ok") is False:
            issues.append(PaperManifestIssue("download_failed", "manifest row records a failed download", row_label))

    if require_local_pdfs:
        for file_value in sorted(_local_pdf_files(root_path)):
            if _normalized_paper_file_key(file_value) not in manifest_file_keys:
                issues.append(
                    PaperManifestIssue(
                        "unmanifested_pdf",
                        f"local PDF {file_value} is not listed in the manifests",
                    )
                )

    issues.extend(_validate_appendix_a_matrix_registry_if_present(root_path))
    issues.extend(_validate_appendix_b_registry_if_present(root_path))
    issues.extend(_validate_ablation_registry_if_present(root_path))
    issues.extend(_validate_alphaevolve_arxiv_abstract_snapshot(root_path))
    issues.extend(_validate_alphaevolve_current_version_boundary(root_path))
    issues.extend(_validate_alphaevolve_cached_pdf_header_consistency_boundary(root_path))
    issues.extend(_validate_alphaevolve_metadata_extraction_script_boundary(root_path))
    issues.extend(_validate_alphaevolve_source_refresh_gate_boundary(root_path))
    issues.extend(_validate_alphaevolve_source_refresh_run_boundary(root_path))
    issues.extend(_validate_alphaevolve_source_refresh_promotion_boundary(root_path))
    issues.extend(_validate_alphaevolve_raw_http_headers_boundary(root_path))
    issues.extend(_validate_alphaevolve_datacite_doi_boundary(root_path))
    issues.extend(_validate_alphaevolve_datacite_full_response_boundary(root_path))
    issues.extend(_validate_alphaevolve_doi_landing_resolution_boundary(root_path))
    issues.extend(_validate_alphaevolve_tex_source_boundary(root_path))
    issues.extend(_validate_alphaevolve_tex_archive_retention_boundary(root_path))
    issues.extend(_validate_alphaevolve_license_page_boundary(root_path))
    issues.extend(_validate_alphaevolve_license_page_html_retention_boundary(root_path))
    issues.extend(_validate_figure8_ablation_artifacts(root_path))
    issues.extend(_validate_benchmark_fixture_readiness_boundary(root_path))
    issues.extend(_validate_systems_result_readiness_boundary(root_path))
    issues.extend(_validate_acknowledgement_role_provenance_boundary(root_path))
    issues.extend(_validate_paper_author_metadata_boundary(root_path))
    issues.extend(_validate_title_page_affiliation_boundary(root_path))
    issues.extend(_validate_system_contribution_provenance_boundary(root_path))
    issues.extend(_validate_initial_program_idea_provenance_boundary(root_path))
    issues.extend(_validate_initial_program_seed_variant_matrix(root_path))
    issues.extend(_validate_initial_program_validity_boundary(root_path))
    issues.extend(_validate_collaborator_feedback_provenance_boundary(root_path))
    issues.extend(_validate_problem_formulation_provenance_boundary(root_path))
    issues.extend(_validate_programmatic_representation_boundary(root_path))
    issues.extend(_validate_qualitative_feedback_boundary(root_path))
    issues.extend(_validate_feedback_calibration_boundary(root_path))
    issues.extend(_validate_llm_role_scheduler_boundary(root_path))
    issues.extend(_validate_llm_budget_policy_boundary(root_path))
    issues.extend(_validate_llm_stochastic_reproducibility_boundary(root_path))
    issues.extend(_validate_fast_strong_model_mix_boundary(root_path))
    issues.extend(_validate_provider_cancellation_boundary(root_path))
    issues.extend(_validate_provider_pricing_boundary(root_path))
    issues.extend(_validate_provider_diagnostics_replay_boundary(root_path))
    issues.extend(_validate_critique_reviewer_pool_boundary(root_path))
    issues.extend(_validate_prompt_section_packing_boundary(root_path))
    issues.extend(_validate_stochastic_prompt_format_boundary(root_path))
    issues.extend(_validate_documentation_truthfulness_boundary(root_path))
    issues.extend(_validate_documentation_claim_inventory(root_path))
    issues.extend(_validate_roadmap_readiness_boundary(root_path))
    issues.extend(_validate_roadmap_claim_evidence_boundary(root_path))
    issues.extend(_validate_todo_ledger_ownership_boundary(root_path))
    issues.extend(_validate_todo_canonical_gap_boundary(root_path))
    issues.extend(_validate_roadmap_source_span_disposition_boundary(root_path))
    issues.extend(_validate_roadmap_source_span_coverage_boundary(root_path))
    issues.extend(_validate_roadmap_non_goal_contradiction_boundary(root_path))
    issues.extend(_validate_roadmap_non_goal_drift_boundary(root_path))
    issues.extend(_validate_roadmap_good_first_followups_boundary(root_path))
    issues.extend(_validate_roadmap_good_first_freshness_boundary(root_path))
    issues.extend(_validate_roadmap_phase_sequence_boundary(root_path))
    issues.extend(_validate_roadmap_phase_freshness_boundary(root_path))
    issues.extend(_validate_roadmap_operational_maturity_boundary(root_path))
    issues.extend(_validate_roadmap_operational_readiness_boundary(root_path))
    issues.extend(_validate_roadmap_representative_benchmark_portfolio_boundary(root_path))
    issues.extend(_validate_roadmap_benchmark_portfolio_readiness_boundary(root_path))
    issues.extend(_validate_roadmap_plugin_extensibility_boundary(root_path))
    issues.extend(_validate_roadmap_plugin_readiness_boundary(root_path))
    issues.extend(_validate_roadmap_backend_scheduling_critique_boundary(root_path))
    issues.extend(_validate_roadmap_backend_control_plane_readiness_boundary(root_path))
    issues.extend(_validate_roadmap_async_resumable_runtime_boundary(root_path))
    issues.extend(_validate_roadmap_async_runtime_readiness_boundary(root_path))
    issues.extend(_validate_roadmap_prompt_context_system_boundary(root_path))
    issues.extend(_validate_roadmap_evaluation_cascade_boundary(root_path))
    issues.extend(_validate_roadmap_candidate_workspace_fidelity_boundary(root_path))
    issues.extend(_validate_roadmap_multi_objective_search_boundary(root_path))
    issues.extend(_validate_implementation_evidence_map_boundary(root_path))
    issues.extend(_validate_release_artifact_reproducibility_boundary(root_path))
    issues.extend(_validate_related_work_taxonomy_boundary(root_path))
    issues.extend(_validate_task_specification_boundary(root_path))
    issues.extend(_validate_natural_language_preamble_boundary(root_path))
    issues.extend(_validate_prompt_example_copy_boundary(root_path))
    issues.extend(_validate_mutation_consistency_boundary(root_path))
    issues.extend(_validate_mutation_operator_boundary(root_path))
    issues.extend(_validate_adaptive_mutation_mode_boundary(root_path))
    issues.extend(_validate_initial_pool_divergence_boundary(root_path))
    issues.extend(_validate_duplicate_work_policy_boundary(root_path))
    issues.extend(_validate_existing_codebase_integration_boundary(root_path))
    issues.extend(_validate_candidate_language_runner_boundary(root_path))
    issues.extend(_validate_candidate_abstraction_boundary(root_path))
    issues.extend(_validate_candidate_abstraction_bias_matrix(root_path))
    issues.extend(_validate_ci_workflow_coverage_boundary(root_path))
    issues.extend(_validate_config_validation_boundary(root_path))
    issues.extend(_validate_evaluator_oracle_boundary(root_path))
    issues.extend(_validate_automated_evaluator_scope_boundary(root_path))
    issues.extend(_validate_embedded_evaluator_boundary(root_path))
    issues.extend(_validate_figure3_supervised_exhibit_boundary(root_path))
    issues.extend(_validate_figure6_scheduling_exhibit_boundary(root_path))
    issues.extend(_validate_figure7_pallas_tiling_exhibit_boundary(root_path))
    issues.extend(_validate_process_exhibit_boundary(root_path))
    issues.extend(_validate_proposal_lifecycle_audit_boundary(root_path))
    issues.extend(_validate_incorrect_suggestion_audit_boundary(root_path))
    issues.extend(_validate_repeated_sampling_baseline_boundary(root_path))
    issues.extend(_validate_sampling_balance_boundary(root_path))
    issues.extend(_validate_sample_efficiency_boundary(root_path))
    issues.extend(_validate_parallel_evaluation_readiness_boundary(root_path))
    issues.extend(_validate_expensive_evaluation_budget_boundary(root_path))
    issues.extend(_validate_distributed_pipeline_topology_boundary(root_path))
    issues.extend(_validate_workspace_materialization_boundary(root_path))
    issues.extend(_validate_whole_run_source_workspace_integrity_boundary(root_path))
    issues.extend(_validate_codebase_scale_benchmark_boundary(root_path))
    issues.extend(_validate_sorting_network_rediscovery_boundary(root_path))
    issues.extend(_validate_table1_capability_exhibit_boundary(root_path))
    issues.extend(_validate_self_improvement_distillation_boundary(root_path))
    issues.extend(_validate_self_improvement_cadence_boundary(root_path))
    issues.extend(_validate_evaluation_cascade_boundary(root_path))
    issues.extend(_validate_cascade_hypothesis_test_boundary(root_path))
    issues.extend(_validate_controller_backtracking_boundary(root_path))
    issues.extend(_validate_example_benchmark_scope_records(root_path))
    issues.extend(_validate_math_outcome_boundaries(root_path))
    issues.extend(_validate_map_elites_illumination_boundary(root_path))
    issues.extend(_validate_map_elites_descriptor_boundary(root_path))
    issues.extend(_validate_objective_archive_boundary(root_path))
    issues.extend(_validate_archive_event_replay_boundary(root_path))
    issues.extend(_validate_controller_pending_work_resume_boundary(root_path))
    issues.extend(_validate_lineage_replay_boundary(root_path))
    issues.extend(_validate_runtime_rng_replay_boundary(root_path))
    issues.extend(_validate_validator_execution_boundary(root_path))
    issues.extend(_validate_validator_artifact_promotion_boundary(root_path))
    issues.extend(_validate_metric_diverse_prompt_boundary(root_path))
    issues.extend(_validate_proposal_score_boundary(root_path))
    issues.extend(_validate_proposal_diversity_boundary(root_path))
    issues.extend(_validate_failure_memory_boundary(root_path))
    issues.extend(_validate_program_output_boundary(root_path))
    issues.extend(_validate_artifact_index_boundary(root_path))
    issues.extend(_validate_gemini_provider_parity_boundary(root_path))
    issues.extend(_validate_gemini_self_training_loop_boundary(root_path))
    issues.extend(_validate_hardware_rtl_eda_evidence_boundary(root_path))
    issues.extend(_validate_hardware_rewrite_artifact_boundary(root_path))
    issues.extend(_validate_hardware_contribution_attribution_boundary(root_path))
    issues.extend(_validate_compiler_ir_reference_check_boundary(root_path))
    issues.extend(_validate_compiler_adoption_path_boundary(root_path))
    issues.extend(_validate_compiler_stack_context_boundary(root_path))
    issues.extend(_validate_gigaevo_framework_boundary(root_path))
    issues.extend(_validate_kernel_tiling_shape_corpus_boundary(root_path))
    issues.extend(_validate_pallas_workflow_baseline_boundary(root_path))
    issues.extend(_validate_codeevolve_boundary(root_path))
    issues.extend(_validate_thetaevolve_boundary(root_path))
    issues.extend(_validate_improvevolve_boundary(root_path))
    issues.extend(_validate_madevolve_boundary(root_path))
    issues.extend(_validate_causalevolve_boundary(root_path))
    issues.extend(_validate_deepevolve_boundary(root_path))
    issues.extend(_validate_magellan_boundary(root_path))
    issues.extend(_validate_archagent_boundary(root_path))
    issues.extend(_validate_multiagent_learning_boundary(root_path))
    issues.extend(_validate_ramsey_numbers_boundary(root_path))
    issues.extend(_validate_combinatorics_berczy_boundary(root_path))
    issues.extend(_validate_ttt_discover_boundary(root_path))
    issues.extend(_validate_bruhat_intervals_boundary(root_path))
    issues.extend(_validate_fault2flow_boundary(root_path))
    issues.extend(_validate_global_nlp_optimization_boundary(root_path))
    issues.extend(_validate_autoconvolution_boundary(root_path))
    issues.extend(_validate_sums_differences_boundary(root_path))
    issues.extend(_validate_sums_differences_sequence_boundary(root_path))
    issues.extend(_validate_ucb1_boundary(root_path))
    issues.extend(_validate_alphaevolve_2026_impact_boundary(root_path))
    issues.extend(_validate_bilateral_trade_boundary(root_path))

    if set(csv_by_id) - seen_ids:
        for row_id in sorted(set(csv_by_id) - seen_ids):
            issues.append(PaperManifestIssue("extra_csv_row", "CSV row has no JSON row", _safe_manifest_label(row_id)))

    status_ids, status_issues = _read_status_table_ids(root_path)
    issues.extend(status_issues)
    if status_ids is not None:
        status_id_set = set(status_ids)
        for row_id in sorted(seen_ids - status_id_set):
            issues.append(
                PaperManifestIssue(
                    "missing_status_table_row",
                    "manifest row is missing from papers/README.md implementation status table",
                    _safe_manifest_label(row_id),
                )
            )
        for row_id in sorted(status_id_set - seen_ids):
            issues.append(
                PaperManifestIssue(
                    "extra_status_table_row",
                    "papers/README.md implementation status row has no manifest row",
                    _safe_manifest_label(row_id),
                )
            )

    expected_count, count_issues = _read_expected_count(root_path)
    issues.extend(count_issues)
    if expected_count is not None and expected_count != len(json_rows):
        issues.append(
            PaperManifestIssue(
                "documented_count_mismatch",
                f"documented paper count is {expected_count} but manifest has {len(json_rows)} rows",
            )
        )
    issues.extend(_validate_root_readme_paper_summary(root_path, seen_ids))
    manifest_rows_by_id = {str(row.get("id")): row for row in json_rows if row.get("id")}
    issues.extend(_validate_paper_source_identity_manifest(root_path, json_rows))
    issues.extend(_validate_alphaevolve_source_pdf_version_manifest(root_path, manifest_rows_by_id))
    issues.extend(_validate_alphaevolve_source_pdf_rights_manifest(root_path, manifest_rows_by_id))
    issues.extend(_validate_alphaevolve_source_pdf_version_record(root_path, manifest_rows_by_id))
    issues.extend(_validate_alphaevolve_source_pdf_rights_record(root_path, manifest_rows_by_id))
    issues.extend(_validate_alphaevolve_references_bibliography(root_path, manifest_rows_by_id, json_rows))
    issues.extend(_validate_alphaevolve_references_section_record(root_path, manifest_rows_by_id))
    issues.extend(_validate_alphaevolve_companion_source_manifest(root_path))
    issues.extend(_validate_alphaevolve_paper_artifact_role_linkage(root_path))
    issues.extend(_validate_alphaevolve_follow_on_source_manifest(root_path))
    issues.extend(_validate_alphaevolve_follow_on_repository_rights_manifest(root_path))
    issues.extend(_validate_alphaevolve_follow_on_runtime_absence_manifest(root_path))
    issues.extend(_validate_alphaevolve_follow_on_tao_blog_manifest(root_path))
    issues.extend(_validate_alphaevolve_follow_on_math_source_record(root_path, manifest_rows_by_id))
    issues.extend(_validate_alphaevolve_follow_on_problem_coverage_record())
    issues.extend(_validate_alphaevolve_theoretical_cs_source_manifest(root_path))
    issues.extend(_validate_alphaevolve_official_blog_manifest(root_path))
    issues.extend(_validate_todo_coverage_table(root_path, seen_ids, manifest_rows_by_id))
    issues.extend(_validate_status_claim_inventory(root_path))
    issues.extend(_validate_todo_absence_wording(root_path, seen_ids))
    issues.extend(_validate_benchmark_coverage_inventory(root_path))
    issues.extend(_validate_benchmark_coverage_decisions(root_path))

    return PaperManifestReport(
        ok=not issues,
        row_count=len(json_rows),
        local_present_count=local_present_count,
        local_missing_count=local_missing_count,
        local_unique_file_count=len(present_file_keys),
        availability=availability,
        issues=issues,
    )


def paper_status_claim_inventory_record(root: str | Path = ".") -> dict[str, Any]:
    """Return a row-level inventory for papers/README.md implementation status."""

    root_path = Path(root)
    manifest_rows, _manifest_issues = _load_json_manifest(
        root_path / "papers" / "download_manifest.json",
        root_path,
    )
    manifest_rows_by_id = {
        str(row.get("id")): row
        for row in manifest_rows
        if isinstance(row.get("id"), str)
    }
    status_records, _status_issues = _read_status_table_row_records(root_path)
    status_records = status_records or []
    todo_rows, _todo_issues = _read_todo_coverage_table_cells(root_path)
    inventory_rows: list[dict[str, Any]] = []
    status_class_counts: dict[str, int] = {}

    for row_ordinal, status_record in enumerate(status_records, start=1):
        cells = status_record["cells"]
        row_id, title, role, status_text = cells
        active_cell, completed_cell = todo_rows.get(row_id, ("", ""))
        active_paths = _status_claim_inventory_paths(active_cell)
        completed_paths = _status_claim_inventory_paths(completed_cell)
        active_path_mentions = _status_todo_evidence_path_mention_records(active_cell, "active")
        completed_path_mentions = _status_todo_evidence_path_mention_records(
            completed_cell,
            "completed",
        )
        active_todo_records = _local_artifact_path_records(root_path, active_paths)
        completed_todo_records = _local_artifact_path_records(root_path, completed_paths)
        manifest_row = manifest_rows_by_id.get(row_id, {})
        missing_todo_paths = [
            record["path"]
            for record in [*active_todo_records, *completed_todo_records]
            if not record["exists"]
        ]
        row_local_artifact_mention_records = _status_local_artifact_mention_records(
            status_text,
            status_record["line_number"],
        )
        row_local_artifact_paths = sorted(
            {record["path"] for record in row_local_artifact_mention_records}
        )
        active_todo_content_records = _status_todo_evidence_content_records(
            root_path,
            row_id,
            active_paths,
            manifest_row,
            row_local_artifact_paths,
            "active",
        )
        completed_todo_content_records = _status_todo_evidence_content_records(
            root_path,
            row_id,
            completed_paths,
            manifest_row,
            row_local_artifact_paths,
            "completed",
        )
        row_artifacts_mentioned_in_todo = sorted(
            {
                artifact
                for record in [*active_todo_content_records, *completed_todo_content_records]
                for artifact in record["mentioned_local_artifact_paths"]
            }
        )
        row_artifacts_missing_from_todo = sorted(
            set(row_local_artifact_paths) - set(row_artifacts_mentioned_in_todo)
        )
        row_local_artifact_records = _local_artifact_path_records(root_path, row_local_artifact_paths)
        row_missing_local_artifacts = [
            record["path"] for record in row_local_artifact_records if not record["exists"]
        ]
        status_class = _status_claim_inventory_class(status_text)
        status_class_counts[status_class] = status_class_counts.get(status_class, 0) + 1
        status_claims = _status_claim_inventory_phrases(
            root_path,
            row_id,
            status_text,
            status_record["line_number"],
            active_paths,
            completed_paths,
            active_todo_records,
            completed_todo_records,
            active_todo_content_records,
            completed_todo_content_records,
            row_local_artifact_paths,
        )
        inventory_rows.append(
            {
                "id": row_id,
                "row_ordinal": row_ordinal,
                "title": title,
                "role": role,
                "status_class": status_class,
                "status_text_sha256": hashlib.sha256(status_text.encode("utf-8")).hexdigest(),
                "source_span": {
                    "path": "papers/README.md",
                    "section": "Implementation status",
                    "line_start": status_record["line_number"],
                    "line_end": status_record["line_number"],
                },
                "manifest_file": manifest_row.get("file", ""),
                "local_artifact_paths": row_local_artifact_paths,
                "local_artifact_mention_records": row_local_artifact_mention_records,
                "local_artifact_records": row_local_artifact_records,
                "local_artifact_existing_count": (
                    len(row_local_artifact_paths) - len(row_missing_local_artifacts)
                ),
                "local_artifact_missing_paths": row_missing_local_artifacts,
                "all_local_artifacts_exist": (
                    bool(row_local_artifact_paths) and not row_missing_local_artifacts
                ),
                "active_todo_paths": active_paths,
                "completed_todo_paths": completed_paths,
                "active_todo_path_mention_records": active_path_mentions,
                "completed_todo_path_mention_records": completed_path_mentions,
                "active_todo_records": active_todo_records,
                "completed_todo_records": completed_todo_records,
                "active_todo_content_records": active_todo_content_records,
                "completed_todo_content_records": completed_todo_content_records,
                "todo_evidence_path_count": len(set(active_paths + completed_paths)),
                "todo_evidence_path_mention_count": len(active_path_mentions)
                + len(completed_path_mentions),
                "todo_evidence_missing_paths": missing_todo_paths,
                "all_todo_evidence_paths_exist": bool(active_paths or completed_paths) and not missing_todo_paths,
                "local_artifacts_mentioned_in_todo_evidence": row_artifacts_mentioned_in_todo,
                "local_artifacts_missing_from_todo_evidence": row_artifacts_missing_from_todo,
                "all_local_artifacts_linked_from_todo_evidence": (
                    bool(row_local_artifact_paths) and not row_artifacts_missing_from_todo
                ),
                "claim_count": len(status_claims),
                "status_claims": status_claims,
                "claim_inventory_status": "phrase_candidate_evidence_links_recorded",
                "artifact_existence_status": (
                    "all_referenced_local_artifacts_present"
                    if row_local_artifact_paths and not row_missing_local_artifacts
                    else "missing_referenced_local_artifacts"
                    if row_missing_local_artifacts
                    else "no_local_artifacts_referenced"
                ),
                "todo_evidence_status": (
                    "all_referenced_todo_paths_present"
                    if (active_paths or completed_paths) and not missing_todo_paths
                    else "missing_referenced_todo_paths"
                    if missing_todo_paths
                    else "no_todo_evidence_paths_referenced"
                ),
                "todo_content_evidence_status": (
                    "all_row_local_artifacts_mentioned_in_todo_evidence"
                    if row_local_artifact_paths and not row_artifacts_missing_from_todo
                    else "missing_row_local_artifact_mentions_in_todo_evidence"
                    if row_artifacts_missing_from_todo
                    else "no_row_local_artifacts_referenced"
                ),
                "source_span_status": "phrase_offsets_recorded_in_status_cell",
                "freshness_status": "structural_only",
            }
        )

    total_claims = sum(row["claim_count"] for row in inventory_rows)
    unique_local_artifacts = sorted(
        {path for row in inventory_rows for path in row["local_artifact_paths"]}
    )
    local_artifact_mention_record_count = sum(
        len(row["local_artifact_mention_records"]) for row in inventory_rows
    )
    missing_local_artifacts = sorted(
        {path for row in inventory_rows for path in row["local_artifact_missing_paths"]}
    )
    unique_todo_paths = sorted(
        {path for row in inventory_rows for path in row["active_todo_paths"] + row["completed_todo_paths"]}
    )
    todo_evidence_path_mention_count = sum(
        row["todo_evidence_path_mention_count"] for row in inventory_rows
    )
    missing_todo_paths = sorted(
        {path for row in inventory_rows for path in row["todo_evidence_missing_paths"]}
    )
    local_artifacts_missing_from_todo = sorted(
        {
            path
            for row in inventory_rows
            for path in row["local_artifacts_missing_from_todo_evidence"]
        }
    )
    todo_content_artifact_mention_record_count = sum(
        len(record["mentioned_local_artifact_records"])
        for row in inventory_rows
        for record in [*row["active_todo_content_records"], *row["completed_todo_content_records"]]
    )
    todo_content_row_specific_block_record_count = sum(
        len(record["row_specific_block_records"])
        for row in inventory_rows
        for record in [*row["active_todo_content_records"], *row["completed_todo_content_records"]]
    )
    todo_content_matched_source_tokens = sorted(
        {
            token
            for row in inventory_rows
            for record in [*row["active_todo_content_records"], *row["completed_todo_content_records"]]
            for token in record["row_source_tokens_matched"]
        }
    )
    phrase_local_artifacts_missing_from_todo = sorted(
        {
            path
            for row in inventory_rows
            for claim in row["status_claims"]
            for path in claim["evidence_links"]["phrase_local_artifacts_missing_from_todo_evidence"]
        }
    )
    phrase_local_artifact_mention_record_count = sum(
        len(claim["evidence_links"]["phrase_local_artifact_mention_records"])
        for row in inventory_rows
        for claim in row["status_claims"]
    )
    phrase_todo_content_block_record_count = sum(
        len(claim["evidence_links"]["phrase_todo_content_block_records"])
        for row in inventory_rows
        for claim in row["status_claims"]
    )
    absence_phrase_ids = [
        claim["claim_id"]
        for row in inventory_rows
        for claim in row["status_claims"]
        if claim["absence_signal_records"]
    ]
    absence_signal_terms = sorted(
        {
            record["term"]
            for row in inventory_rows
            for claim in row["status_claims"]
            for record in claim["absence_signal_records"]
        }
    )
    absence_signal_record_count = sum(
        len(claim["absence_signal_records"])
        for row in inventory_rows
        for claim in row["status_claims"]
    )
    return {
        "schema": STATUS_CLAIM_INVENTORY_SCHEMA,
        "inventory_status": STATUS_CLAIM_INVENTORY_STATUS,
        "source_path": "papers/README.md#implementation-status",
        "row_count": len(inventory_rows),
        "claim_count": total_claims,
        "row_ids": [row["id"] for row in inventory_rows],
        "status_class_counts": dict(sorted(status_class_counts.items())),
        "unique_local_artifact_paths": unique_local_artifacts,
        "unique_local_artifact_count": len(unique_local_artifacts),
        "local_artifact_mention_record_count": local_artifact_mention_record_count,
        "missing_local_artifact_paths": missing_local_artifacts,
        "artifact_existence_status": (
            "all_referenced_local_artifacts_present"
            if unique_local_artifacts and not missing_local_artifacts
            else "missing_referenced_local_artifacts"
            if missing_local_artifacts
            else "no_local_artifacts_referenced"
        ),
        "unique_todo_evidence_paths": unique_todo_paths,
        "unique_todo_evidence_path_count": len(unique_todo_paths),
        "todo_evidence_path_mention_count": todo_evidence_path_mention_count,
        "missing_todo_evidence_paths": missing_todo_paths,
        "todo_evidence_status": (
            "all_referenced_todo_paths_present"
            if unique_todo_paths and not missing_todo_paths
            else "missing_referenced_todo_paths"
            if missing_todo_paths
            else "no_todo_evidence_paths_referenced"
        ),
        "local_artifacts_missing_from_todo_evidence": local_artifacts_missing_from_todo,
        "todo_content_artifact_mention_record_count": todo_content_artifact_mention_record_count,
        "todo_content_row_specific_block_record_count": todo_content_row_specific_block_record_count,
        "todo_content_matched_source_tokens": todo_content_matched_source_tokens,
        "todo_content_matched_source_token_count": len(todo_content_matched_source_tokens),
        "todo_content_evidence_status": (
            "all_row_local_artifacts_mentioned_in_todo_evidence"
            if unique_local_artifacts and not local_artifacts_missing_from_todo
            else "missing_row_local_artifact_mentions_in_todo_evidence"
            if local_artifacts_missing_from_todo
            else "no_row_local_artifacts_referenced"
        ),
        "phrase_local_artifacts_missing_from_todo_evidence": phrase_local_artifacts_missing_from_todo,
        "phrase_local_artifact_mention_record_count": phrase_local_artifact_mention_record_count,
        "phrase_todo_content_block_record_count": phrase_todo_content_block_record_count,
        "phrase_todo_content_evidence_status": (
            "all_phrase_local_artifacts_mentioned_in_todo_evidence"
            if unique_local_artifacts and not phrase_local_artifacts_missing_from_todo
            else "missing_phrase_local_artifact_mentions_in_todo_evidence"
            if phrase_local_artifacts_missing_from_todo
            else "no_phrase_local_artifacts_referenced"
        ),
        "absence_phrase_count": len(absence_phrase_ids),
        "absence_phrase_ids": absence_phrase_ids,
        "absence_signal_record_count": absence_signal_record_count,
        "absence_signal_terms": absence_signal_terms,
        "absence_signal_inventory_status": "absence_signals_structurally_classified_without_freshness_verification",
        "missing_evidence": dict(STATUS_CLAIM_INVENTORY_MISSING_EVIDENCE),
        "rows": inventory_rows,
        "claim_boundary": (
            "This inventory records one structured row for every "
            "papers/README.md implementation-status table row, including "
            "role, status class, status text hash, manifest file, local "
            "artifact mention source offsets and existence records, row "
            "source line, TODO evidence path source offsets and existence "
            "records, and status-cell phrase hashes with character offsets "
            "and candidate evidence links plus row/phrase-specific TODO content "
            "matched source tokens, block hashes/source offsets, "
            "artifact-mention source offsets, phrase-local TODO block "
            "records, and "
            "absence-signal source offsets. It "
            "does not claim phrase-level "
            "status verification, evidence-link sufficiency, "
            "implemented-benchmark bullet coverage, absence-sentence "
            "freshness, or proof that status-cell prose is semantically "
            "complete."
        ),
    }


def paper_benchmark_coverage_inventory_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the paper-index implemented benchmark coverage inventory."""

    root_path = Path(root)
    manifest_rows, _manifest_issues = _load_json_manifest(
        root_path / "papers" / "download_manifest.json",
        root_path,
    )
    bullets, _issues = _read_implemented_benchmark_bullet_records(root_path)
    rows: list[dict[str, Any]] = []
    for ordinal, bullet in enumerate(bullets, start=1):
        text = bullet["text"]
        summary = text.splitlines()[0].strip()
        source_token_match_records = _benchmark_source_token_match_records(
            text,
            bullet["line_start"],
            bullet["file_text_char_start"],
            manifest_rows,
        )
        source_ids_mentioned = sorted({record["row_id"] for record in source_token_match_records})
        local_artifact_mention_records = _benchmark_local_artifact_mention_records(
            text,
            bullet["line_start"],
            bullet["file_text_char_start"],
        )
        local_artifacts = sorted({record["path"] for record in local_artifact_mention_records})
        local_artifact_records = _local_artifact_path_records(root_path, local_artifacts)
        missing_local_artifacts = [
            record["path"] for record in local_artifact_records if not record["exists"]
        ]
        limitation_signal_records = _benchmark_limitation_signal_records(
            text,
            bullet["line_start"],
            bullet["file_text_char_start"],
        )
        limitation_signal_terms = list(
            dict.fromkeys(record["term"] for record in limitation_signal_records)
        )
        rows.append(
            {
                "coverage_id": f"implemented_benchmark_{ordinal:03d}",
                "bullet_ordinal": ordinal,
                "summary_sha256": hashlib.sha256(summary.encode("utf-8")).hexdigest(),
                "body_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "source_span": {
                    "path": "papers/README.md",
                    "section": "Benchmark coverage decisions",
                    "line_start": bullet["line_start"],
                    "line_end": bullet["line_end"],
                    "file_text_char_start": bullet["file_text_char_start"],
                    "file_text_char_end": bullet["file_text_char_end"],
                },
                "source_ids_mentioned": source_ids_mentioned,
                "source_token_match_records": source_token_match_records,
                "source_token_match_count": len(source_token_match_records),
                "local_artifact_paths": local_artifacts,
                "has_local_artifact": bool(local_artifacts),
                "local_artifact_mention_records": local_artifact_mention_records,
                "local_artifact_records": local_artifact_records,
                "local_artifact_existing_count": len(local_artifacts) - len(missing_local_artifacts),
                "local_artifact_missing_paths": missing_local_artifacts,
                "all_local_artifacts_exist": bool(local_artifacts) and not missing_local_artifacts,
                "limitation_signal_records": limitation_signal_records,
                "limitation_signal_terms": limitation_signal_terms,
                "has_limitation_boundary": bool(limitation_signal_terms),
                "has_not_implemented_contradiction": bool(BENCHMARK_IMPLEMENTED_NOT_IMPLEMENTED_RE.search(text)),
                "coverage_status": "implemented_bullet_structurally_inventoried",
                "limitation_signal_status": (
                    "limitation_signals_structurally_classified"
                    if limitation_signal_terms
                    else "no_limitation_signal_detected"
                ),
                "artifact_existence_status": (
                    "all_referenced_local_artifacts_present"
                    if local_artifacts and not missing_local_artifacts
                    else "missing_referenced_local_artifacts"
                    if missing_local_artifacts
                    else "no_local_artifacts_referenced"
                ),
                "semantic_status": "not_verified",
            }
        )
    unique_local_artifacts = sorted(
        {path for row in rows for path in row["local_artifact_paths"]}
    )
    local_artifact_mention_record_count = sum(
        len(row["local_artifact_mention_records"]) for row in rows
    )
    benchmark_source_ids_mentioned = sorted(
        {row_id for row in rows for row_id in row["source_ids_mentioned"]}
    )
    benchmark_source_token_match_record_count = sum(
        row["source_token_match_count"] for row in rows
    )
    missing_local_artifacts = sorted(
        {path for row in rows for path in row["local_artifact_missing_paths"]}
    )
    limitation_bullet_ids = [
        row["coverage_id"] for row in rows if row["limitation_signal_terms"]
    ]
    limitation_signal_terms = sorted(
        {
            term
            for row in rows
            for term in row["limitation_signal_terms"]
        }
    )
    limitation_signal_record_count = sum(
        len(row["limitation_signal_records"]) for row in rows
    )
    contradiction_bullet_ids = [
        row["coverage_id"] for row in rows if row["has_not_implemented_contradiction"]
    ]
    return {
        "schema": BENCHMARK_COVERAGE_INVENTORY_SCHEMA,
        "inventory_status": BENCHMARK_COVERAGE_INVENTORY_STATUS,
        "source_path": "papers/README.md#benchmark-coverage-decisions",
        "implemented_bullet_count": len(rows),
        "implemented_bullet_ids": [row["coverage_id"] for row in rows],
        "source_ids_mentioned": benchmark_source_ids_mentioned,
        "source_id_mention_count": len(benchmark_source_ids_mentioned),
        "source_token_match_record_count": benchmark_source_token_match_record_count,
        "source_token_coverage_status": "source_tokens_structurally_recorded_without_semantic_verifier",
        "implemented_bullet_source_span_status": "file_character_offsets_recorded",
        "implemented_bullet_mention_source_span_status": "file_character_offsets_recorded",
        "unique_local_artifact_paths": unique_local_artifacts,
        "unique_local_artifact_count": len(unique_local_artifacts),
        "local_artifact_mention_record_count": local_artifact_mention_record_count,
        "missing_local_artifact_paths": missing_local_artifacts,
        "artifact_existence_status": (
            "all_referenced_local_artifacts_present"
            if unique_local_artifacts and not missing_local_artifacts
            else "missing_referenced_local_artifacts"
            if missing_local_artifacts
            else "no_local_artifacts_referenced"
        ),
        "limitation_bullet_count": len(limitation_bullet_ids),
        "limitation_bullet_ids": limitation_bullet_ids,
        "limitation_signal_record_count": limitation_signal_record_count,
        "limitation_signal_terms": limitation_signal_terms,
        "limitation_signal_inventory_status": "limitation_signals_structurally_classified_without_semantic_verifier",
        "not_implemented_contradiction_count": len(contradiction_bullet_ids),
        "not_implemented_contradiction_bullet_ids": contradiction_bullet_ids,
        "missing_evidence": dict(BENCHMARK_COVERAGE_MISSING_EVIDENCE),
        "implemented_bullets": rows,
        "claim_boundary": (
            "This inventory records one structured entry for each "
            "papers/README.md Implemented benchmark coverage bullet, including "
            "source lines and file character offsets, summary/body hashes, "
            "source-token match offsets, local artifact mention source "
            "offsets, local artifact existence records, limitation-signal terms/source offsets, and "
            "contradiction flags. It does not claim "
            "semantic verification, benchmark freshness, reproduced result "
            "linkage, or proof that the benchmark coverage prose is complete."
        ),
    }


def _validate_appendix_a_matrix_registry_if_present(root_path: Path) -> list[PaperManifestIssue]:
    try:
        relative_registry = APPENDIX_A_MATRIX_REGISTRY_PATH.relative_to(_repo_root())
    except ValueError:
        relative_registry = Path("libreevolve/problems/benchmarks/alphaevolve_appendix_a_matrix.json")
    registry_path = root_path / relative_registry
    if not registry_path.exists():
        return []
    report = validate_appendix_a_matrix_registry(registry_path)
    issues = [
        PaperManifestIssue(
            f"appendix_a_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.target_id) if issue.target_id else None,
        )
        for issue in report.issues
    ]
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False

    curation_path = root_path / APPENDIX_A_CURATION_FILE
    if curation_path.exists():
        curation_recordset: object | str | Path = curation_path
    else:
        curation_recordset = appendix_a_matrix_curation_record(registry_path)
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "appendix_a_curation_manifest_missing",
                    f"{APPENDIX_A_CURATION_FILE} must emit the Appendix A matrix target-suite curation record",
                    "appendix_a_matrix_curation",
                )
            )
    curation_report = validate_appendix_a_matrix_curation(curation_recordset)
    issues.extend(
        PaperManifestIssue(
            f"appendix_a_curation_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.target_id) if issue.target_id else None,
        )
        for issue in curation_report.issues
    )
    excluded_curation_path = root_path / APPENDIX_A_EXCLUDED_TARGET_CURATION_FILE
    if excluded_curation_path.exists():
        excluded_curation_recordset: object | str | Path = excluded_curation_path
    else:
        excluded_curation_recordset = appendix_a_matrix_excluded_target_curation_boundary_record()
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "appendix_a_excluded_target_curation_manifest_missing",
                    (
                        f"{APPENDIX_A_EXCLUDED_TARGET_CURATION_FILE} must emit the "
                        "Appendix A excluded-target curation boundary"
                    ),
                    "appendix_a_matrix_excluded_target_curation",
                )
            )
    excluded_curation_report = validate_appendix_a_matrix_excluded_target_curation_boundary(
        excluded_curation_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"appendix_a_excluded_target_curation_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.target_id) if issue.target_id else None,
        )
        for issue in excluded_curation_report.issues
    )
    baseline_citations_path = root_path / APPENDIX_A_BASELINE_CITATIONS_FILE
    if baseline_citations_path.exists():
        baseline_citation_recordset: object | str | Path = baseline_citations_path
    else:
        baseline_citation_recordset = appendix_a_matrix_baseline_citation_boundary_record()
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "appendix_a_baseline_citation_manifest_missing",
                    (
                        f"{APPENDIX_A_BASELINE_CITATIONS_FILE} must record "
                        "Appendix A Table 3 best-known-rank reference ids"
                    ),
                    "appendix_a_matrix_baseline_citations",
                )
            )
    baseline_citation_report = validate_appendix_a_matrix_baseline_citation_boundary(
        baseline_citation_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"appendix_a_baseline_citation_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.target_id) if issue.target_id else None,
        )
        for issue in baseline_citation_report.issues
    )
    resource_frontier_path = root_path / APPENDIX_A_RESOURCE_FRONTIER_FILE
    if resource_frontier_path.exists():
        resource_frontier_recordset: object | str | Path = resource_frontier_path
    else:
        resource_frontier_recordset = appendix_a_matrix_resource_frontier_record()
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "appendix_a_resource_frontier_manifest_missing",
                    f"{APPENDIX_A_RESOURCE_FRONTIER_FILE} must emit the Appendix A paper resource-frontier boundary",
                    "appendix_a_matrix_resource_frontier",
                )
            )
    resource_frontier_report = validate_appendix_a_matrix_resource_frontier(
        resource_frontier_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"appendix_a_resource_frontier_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.attempt_id) if issue.attempt_id else None,
        )
        for issue in resource_frontier_report.issues
    )
    local_resource_frontier_path = root_path / APPENDIX_A_LOCAL_RESOURCE_FRONTIER_FILE
    if local_resource_frontier_path.exists():
        local_resource_frontier_recordset: object | str | Path = local_resource_frontier_path
    else:
        local_resource_frontier_recordset = appendix_a_matrix_local_resource_frontier_record()
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "appendix_a_local_resource_frontier_manifest_missing",
                    (
                        f"{APPENDIX_A_LOCAL_RESOURCE_FRONTIER_FILE} must emit the "
                        "Appendix A local resource-frontier absence boundary"
                    ),
                    "appendix_a_matrix_local_resource_frontier",
                )
            )
    local_resource_frontier_report = validate_appendix_a_matrix_local_resource_frontier(
        local_resource_frontier_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"appendix_a_local_resource_frontier_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.attempt_id) if issue.attempt_id else None,
        )
        for issue in local_resource_frontier_report.issues
    )
    subset_scope_artifacts_path = root_path / APPENDIX_A_SUBSET_SCOPE_ARTIFACTS_FILE
    if subset_scope_artifacts_path.exists():
        subset_scope_artifact_recordset: object | str | Path = subset_scope_artifacts_path
    else:
        subset_scope_artifact_recordset = appendix_a_matrix_subset_scope_artifact_boundary_record()
        try:
            is_repo_root = root_path.resolve() == _repo_root().resolve()
        except OSError:
            is_repo_root = False
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "appendix_a_subset_scope_artifact_manifest_missing",
                    f"{APPENDIX_A_SUBSET_SCOPE_ARTIFACTS_FILE} must emit the Appendix A matrix subset-scope artifacts",
                    "appendix_a_full",
                )
            )
    subset_scope_artifact_report = validate_appendix_a_matrix_subset_scope_artifact_boundary(
        subset_scope_artifact_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"appendix_a_subset_scope_artifact_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.subset_id) if issue.subset_id else None,
        )
        for issue in subset_scope_artifact_report.issues
    )
    row_note_artifacts_path = root_path / APPENDIX_A_ROW_NOTE_ARTIFACTS_FILE
    if row_note_artifacts_path.exists():
        row_note_artifact_recordset: object | str | Path = row_note_artifacts_path
    else:
        row_note_artifact_recordset = appendix_a_matrix_row_note_artifact_boundary_record()
        try:
            is_repo_root = root_path.resolve() == _repo_root().resolve()
        except OSError:
            is_repo_root = False
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "appendix_a_row_note_artifact_manifest_missing",
                    f"{APPENDIX_A_ROW_NOTE_ARTIFACTS_FILE} must emit the Appendix A matrix row-note caveat artifact",
                    "concurrent_work_rank90_mm_4x5x6",
                )
            )
    row_note_artifact_report = validate_appendix_a_matrix_row_note_artifact_boundary(
        row_note_artifact_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"appendix_a_row_note_artifact_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.note_id) if issue.note_id else None,
        )
        for issue in row_note_artifact_report.issues
    )
    strassen_bundle_report = validate_strassen_2x2_publication_bundle()
    issues.extend(
        PaperManifestIssue(
            f"matrix_strassen_bundle_{issue.code}",
            issue.message,
        )
        for issue in strassen_bundle_report.issues
    )
    suite_publication_path = root_path / MATRIX_SUITE_PUBLICATION_ARTIFACTS_FILE
    if suite_publication_path.exists():
        suite_publication_recordset: object | str | Path = suite_publication_path
    else:
        suite_publication_recordset = matrix_suite_publication_artifact_boundary_record()
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "matrix_suite_publication_artifact_manifest_missing",
                    (
                        f"{MATRIX_SUITE_PUBLICATION_ARTIFACTS_FILE} must emit "
                        "the matrix suite publication-artifact boundary"
                    ),
                    "matrix_suite_publication_artifacts",
                )
            )
    suite_publication_report = validate_matrix_suite_publication_artifact_boundary(
        suite_publication_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_suite_publication_artifact_{issue.code}",
            issue.message,
        )
        for issue in suite_publication_report.issues
    )
    baseline_component_runtime_path = root_path / MATRIX_BASELINE_COMPONENT_RUNTIME_FILE
    if baseline_component_runtime_path.exists():
        baseline_component_runtime_recordset: object | str | Path = (
            baseline_component_runtime_path
        )
    else:
        baseline_component_runtime_recordset = matrix_baseline_component_runtime_boundary_record()
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "matrix_baseline_component_runtime_manifest_missing",
                    (
                        f"{MATRIX_BASELINE_COMPONENT_RUNTIME_FILE} must emit the "
                        "matrix baseline-component runtime boundary"
                    ),
                    "matrix_baseline_component_runtime_boundary",
                )
            )
    baseline_component_runtime_report = validate_matrix_baseline_component_runtime_boundary(
        baseline_component_runtime_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_baseline_component_runtime_{issue.code}",
            issue.message,
        )
        for issue in baseline_component_runtime_report.issues
    )
    cascade_run_runtime_path = root_path / MATRIX_CASCADE_RUN_RUNTIME_FILE
    if cascade_run_runtime_path.exists():
        cascade_run_runtime_recordset: object | str | Path = cascade_run_runtime_path
    else:
        cascade_run_runtime_recordset = matrix_cascade_run_runtime_boundary_record()
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "matrix_cascade_run_runtime_manifest_missing",
                    (
                        f"{MATRIX_CASCADE_RUN_RUNTIME_FILE} must emit the "
                        "matrix cascade-run runtime boundary"
                    ),
                    "matrix_cascade_run_runtime_boundary",
                )
            )
    cascade_run_runtime_report = validate_matrix_cascade_run_runtime_boundary(
        cascade_run_runtime_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_cascade_run_runtime_{issue.code}",
            issue.message,
        )
        for issue in cascade_run_runtime_report.issues
    )
    near_integrality_runtime_path = root_path / MATRIX_NEAR_INTEGRALITY_RUNTIME_FILE
    if near_integrality_runtime_path.exists():
        near_integrality_runtime_recordset: object | str | Path = (
            near_integrality_runtime_path
        )
    else:
        near_integrality_runtime_recordset = matrix_near_integrality_runtime_boundary_record()
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "matrix_near_integrality_runtime_manifest_missing",
                    (
                        f"{MATRIX_NEAR_INTEGRALITY_RUNTIME_FILE} must emit the "
                        "matrix near-integrality runtime boundary"
                    ),
                    "matrix_near_integrality_runtime_boundary",
                )
            )
    near_integrality_runtime_report = validate_matrix_near_integrality_runtime_boundary(
        near_integrality_runtime_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_near_integrality_runtime_{issue.code}",
            issue.message,
        )
        for issue in near_integrality_runtime_report.issues
    )
    scalar_field_runtime_path = root_path / MATRIX_SCALAR_FIELD_RUNTIME_FILE
    if scalar_field_runtime_path.exists():
        scalar_field_runtime_recordset: object | str | Path = scalar_field_runtime_path
    else:
        scalar_field_runtime_recordset = matrix_scalar_field_runtime_boundary_record()
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "matrix_scalar_field_runtime_manifest_missing",
                    (
                        f"{MATRIX_SCALAR_FIELD_RUNTIME_FILE} must emit the "
                        "matrix scalar-field runtime boundary"
                    ),
                    "matrix_scalar_field_runtime_boundary",
                )
            )
    scalar_field_runtime_report = validate_matrix_scalar_field_runtime_boundary(
        scalar_field_runtime_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_scalar_field_runtime_{issue.code}",
            issue.message,
        )
        for issue in scalar_field_runtime_report.issues
    )
    sweep_space_runtime_path = root_path / MATRIX_SWEEP_SPACE_RUNTIME_FILE
    if sweep_space_runtime_path.exists():
        sweep_space_runtime_recordset: object | str | Path = sweep_space_runtime_path
    else:
        sweep_space_runtime_recordset = matrix_sweep_space_runtime_boundary_record()
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "matrix_sweep_space_runtime_manifest_missing",
                    (
                        f"{MATRIX_SWEEP_SPACE_RUNTIME_FILE} must emit the "
                        "matrix sweep-space runtime boundary"
                    ),
                    "matrix_sweep_space_runtime_boundary",
                )
            )
    sweep_space_runtime_report = validate_matrix_sweep_space_runtime_boundary(
        sweep_space_runtime_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_sweep_space_runtime_{issue.code}",
            issue.message,
        )
        for issue in sweep_space_runtime_report.issues
    )
    tensor_rank_runtime_path = root_path / MATRIX_TENSOR_RANK_RUNTIME_FILE
    if tensor_rank_runtime_path.exists():
        tensor_rank_runtime_recordset: object | str | Path = tensor_rank_runtime_path
    else:
        tensor_rank_runtime_recordset = matrix_tensor_rank_runtime_boundary_record()
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "matrix_tensor_rank_runtime_manifest_missing",
                    (
                        f"{MATRIX_TENSOR_RANK_RUNTIME_FILE} must emit the "
                        "matrix tensor-rank runtime boundary"
                    ),
                    "matrix_tensor_rank_runtime_boundary",
                )
            )
    tensor_rank_runtime_report = validate_matrix_tensor_rank_runtime_boundary(
        tensor_rank_runtime_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_tensor_rank_runtime_{issue.code}",
            issue.message,
        )
        for issue in tensor_rank_runtime_report.issues
    )
    headline_historicity_artifacts_path = root_path / MATRIX_HEADLINE_HISTORICITY_ARTIFACTS_FILE
    if headline_historicity_artifacts_path.exists():
        headline_historicity_recordset: object | str | Path = (
            headline_historicity_artifacts_path
        )
    else:
        headline_historicity_recordset = matrix_headline_historicity_runtime_boundary_record()
        try:
            is_repo_root = root_path.resolve() == _repo_root().resolve()
        except OSError:
            is_repo_root = False
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "matrix_headline_historicity_artifact_manifest_missing",
                    (
                        f"{MATRIX_HEADLINE_HISTORICITY_ARTIFACTS_FILE} must "
                        "emit the 4x4 complex rank-48 headline historicity artifact"
                    ),
                    "mm_4x4x4",
                )
            )
    headline_runtime_report = validate_matrix_headline_historicity_runtime_boundary(
        headline_historicity_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_headline_historicity_runtime_{issue.code}",
            issue.message,
        )
        for issue in headline_runtime_report.issues
    )
    rank_table_artifacts_path = root_path / MATRIX_RANK_TABLE_ARTIFACTS_FILE
    if rank_table_artifacts_path.exists():
        rank_table_artifact_recordset: object | str | Path = rank_table_artifacts_path
    else:
        rank_table_artifact_recordset = matrix_rank_table_artifact_boundary_record()
        try:
            is_repo_root = root_path.resolve() == _repo_root().resolve()
        except OSError:
            is_repo_root = False
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "matrix_rank_table_artifact_manifest_missing",
                    f"{MATRIX_RANK_TABLE_ARTIFACTS_FILE} must emit Table 2/Table 3 matrix-rank table artifacts",
                    "table2_matrix_rank_selected",
                )
            )
    rank_table_artifact_report = validate_matrix_rank_table_artifact_boundary(
        rank_table_artifact_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"matrix_rank_table_artifact_{issue.code}",
            issue.message,
        )
        for issue in rank_table_artifact_report.issues
    )
    figure9_artifacts_path = root_path / FIGURE9_MATRIX_DIFF_ARTIFACTS_FILE
    if figure9_artifacts_path.exists():
        figure9_artifact_recordset: object | str | Path = figure9_artifacts_path
    else:
        figure9_artifact_recordset = figure9_matrix_diff_artifact_boundary_record()
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "figure9_matrix_diff_artifact_manifest_missing",
                    (
                        f"{FIGURE9_MATRIX_DIFF_ARTIFACTS_FILE} must emit "
                        "Figure 9 matrix-diff artifact availability"
                    ),
                    "figure9_matrix_diff_magnified",
                )
            )
    figure9_artifact_report = validate_figure9_matrix_diff_artifact_boundary(
        figure9_artifact_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"figure9_matrix_diff_artifact_{issue.code}",
            issue.message,
        )
        for issue in figure9_artifact_report.issues
    )
    figure4_artifacts_path = root_path / FIGURE4_MATRIX_DISCOVERY_ARTIFACTS_FILE
    if figure4_artifacts_path.exists():
        figure4_artifact_recordset: object | str | Path = figure4_artifacts_path
    else:
        figure4_artifact_recordset = figure4_matrix_discovery_artifact_boundary_record()
        if is_repo_root:
            issues.append(
                PaperManifestIssue(
                    "figure4_matrix_discovery_artifact_manifest_missing",
                    (
                        f"{FIGURE4_MATRIX_DISCOVERY_ARTIFACTS_FILE} must emit "
                        "Figure 4 matrix-discovery artifact availability"
                    ),
                    "figure4_matrix_discovery",
                )
            )
    figure4_artifact_report = validate_figure4_matrix_discovery_artifact_boundary(
        figure4_artifact_recordset
    )
    issues.extend(
        PaperManifestIssue(
            f"figure4_matrix_discovery_artifact_{issue.code}",
            issue.message,
        )
        for issue in figure4_artifact_report.issues
    )
    return issues


def _validate_alphaevolve_arxiv_abstract_snapshot(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ARXIV_ABSTRACT_SNAPSHOT_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_arxiv_abstract_snapshot_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_arxiv_abstract_snapshot_manifest_missing",
                    (
                        f"{ARXIV_ABSTRACT_SNAPSHOT_FILE} must emit the pinned "
                        "AlphaEvolve arXiv abstract-page metadata snapshot"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_arxiv_abstract_snapshot(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_arxiv_abstract_snapshot_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_current_version_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_CURRENT_VERSION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_current_version_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_current_version_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_CURRENT_VERSION_BOUNDARY_FILE} must emit "
                        "the AlphaEvolve current-version/floating-PDF boundary"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_current_version_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_current_version_boundary_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_cached_pdf_header_consistency_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_CACHED_PDF_HEADER_CONSISTENCY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_cached_pdf_header_consistency_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_cached_pdf_header_consistency_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_CACHED_PDF_HEADER_CONSISTENCY_BOUNDARY_FILE} must emit "
                        "the AlphaEvolve cached-PDF header consistency boundary"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_cached_pdf_header_consistency_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_cached_pdf_header_consistency_boundary_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_metadata_extraction_script_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_METADATA_EXTRACTION_SCRIPT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_metadata_extraction_script_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_metadata_extraction_script_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_METADATA_EXTRACTION_SCRIPT_BOUNDARY_FILE} must emit "
                        "the AlphaEvolve metadata extraction-script boundary"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_metadata_extraction_script_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_metadata_extraction_script_boundary_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_source_refresh_gate_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_SOURCE_REFRESH_GATE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_source_refresh_gate_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_source_refresh_gate_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_SOURCE_REFRESH_GATE_BOUNDARY_FILE} must emit "
                        "the AlphaEvolve source refresh-gate boundary"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_source_refresh_gate_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_source_refresh_gate_boundary_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_source_refresh_run_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_SOURCE_REFRESH_RUN_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_source_refresh_run_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_source_refresh_run_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_SOURCE_REFRESH_RUN_BOUNDARY_FILE} must emit "
                        "the AlphaEvolve source refresh-run boundary"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_source_refresh_run_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_source_refresh_run_boundary_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_source_refresh_promotion_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_SOURCE_REFRESH_PROMOTION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_source_refresh_promotion_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_source_refresh_promotion_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_SOURCE_REFRESH_PROMOTION_BOUNDARY_FILE} must emit "
                        "the AlphaEvolve source refresh promotion boundary"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_source_refresh_promotion_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_source_refresh_promotion_boundary_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_raw_http_headers_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_RAW_HTTP_HEADERS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_raw_http_headers_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_raw_http_headers_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_RAW_HTTP_HEADERS_BOUNDARY_FILE} must emit "
                        "the AlphaEvolve raw HTTP headers boundary"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_raw_http_headers_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_raw_http_headers_boundary_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_datacite_doi_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_DATACITE_DOI_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_datacite_doi_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_datacite_doi_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_DATACITE_DOI_BOUNDARY_FILE} must emit "
                        "the AlphaEvolve DOI/DataCite source-evidence boundary"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_datacite_doi_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_datacite_doi_boundary_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_datacite_full_response_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_DATACITE_FULL_RESPONSE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_datacite_full_response_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_datacite_full_response_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_DATACITE_FULL_RESPONSE_BOUNDARY_FILE} must emit "
                        "the AlphaEvolve full DataCite response boundary"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_datacite_full_response_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_datacite_full_response_boundary_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_doi_landing_resolution_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_DOI_LANDING_RESOLUTION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_doi_landing_resolution_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_doi_landing_resolution_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_DOI_LANDING_RESOLUTION_BOUNDARY_FILE} must emit "
                        "the AlphaEvolve DOI landing-resolution boundary"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_doi_landing_resolution_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_doi_landing_resolution_boundary_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_tex_source_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_TEX_SOURCE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_tex_source_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_tex_source_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_TEX_SOURCE_BOUNDARY_FILE} must emit "
                        "the AlphaEvolve arXiv TeX/e-print digest boundary"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_tex_source_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_tex_source_boundary_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_tex_archive_retention_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_TEX_ARCHIVE_RETENTION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_tex_archive_retention_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_tex_archive_retention_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_TEX_ARCHIVE_RETENTION_BOUNDARY_FILE} must emit "
                        "the AlphaEvolve TeX archive retention boundary"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_tex_archive_retention_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_tex_archive_retention_boundary_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_license_page_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_LICENSE_PAGE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_license_page_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_license_page_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_LICENSE_PAGE_BOUNDARY_FILE} must emit "
                        "the AlphaEvolve source-license page digest boundary"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_license_page_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_license_page_boundary_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_appendix_b_registry_if_present(root_path: Path) -> list[PaperManifestIssue]:
    try:
        relative_registry = APPENDIX_B_REGISTRY_PATH.relative_to(_repo_root())
    except ValueError:
        relative_registry = Path("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json")
    registry_path = root_path / relative_registry
    if not registry_path.exists():
        return []
    report = validate_appendix_b_registry(registry_path, repo_root=root_path)
    return [
        PaperManifestIssue(
            f"appendix_b_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.family_id) if issue.family_id else None,
        )
        for issue in report.issues
    ]


def _validate_ablation_registry_if_present(root_path: Path) -> list[PaperManifestIssue]:
    try:
        relative_registry = ABLATION_REGISTRY_PATH.relative_to(_repo_root())
    except ValueError:
        relative_registry = Path("libreevolve/problems/benchmarks/alphaevolve_ablations.json")
    registry_path = root_path / relative_registry
    if not registry_path.exists():
        return []
    report = validate_ablation_registry(registry_path)
    return [
        PaperManifestIssue(
            f"ablation_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.variant_id) if issue.variant_id else None,
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_license_page_html_retention_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_LICENSE_PAGE_HTML_RETENTION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_license_page_html_retention_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_license_page_html_retention_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_LICENSE_PAGE_HTML_RETENTION_BOUNDARY_FILE} must emit "
                        "the AlphaEvolve license-page HTML retention boundary"
                    ),
                    "2506.13131",
                )
            ]
    report = validate_alphaevolve_license_page_html_retention_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_license_page_html_retention_boundary_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_figure8_ablation_artifacts(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / FIGURE8_ABLATION_ARTIFACTS_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = figure8_artifact_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "figure8_ablation_artifact_manifest_missing",
                    f"{FIGURE8_ABLATION_ARTIFACTS_FILE} must emit Figure 8 ablation-curve artifact availability",
                    "figure8_ablation_curves",
                )
            ]
    report = validate_figure8_artifact_boundary(recordset)
    return [
        PaperManifestIssue(
            f"figure8_ablation_artifact_{issue.code}",
            issue.message,
            "figure8_ablation_curves",
        )
        for issue in report.issues
    ]


def _validate_benchmark_fixture_readiness_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / BENCHMARK_FIXTURE_READINESS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = benchmark_fixture_readiness_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "benchmark_fixture_readiness_boundary_manifest_missing",
                    (
                        f"{BENCHMARK_FIXTURE_READINESS_BOUNDARY_FILE} must emit "
                        "benchmark-fixture readiness availability"
                    ),
                    "benchmark_fixture_readiness",
                )
            ]
    report = validate_benchmark_fixture_readiness_boundary(recordset)
    return [
        PaperManifestIssue(
            f"benchmark_fixture_readiness_boundary_{issue.code}",
            issue.message,
            "benchmark_fixture_readiness",
        )
        for issue in report.issues
    ]


def _validate_systems_result_readiness_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / SYSTEMS_RESULT_READINESS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = systems_result_readiness_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "systems_result_readiness_boundary_manifest_missing",
                    (
                        f"{SYSTEMS_RESULT_READINESS_BOUNDARY_FILE} must emit "
                        "systems-result report-contract versus real-fixture readiness"
                    ),
                    "systems_result_readiness",
                )
            ]
    report = validate_systems_result_readiness_boundary(recordset)
    return [
        PaperManifestIssue(
            f"systems_result_readiness_boundary_{issue.code}",
            issue.message,
            "systems_result_readiness",
        )
        for issue in report.issues
    ]


def _validate_problem_formulation_provenance_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PROBLEM_FORMULATION_PROVENANCE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = problem_formulation_provenance_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "problem_formulation_provenance_boundary_manifest_missing",
                    (
                        f"{PROBLEM_FORMULATION_PROVENANCE_BOUNDARY_FILE} must emit "
                        "problem-formulation provenance availability"
                    ),
                    "problem_formulation_provenance",
                )
            ]
    report = validate_problem_formulation_provenance_boundary(recordset)
    return [
        PaperManifestIssue(
            f"problem_formulation_provenance_boundary_{issue.code}",
            issue.message,
            "problem_formulation_provenance",
        )
        for issue in report.issues
    ]


def _validate_task_specification_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / TASK_SPECIFICATION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = task_specification_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "task_specification_boundary_manifest_missing",
                    (
                        f"{TASK_SPECIFICATION_BOUNDARY_FILE} must emit "
                        "task-specification artifact-resolution availability"
                    ),
                    "task_specification",
                )
            ]
    report = validate_task_specification_boundary(recordset)
    return [
        PaperManifestIssue(
            f"task_specification_boundary_{issue.code}",
            issue.message,
            "task_specification",
        )
        for issue in report.issues
    ]


def _validate_natural_language_preamble_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / NATURAL_LANGUAGE_PREAMBLE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = natural_language_preamble_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "natural_language_preamble_boundary_manifest_missing",
                    (
                        f"{NATURAL_LANGUAGE_PREAMBLE_BOUNDARY_FILE} must emit "
                        "bounded leading preamble versus complete rationale-handling scope"
                    ),
                    "natural_language_preamble",
                )
            ]
    report = validate_natural_language_preamble_boundary(recordset)
    return [
        PaperManifestIssue(
            f"natural_language_preamble_boundary_{issue.code}",
            issue.message,
            "natural_language_preamble",
        )
        for issue in report.issues
    ]


def _validate_prompt_example_copy_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PROMPT_EXAMPLE_COPY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = prompt_example_copy_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "prompt_example_copy_boundary_manifest_missing",
                    (
                        f"{PROMPT_EXAMPLE_COPY_BOUNDARY_FILE} must emit "
                        "built-in prompt-example diagnostics versus full guard scope"
                    ),
                    "prompt_example_copy",
                )
            ]
    report = validate_prompt_example_copy_boundary(recordset)
    return [
        PaperManifestIssue(
            f"prompt_example_copy_boundary_{issue.code}",
            issue.message,
            "prompt_example_copy",
        )
        for issue in report.issues
    ]


def _validate_mutation_consistency_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / MUTATION_CONSISTENCY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = mutation_consistency_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "mutation_consistency_boundary_manifest_missing",
                    (
                        f"{MUTATION_CONSISTENCY_BOUNDARY_FILE} must emit "
                        "multi-edit diagnostic scan versus consistency proof scope"
                    ),
                    "mutation_consistency",
                )
            ]
    report = validate_mutation_consistency_boundary(recordset)
    return [
        PaperManifestIssue(
            f"mutation_consistency_boundary_{issue.code}",
            issue.message,
            "mutation_consistency",
        )
        for issue in report.issues
    ]


def _validate_mutation_operator_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / MUTATION_OPERATOR_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = mutation_operator_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "mutation_operator_boundary_manifest_missing",
                    (
                        f"{MUTATION_OPERATOR_BOUNDARY_FILE} must emit "
                        "fixed edit payload grammar versus operator-family evidence"
                    ),
                    "mutation_operator",
                )
            ]
    report = validate_mutation_operator_boundary(recordset)
    return [
        PaperManifestIssue(
            f"mutation_operator_boundary_{issue.code}",
            issue.message,
            "mutation_operator",
        )
        for issue in report.issues
    ]


def _validate_adaptive_mutation_mode_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ADAPTIVE_MUTATION_MODE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = adaptive_mutation_mode_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "adaptive_mutation_mode_boundary_manifest_missing",
                    (
                        f"{ADAPTIVE_MUTATION_MODE_BOUNDARY_FILE} must emit "
                        "run-wide mutation-mode versus adaptive selection scope"
                    ),
                    "adaptive_mutation_mode",
                )
            ]
    report = validate_adaptive_mutation_mode_boundary(recordset)
    return [
        PaperManifestIssue(
            f"adaptive_mutation_mode_boundary_{issue.code}",
            issue.message,
            "adaptive_mutation_mode",
        )
        for issue in report.issues
    ]


def _validate_initial_pool_divergence_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / INITIAL_POOL_DIVERGENCE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = initial_pool_divergence_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "initial_pool_divergence_boundary_manifest_missing",
                    (
                        f"{INITIAL_POOL_DIVERGENCE_BOUNDARY_FILE} must emit "
                        "syntactic/metric telemetry versus functional discovery-distance scope"
                    ),
                    "initial_pool_divergence",
                )
            ]
    report = validate_initial_pool_divergence_boundary(recordset)
    return [
        PaperManifestIssue(
            f"initial_pool_divergence_boundary_{issue.code}",
            issue.message,
            "initial_pool_divergence",
        )
        for issue in report.issues
    ]


def _validate_duplicate_work_policy_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / DUPLICATE_WORK_POLICY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = duplicate_work_policy_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "duplicate_work_policy_boundary_manifest_missing",
                    (
                        f"{DUPLICATE_WORK_POLICY_BOUNDARY_FILE} must emit "
                        "run-local exact workspace cache versus durable memory scope"
                    ),
                    "duplicate_work_policy",
                )
            ]
    report = validate_duplicate_work_policy_boundary(recordset)
    return [
        PaperManifestIssue(
            f"duplicate_work_policy_boundary_{issue.code}",
            issue.message,
            "duplicate_work_policy",
        )
        for issue in report.issues
    ]


def _validate_programmatic_representation_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PROGRAMMATIC_REPRESENTATION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = programmatic_representation_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "programmatic_representation_boundary_manifest_missing",
                    (
                        f"{PROGRAMMATIC_REPRESENTATION_BOUNDARY_FILE} must emit "
                        "code/programmatic-evaluation versus natural-language boundary"
                    ),
                    "programmatic_representation",
                )
            ]
    report = validate_programmatic_representation_boundary(recordset)
    return [
        PaperManifestIssue(
            f"programmatic_representation_boundary_{issue.code}",
            issue.message,
            "programmatic_representation",
        )
        for issue in report.issues
    ]


def _validate_qualitative_feedback_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / QUALITATIVE_FEEDBACK_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = qualitative_feedback_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "qualitative_feedback_boundary_manifest_missing",
                    (
                        f"{QUALITATIVE_FEEDBACK_BOUNDARY_FILE} must emit "
                        "declared qualitative feedback versus executed calibration scope"
                    ),
                    "qualitative_feedback",
                )
            ]
    report = validate_qualitative_feedback_boundary(recordset)
    return [
        PaperManifestIssue(
            f"qualitative_feedback_boundary_{issue.code}",
            issue.message,
            "qualitative_feedback",
        )
        for issue in report.issues
    ]


def _validate_feedback_calibration_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / FEEDBACK_CALIBRATION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = feedback_calibration_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "feedback_calibration_boundary_manifest_missing",
                    (
                        f"{FEEDBACK_CALIBRATION_BOUNDARY_FILE} must emit "
                        "feedback-calibration contract versus executed-fixture scope"
                    ),
                    "feedback_calibration",
                )
            ]
    report = validate_feedback_calibration_boundary(recordset)
    return [
        PaperManifestIssue(
            f"feedback_calibration_boundary_{issue.code}",
            issue.message,
            "feedback_calibration",
        )
        for issue in report.issues
    ]


def _validate_llm_role_scheduler_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / LLM_ROLE_SCHEDULER_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = llm_role_scheduler_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "llm_role_scheduler_boundary_manifest_missing",
                    (
                        f"{LLM_ROLE_SCHEDULER_BOUNDARY_FILE} must emit "
                        "role-scoped scheduler evidence versus calibrated policy scope"
                    ),
                    "llm_role_scheduler",
                )
            ]
    report = validate_llm_role_scheduler_boundary(recordset)
    return [
        PaperManifestIssue(
            f"llm_role_scheduler_boundary_{issue.code}",
            issue.message,
            "llm_role_scheduler",
        )
        for issue in report.issues
    ]


def _validate_llm_budget_policy_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / LLM_BUDGET_POLICY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = llm_budget_policy_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "llm_budget_policy_boundary_manifest_missing",
                    (
                        f"{LLM_BUDGET_POLICY_BOUNDARY_FILE} must emit "
                        "cooperative LLM budget versus async pending-work scope"
                    ),
                    "llm_budget_policy",
                )
            ]
    report = validate_llm_budget_policy_boundary(recordset)
    return [
        PaperManifestIssue(
            f"llm_budget_policy_boundary_{issue.code}",
            issue.message,
            "llm_budget_policy",
        )
        for issue in report.issues
    ]


def _validate_llm_stochastic_reproducibility_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / LLM_STOCHASTIC_REPRODUCIBILITY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = llm_stochastic_reproducibility_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "llm_stochastic_reproducibility_boundary_manifest_missing",
                    (
                        f"{LLM_STOCHASTIC_REPRODUCIBILITY_BOUNDARY_FILE} must emit "
                        "request-parameter telemetry versus deterministic replay scope"
                    ),
                    "llm_stochastic_reproducibility",
                )
            ]
    report = validate_llm_stochastic_reproducibility_boundary(recordset)
    return [
        PaperManifestIssue(
            f"llm_stochastic_reproducibility_boundary_{issue.code}",
            issue.message,
            "llm_stochastic_reproducibility",
        )
        for issue in report.issues
    ]


def _validate_fast_strong_model_mix_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / FAST_STRONG_MODEL_MIX_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = fast_strong_model_mix_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "fast_strong_model_mix_boundary_manifest_missing",
                    (
                        f"{FAST_STRONG_MODEL_MIX_BOUNDARY_FILE} must emit "
                        "throughput/depth metadata versus fast/strong experiment scope"
                    ),
                    "fast_strong_model_mix",
                )
            ]
    report = validate_fast_strong_model_mix_boundary(recordset)
    return [
        PaperManifestIssue(
            f"fast_strong_model_mix_boundary_{issue.code}",
            issue.message,
            "fast_strong_model_mix",
        )
        for issue in report.issues
    ]


def _validate_provider_cancellation_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PROVIDER_CANCELLATION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = provider_cancellation_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "provider_cancellation_boundary_manifest_missing",
                    (
                        f"{PROVIDER_CANCELLATION_BOUNDARY_FILE} must emit "
                        "provider cancellation policy versus live hard-cancel scope"
                    ),
                    "provider_cancellation",
                )
            ]
    report = validate_provider_cancellation_boundary(recordset)
    return [
        PaperManifestIssue(
            f"provider_cancellation_boundary_{issue.code}",
            issue.message,
            "provider_cancellation",
        )
        for issue in report.issues
    ]


def _validate_provider_pricing_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PROVIDER_PRICING_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = provider_pricing_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "provider_pricing_boundary_manifest_missing",
                    (
                        f"{PROVIDER_PRICING_BOUNDARY_FILE} must emit "
                        "configured-cost estimates versus live provider-pricing scope"
                    ),
                    "provider_pricing",
                )
            ]
    report = validate_provider_pricing_boundary(recordset)
    return [
        PaperManifestIssue(
            f"provider_pricing_boundary_{issue.code}",
            issue.message,
            "provider_pricing",
        )
        for issue in report.issues
    ]


def _validate_provider_diagnostics_replay_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PROVIDER_DIAGNOSTICS_REPLAY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = provider_diagnostics_replay_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "provider_diagnostics_replay_boundary_manifest_missing",
                    (
                        f"{PROVIDER_DIAGNOSTICS_REPLAY_BOUNDARY_FILE} must emit "
                        "bounded provider diagnostics versus raw provider replay scope"
                    ),
                    "provider_diagnostics_replay",
                )
            ]
    report = validate_provider_diagnostics_replay_boundary(recordset)
    return [
        PaperManifestIssue(
            f"provider_diagnostics_replay_boundary_{issue.code}",
            issue.message,
            "provider_diagnostics_replay",
        )
        for issue in report.issues
    ]


def _validate_critique_reviewer_pool_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / CRITIQUE_REVIEWER_POOL_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = critique_reviewer_pool_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "critique_reviewer_pool_boundary_manifest_missing",
                    (
                        f"{CRITIQUE_REVIEWER_POOL_BOUNDARY_FILE} must emit "
                        "synchronous reviewer pool versus calibrated reviewer scope"
                    ),
                    "critique_reviewer_pool",
                )
            ]
    report = validate_critique_reviewer_pool_boundary(recordset)
    return [
        PaperManifestIssue(
            f"critique_reviewer_pool_boundary_{issue.code}",
            issue.message,
            "critique_reviewer_pool",
        )
        for issue in report.issues
    ]


def _validate_prompt_section_packing_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PROMPT_SECTION_PACKING_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = prompt_section_packing_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "prompt_section_packing_boundary_manifest_missing",
                    (
                        f"{PROMPT_SECTION_PACKING_BOUNDARY_FILE} must emit "
                        "mutation section-packing versus all-role provider-token scope"
                    ),
                    "prompt_section_packing",
                )
            ]
    report = validate_prompt_section_packing_boundary(recordset)
    return [
        PaperManifestIssue(
            f"prompt_section_packing_boundary_{issue.code}",
            issue.message,
            "prompt_section_packing",
        )
        for issue in report.issues
    ]


def _validate_stochastic_prompt_format_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / STOCHASTIC_PROMPT_FORMAT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = stochastic_prompt_format_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "stochastic_prompt_format_boundary_manifest_missing",
                    (
                        f"{STOCHASTIC_PROMPT_FORMAT_BOUNDARY_FILE} must emit "
                        "effective config distribution versus separate-source scope"
                    ),
                    "stochastic_prompt_format",
                )
            ]
    report = validate_stochastic_prompt_format_boundary(recordset)
    return [
        PaperManifestIssue(
            f"stochastic_prompt_format_boundary_{issue.code}",
            issue.message,
            "stochastic_prompt_format",
        )
        for issue in report.issues
    ]


def _validate_documentation_truthfulness_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / DOCUMENTATION_TRUTHFULNESS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = documentation_truthfulness_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "documentation_truthfulness_boundary_manifest_missing",
                    (
                        f"{DOCUMENTATION_TRUTHFULNESS_BOUNDARY_FILE} must emit "
                        "cross-document guards versus semantic claim-proof scope"
                    ),
                    "documentation_truthfulness",
                )
            ]
    report = validate_documentation_truthfulness_boundary(recordset)
    return [
        PaperManifestIssue(
            f"documentation_truthfulness_boundary_{issue.code}",
            issue.message,
            "documentation_truthfulness",
        )
        for issue in report.issues
    ]


def _validate_documentation_claim_inventory(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / DOCUMENTATION_CLAIM_INVENTORY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = documentation_claim_inventory_record(root_path)
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "documentation_claim_inventory_manifest_missing",
                    (
                        f"{DOCUMENTATION_CLAIM_INVENTORY_FILE} must emit "
                        "top-level README/ROADMAP claim anchors versus semantic proof scope"
                    ),
                    "documentation_claim_inventory",
                )
            ]
    report = validate_documentation_claim_inventory(recordset, root=root_path)
    return [
        PaperManifestIssue(
            f"documentation_claim_inventory_{issue.code}",
            issue.message,
            "documentation_claim_inventory",
        )
        for issue in report.issues
    ]


def _validate_roadmap_readiness_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_READINESS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = roadmap_readiness_boundary_record(root_path)
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_readiness_boundary_manifest_missing",
                    (
                        f"{ROADMAP_READINESS_BOUNDARY_FILE} must emit "
                        "weighted TODO-ledger readiness versus semantic AlphaEvolve readiness"
                    ),
                    "roadmap_readiness",
                )
            ]
    report = validate_roadmap_readiness_boundary(recordset, root=root_path)
    return [
        PaperManifestIssue(
            f"roadmap_readiness_boundary_{issue.code}",
            issue.message,
            "roadmap_readiness",
        )
        for issue in report.issues
    ]


def _validate_roadmap_claim_evidence_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_CLAIM_EVIDENCE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_claim_evidence_boundary_manifest_missing",
                    (
                        f"{ROADMAP_CLAIM_EVIDENCE_BOUNDARY_FILE} must emit "
                        "ROADMAP current-state and priority claim evidence metadata"
                    ),
                    "roadmap_claim_evidence",
                )
            ]
        return []
    report = validate_roadmap_claim_evidence_boundary(recordset, root=root_path)
    return [
        PaperManifestIssue(
            f"roadmap_claim_evidence_boundary_{issue.code}",
            issue.message,
            "roadmap_claim_evidence",
        )
        for issue in report.issues
    ]


def _validate_todo_ledger_ownership_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / TODO_LEDGER_OWNERSHIP_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = todo_ledger_ownership_boundary_record(root_path)
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "todo_ledger_ownership_boundary_manifest_missing",
                    (
                        f"{TODO_LEDGER_OWNERSHIP_BOUNDARY_FILE} must emit "
                        "TODO-ledger ownership versus canonical gap-deduplication scope"
                    ),
                    "todo_ledger_ownership",
                )
            ]
    report = validate_todo_ledger_ownership_boundary(recordset, root=root_path)
    return [
        PaperManifestIssue(
            f"todo_ledger_ownership_boundary_{issue.code}",
            issue.message,
            "todo_ledger_ownership",
        )
        for issue in report.issues
    ]


def _validate_todo_canonical_gap_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / TODO_CANONICAL_GAP_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "todo_canonical_gap_boundary_manifest_missing",
                    (
                        f"{TODO_CANONICAL_GAP_BOUNDARY_FILE} must emit "
                        "TODO canonical-gap readiness metadata"
                    ),
                    "todo_canonical_gap",
                )
            ]
        return []
    report = validate_todo_canonical_gap_boundary(recordset, root=root_path)
    return [
        PaperManifestIssue(
            f"todo_canonical_gap_boundary_{issue.code}",
            issue.message,
            "todo_canonical_gap",
        )
        for issue in report.issues
    ]


def _validate_roadmap_source_span_disposition_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_SOURCE_SPAN_DISPOSITION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = roadmap_source_span_disposition_boundary_record(root_path)
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_source_span_disposition_boundary_manifest_missing",
                    (
                        f"{ROADMAP_SOURCE_SPAN_DISPOSITION_BOUNDARY_FILE} must emit "
                        "ROADMAP core source-span dispositions versus exhaustive coverage scope"
                    ),
                    "roadmap_source_span_disposition",
                )
            ]
    report = validate_roadmap_source_span_disposition_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_source_span_disposition_boundary_{issue.code}",
            issue.message,
            "roadmap_source_span_disposition",
        )
        for issue in report.issues
    ]


def _validate_roadmap_source_span_coverage_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_SOURCE_SPAN_COVERAGE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_source_span_coverage_boundary_manifest_missing",
                    (
                        f"{ROADMAP_SOURCE_SPAN_COVERAGE_BOUNDARY_FILE} must emit "
                        "ROADMAP AlphaEvolve source-span coverage metadata"
                    ),
                    "roadmap_source_span_coverage",
                )
            ]
        return []
    report = validate_roadmap_source_span_coverage_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_source_span_coverage_boundary_{issue.code}",
            issue.message,
            "roadmap_source_span_coverage",
        )
        for issue in report.issues
    ]


def _validate_roadmap_non_goal_contradiction_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_NON_GOAL_CONTRADICTION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = roadmap_non_goal_contradiction_boundary_record(root_path)
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_non_goal_contradiction_boundary_manifest_missing",
                    (
                        f"{ROADMAP_NON_GOAL_CONTRADICTION_BOUNDARY_FILE} must emit "
                        "ROADMAP non-goal inventory and bounded contradiction checks"
                    ),
                    "roadmap_non_goal_contradiction",
                )
            ]
    report = validate_roadmap_non_goal_contradiction_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_non_goal_contradiction_boundary_{issue.code}",
            issue.message,
            "roadmap_non_goal_contradiction",
        )
        for issue in report.issues
    ]


def _validate_roadmap_non_goal_drift_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_NON_GOAL_DRIFT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = roadmap_non_goal_drift_boundary_record(root_path)
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_non_goal_drift_boundary_manifest_missing",
                    (
                        f"{ROADMAP_NON_GOAL_DRIFT_BOUNDARY_FILE} must emit "
                        "ROADMAP non-goal drift and promotion readiness metadata"
                    ),
                    "roadmap_non_goal_drift",
                )
            ]
    report = validate_roadmap_non_goal_drift_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_non_goal_drift_boundary_{issue.code}",
            issue.message,
            "roadmap_non_goal_drift",
        )
        for issue in report.issues
    ]


def _validate_roadmap_good_first_followups_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_GOOD_FIRST_FOLLOWUPS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_good_first_followups_boundary_manifest_missing",
                    (
                        f"{ROADMAP_GOOD_FIRST_FOLLOWUPS_BOUNDARY_FILE} must emit "
                        "ROADMAP Good First Follow-Ups priority mapping"
                    ),
                    "roadmap_good_first_followups",
                )
            ]
        return []
    report = validate_roadmap_good_first_followups_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_good_first_followups_boundary_{issue.code}",
            issue.message,
            "roadmap_good_first_followups",
        )
        for issue in report.issues
    ]


def _validate_roadmap_good_first_freshness_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_GOOD_FIRST_FRESHNESS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = roadmap_good_first_freshness_boundary_record(root_path)
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_good_first_freshness_boundary_manifest_missing",
                    (
                        f"{ROADMAP_GOOD_FIRST_FRESHNESS_BOUNDARY_FILE} must "
                        "emit ROADMAP Good First Follow-Ups freshness metadata"
                    ),
                    "roadmap_good_first_freshness",
                )
            ]
    report = validate_roadmap_good_first_freshness_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_good_first_freshness_boundary_{issue.code}",
            issue.message,
            "roadmap_good_first_freshness",
        )
        for issue in report.issues
    ]


def _validate_roadmap_phase_sequence_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_PHASE_SEQUENCE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_phase_sequence_boundary_manifest_missing",
                    (
                        f"{ROADMAP_PHASE_SEQUENCE_BOUNDARY_FILE} must emit "
                        "ROADMAP phase and major-section sequencing metadata"
                    ),
                    "roadmap_phase_sequence",
                )
            ]
        return []
    report = validate_roadmap_phase_sequence_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_phase_sequence_boundary_{issue.code}",
            issue.message,
            "roadmap_phase_sequence",
        )
        for issue in report.issues
    ]


def _validate_roadmap_phase_freshness_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_PHASE_FRESHNESS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_phase_freshness_boundary_manifest_missing",
                    (
                        f"{ROADMAP_PHASE_FRESHNESS_BOUNDARY_FILE} must emit "
                        "ROADMAP phase freshness metadata"
                    ),
                    "roadmap_phase_freshness",
                )
            ]
        return []
    report = validate_roadmap_phase_freshness_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_phase_freshness_boundary_{issue.code}",
            issue.message,
            "roadmap_phase_freshness",
        )
        for issue in report.issues
    ]


def _validate_roadmap_operational_maturity_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_OPERATIONAL_MATURITY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_operational_maturity_boundary_manifest_missing",
                    (
                        f"{ROADMAP_OPERATIONAL_MATURITY_BOUNDARY_FILE} must emit "
                        "ROADMAP operational maturity criteria metadata"
                    ),
                    "roadmap_operational_maturity",
                )
            ]
        return []
    report = validate_roadmap_operational_maturity_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_operational_maturity_boundary_{issue.code}",
            issue.message,
            "roadmap_operational_maturity",
        )
        for issue in report.issues
    ]


def _validate_roadmap_operational_readiness_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_OPERATIONAL_READINESS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_operational_readiness_boundary_manifest_missing",
                    (
                        f"{ROADMAP_OPERATIONAL_READINESS_BOUNDARY_FILE} must "
                        "emit ROADMAP operational readiness metadata"
                    ),
                    "roadmap_operational_readiness",
                )
            ]
        return []
    report = validate_roadmap_operational_readiness_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_operational_readiness_boundary_{issue.code}",
            issue.message,
            "roadmap_operational_readiness",
        )
        for issue in report.issues
    ]


def _validate_roadmap_representative_benchmark_portfolio_boundary(
    root_path: Path,
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_REPRESENTATIVE_BENCHMARK_PORTFOLIO_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_representative_benchmark_portfolio_boundary_manifest_missing",
                    (
                        f"{ROADMAP_REPRESENTATIVE_BENCHMARK_PORTFOLIO_BOUNDARY_FILE} "
                        "must emit ROADMAP representative benchmark portfolio metadata"
                    ),
                    "roadmap_representative_benchmark_portfolio",
                )
            ]
        return []
    report = validate_roadmap_representative_benchmark_portfolio_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_representative_benchmark_portfolio_boundary_{issue.code}",
            issue.message,
            "roadmap_representative_benchmark_portfolio",
        )
        for issue in report.issues
    ]


def _validate_roadmap_benchmark_portfolio_readiness_boundary(
    root_path: Path,
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_BENCHMARK_PORTFOLIO_READINESS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_benchmark_portfolio_readiness_boundary_manifest_missing",
                    (
                        f"{ROADMAP_BENCHMARK_PORTFOLIO_READINESS_BOUNDARY_FILE} "
                        "must emit ROADMAP representative benchmark portfolio "
                        "readiness metadata"
                    ),
                    "roadmap_benchmark_portfolio_readiness",
                )
            ]
        return []
    report = validate_roadmap_benchmark_portfolio_readiness_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_benchmark_portfolio_readiness_boundary_{issue.code}",
            issue.message,
            "roadmap_benchmark_portfolio_readiness",
        )
        for issue in report.issues
    ]


def _validate_roadmap_plugin_extensibility_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_PLUGIN_EXTENSIBILITY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_plugin_extensibility_boundary_manifest_missing",
                    (
                        f"{ROADMAP_PLUGIN_EXTENSIBILITY_BOUNDARY_FILE} must emit "
                        "ROADMAP plugin extensibility metadata"
                    ),
                    "roadmap_plugin_extensibility",
                )
            ]
        return []
    report = validate_roadmap_plugin_extensibility_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_plugin_extensibility_boundary_{issue.code}",
            issue.message,
            "roadmap_plugin_extensibility",
        )
        for issue in report.issues
    ]


def _validate_roadmap_plugin_readiness_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_PLUGIN_READINESS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_plugin_readiness_boundary_manifest_missing",
                    (
                        f"{ROADMAP_PLUGIN_READINESS_BOUNDARY_FILE} must emit "
                        "ROADMAP plugin readiness metadata"
                    ),
                    "roadmap_plugin_readiness",
                )
            ]
        return []
    report = validate_roadmap_plugin_readiness_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_plugin_readiness_boundary_{issue.code}",
            issue.message,
            "roadmap_plugin_readiness",
        )
        for issue in report.issues
    ]


def _validate_roadmap_backend_scheduling_critique_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_BACKEND_SCHEDULING_CRITIQUE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_backend_scheduling_critique_boundary_manifest_missing",
                    (
                        f"{ROADMAP_BACKEND_SCHEDULING_CRITIQUE_BOUNDARY_FILE} "
                        "must emit ROADMAP backend scheduling and critique metadata"
                    ),
                    "roadmap_backend_scheduling_critique",
                )
            ]
        return []
    report = validate_roadmap_backend_scheduling_critique_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_backend_scheduling_critique_boundary_{issue.code}",
            issue.message,
            "roadmap_backend_scheduling_critique",
        )
        for issue in report.issues
    ]


def _validate_roadmap_backend_control_plane_readiness_boundary(
    root_path: Path,
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_BACKEND_CONTROL_PLANE_READINESS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_backend_control_plane_readiness_boundary_manifest_missing",
                    (
                        f"{ROADMAP_BACKEND_CONTROL_PLANE_READINESS_BOUNDARY_FILE} "
                        "must emit ROADMAP backend control-plane readiness metadata"
                    ),
                    "roadmap_backend_control_plane_readiness",
                )
            ]
        return []
    report = validate_roadmap_backend_control_plane_readiness_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_backend_control_plane_readiness_boundary_{issue.code}",
            issue.message,
            "roadmap_backend_control_plane_readiness",
        )
        for issue in report.issues
    ]


def _validate_roadmap_async_resumable_runtime_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_ASYNC_RESUMABLE_RUNTIME_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_async_resumable_runtime_boundary_manifest_missing",
                    (
                        f"{ROADMAP_ASYNC_RESUMABLE_RUNTIME_BOUNDARY_FILE} must emit "
                        "ROADMAP async and resumable runtime metadata"
                    ),
                    "roadmap_async_resumable_runtime",
                )
            ]
        return []
    report = validate_roadmap_async_resumable_runtime_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_async_resumable_runtime_boundary_{issue.code}",
            issue.message,
            "roadmap_async_resumable_runtime",
        )
        for issue in report.issues
    ]


def _validate_roadmap_async_runtime_readiness_boundary(
    root_path: Path,
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_ASYNC_RUNTIME_READINESS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_async_runtime_readiness_boundary_manifest_missing",
                    (
                        f"{ROADMAP_ASYNC_RUNTIME_READINESS_BOUNDARY_FILE} "
                        "must emit ROADMAP async runtime readiness metadata"
                    ),
                    "roadmap_async_runtime_readiness",
                )
            ]
        return []
    report = validate_roadmap_async_runtime_readiness_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_async_runtime_readiness_boundary_{issue.code}",
            issue.message,
            "roadmap_async_runtime_readiness",
        )
        for issue in report.issues
    ]


def _validate_roadmap_prompt_context_system_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_PROMPT_CONTEXT_SYSTEM_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_prompt_context_system_boundary_manifest_missing",
                    (
                        f"{ROADMAP_PROMPT_CONTEXT_SYSTEM_BOUNDARY_FILE} must emit "
                        "ROADMAP prompt/context-system metadata"
                    ),
                    "roadmap_prompt_context_system",
                )
            ]
        return []
    report = validate_roadmap_prompt_context_system_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_prompt_context_system_boundary_{issue.code}",
            issue.message,
            "roadmap_prompt_context_system",
        )
        for issue in report.issues
    ]


def _validate_roadmap_evaluation_cascade_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_EVALUATION_CASCADE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_evaluation_cascade_boundary_manifest_missing",
                    (
                        f"{ROADMAP_EVALUATION_CASCADE_BOUNDARY_FILE} must emit "
                        "ROADMAP evaluation-cascade metadata"
                    ),
                    "roadmap_evaluation_cascade",
                )
            ]
        return []
    report = validate_roadmap_evaluation_cascade_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_evaluation_cascade_boundary_{issue.code}",
            issue.message,
            "roadmap_evaluation_cascade",
        )
        for issue in report.issues
    ]


def _validate_roadmap_candidate_workspace_fidelity_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_CANDIDATE_WORKSPACE_FIDELITY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_candidate_workspace_fidelity_boundary_manifest_missing",
                    (
                        f"{ROADMAP_CANDIDATE_WORKSPACE_FIDELITY_BOUNDARY_FILE} must emit "
                        "ROADMAP candidate-workspace fidelity metadata"
                    ),
                    "roadmap_candidate_workspace_fidelity",
                )
            ]
        return []
    report = validate_roadmap_candidate_workspace_fidelity_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_candidate_workspace_fidelity_boundary_{issue.code}",
            issue.message,
            "roadmap_candidate_workspace_fidelity",
        )
        for issue in report.issues
    ]


def _validate_roadmap_multi_objective_search_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ROADMAP_MULTI_OBJECTIVE_SEARCH_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "roadmap_multi_objective_search_boundary_manifest_missing",
                    (
                        f"{ROADMAP_MULTI_OBJECTIVE_SEARCH_BOUNDARY_FILE} must emit "
                        "ROADMAP multi-objective search metadata"
                    ),
                    "roadmap_multi_objective_search",
                )
            ]
        return []
    report = validate_roadmap_multi_objective_search_boundary(
        recordset,
        root=root_path,
    )
    return [
        PaperManifestIssue(
            f"roadmap_multi_objective_search_boundary_{issue.code}",
            issue.message,
            "roadmap_multi_objective_search",
        )
        for issue in report.issues
    ]


def _validate_implementation_evidence_map_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / IMPLEMENTATION_EVIDENCE_MAP_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = implementation_evidence_map_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "implementation_evidence_map_boundary_manifest_missing",
                    (
                        f"{IMPLEMENTATION_EVIDENCE_MAP_BOUNDARY_FILE} must emit "
                        "core AlphaEvolve requirement anchors versus exhaustive audit scope"
                    ),
                    "implementation_evidence_map",
                )
            ]
    report = validate_implementation_evidence_map_boundary(recordset)
    return [
        PaperManifestIssue(
            f"implementation_evidence_map_boundary_{issue.code}",
            issue.message,
            "implementation_evidence_map",
        )
        for issue in report.issues
    ]


def _validate_status_claim_inventory(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / STATUS_CLAIM_INVENTORY_FILE
    if not sidecar_path.exists():
        if not is_repo_root:
            return []
        return [
            PaperManifestIssue(
                "status_claim_inventory_missing",
                (
                    f"{STATUS_CLAIM_INVENTORY_FILE} must record every "
                    "papers/README.md implementation-status row"
                ),
                "status_claim_inventory",
            )
        ]
    try:
        data = json.loads(sidecar_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [
            PaperManifestIssue(
                "status_claim_inventory_unreadable",
                _manifest_diagnostic(sidecar_path, root_path, exc),
                "status_claim_inventory",
            )
        ]
    if not isinstance(data, dict):
        return [
            PaperManifestIssue(
                "status_claim_inventory_schema",
                "status claim inventory must be a JSON object",
                "status_claim_inventory",
            )
        ]

    expected = paper_status_claim_inventory_record(root_path)
    issues: list[PaperManifestIssue] = []
    checks = (
        ("schema", "status claim inventory schema changed"),
        ("inventory_status", "status claim inventory status changed"),
        ("source_path", "status claim inventory source path changed"),
        ("row_count", "status claim inventory row count drifted"),
        ("row_ids", "status claim inventory row ids drifted"),
        ("status_class_counts", "status claim inventory status-class counts drifted"),
        ("unique_local_artifact_paths", "status claim inventory unique local artifact paths drifted"),
        ("unique_local_artifact_count", "status claim inventory unique local artifact count drifted"),
        ("local_artifact_mention_record_count", "status claim inventory local artifact mention count drifted"),
        ("missing_local_artifact_paths", "status claim inventory missing local artifact paths drifted"),
        ("artifact_existence_status", "status claim inventory artifact existence status drifted"),
        ("unique_todo_evidence_paths", "status claim inventory unique TODO evidence paths drifted"),
        ("unique_todo_evidence_path_count", "status claim inventory unique TODO evidence path count drifted"),
        ("todo_evidence_path_mention_count", "status claim inventory TODO evidence path mention count drifted"),
        ("missing_todo_evidence_paths", "status claim inventory missing TODO evidence paths drifted"),
        ("todo_evidence_status", "status claim inventory TODO evidence status drifted"),
        (
            "local_artifacts_missing_from_todo_evidence",
            "status claim inventory TODO content local artifact mentions drifted",
        ),
        (
            "todo_content_artifact_mention_record_count",
            "status claim inventory TODO content local artifact mention count drifted",
        ),
        (
            "todo_content_row_specific_block_record_count",
            "status claim inventory TODO content block record count drifted",
        ),
        (
            "todo_content_matched_source_tokens",
            "status claim inventory TODO content matched source tokens drifted",
        ),
        (
            "todo_content_matched_source_token_count",
            "status claim inventory TODO content matched source token count drifted",
        ),
        ("todo_content_evidence_status", "status claim inventory TODO content status drifted"),
        (
            "phrase_local_artifacts_missing_from_todo_evidence",
            "status claim inventory phrase TODO content local artifact mentions drifted",
        ),
        (
            "phrase_local_artifact_mention_record_count",
            "status claim inventory phrase local artifact mention count drifted",
        ),
        (
            "phrase_todo_content_block_record_count",
            "status claim inventory phrase TODO content block count drifted",
        ),
        ("phrase_todo_content_evidence_status", "status claim inventory phrase TODO content status drifted"),
        ("absence_phrase_count", "status claim inventory absence phrase count drifted"),
        ("absence_phrase_ids", "status claim inventory absence phrase ids drifted"),
        ("absence_signal_record_count", "status claim inventory absence signal record count drifted"),
        ("absence_signal_terms", "status claim inventory absence signal terms drifted"),
        ("absence_signal_inventory_status", "status claim inventory absence signal status drifted"),
        ("missing_evidence", "status claim inventory missing-evidence boundary drifted"),
        ("claim_boundary", "status claim inventory claim boundary drifted"),
        ("rows", "status claim inventory rows drifted from papers/README.md"),
    )
    for key, message in checks:
        if data.get(key) != expected[key]:
            issues.append(
                PaperManifestIssue(
                    f"status_claim_inventory_{key}_mismatch",
                    message,
                    "status_claim_inventory",
                )
            )
    issues.extend(_validate_status_claim_inventory_readme_summary(root_path, data))
    issues.extend(_validate_status_claim_inventory_status_ledger_summary(root_path, data))
    for missing_path in expected["missing_local_artifact_paths"]:
        issues.append(
            PaperManifestIssue(
                "status_claim_inventory_missing_local_artifact",
                "implementation-status row cites a missing local artifact path",
                _safe_manifest_label(str(missing_path)),
            )
        )
    for missing_path in expected["missing_todo_evidence_paths"]:
        issues.append(
            PaperManifestIssue(
                "status_claim_inventory_missing_todo_evidence_path",
                "implementation-status row cites a missing TODO evidence path",
                _safe_manifest_label(str(missing_path)),
            )
        )
    for missing_path in expected["local_artifacts_missing_from_todo_evidence"]:
        issues.append(
            PaperManifestIssue(
                "status_claim_inventory_local_artifact_missing_from_todo_evidence",
                "implementation-status local artifact path is not mentioned in row-specific TODO evidence",
                _safe_manifest_label(str(missing_path)),
            )
        )
    for missing_path in expected["phrase_local_artifacts_missing_from_todo_evidence"]:
        issues.append(
            PaperManifestIssue(
                "status_claim_inventory_phrase_local_artifact_missing_from_todo_evidence",
                "implementation-status phrase local artifact path is not mentioned in row-specific TODO evidence",
                _safe_manifest_label(str(missing_path)),
            )
        )
    return issues


def _validate_status_claim_inventory_readme_summary(
    root_path: Path,
    inventory: dict[str, Any],
) -> list[PaperManifestIssue]:
    readme_path = root_path / "papers" / "README.md"
    try:
        text = readme_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [
            PaperManifestIssue(
                "status_claim_inventory_readme_summary_unreadable",
                _manifest_diagnostic(readme_path, root_path, exc),
                "status_claim_inventory",
            )
        ]
    if STATUS_CLAIM_INVENTORY_FILE not in text:
        return []
    summary_start = text.find(f"`{STATUS_CLAIM_INVENTORY_FILE}`")
    if summary_start < 0:
        summary_start = text.find(STATUS_CLAIM_INVENTORY_FILE)
    line_start = text.rfind("\n- ", 0, summary_start)
    if line_start < 0:
        line_start = text.rfind("\n", 0, summary_start)
    block_start = 0 if line_start < 0 else line_start + 1
    next_bullet = text.find("\n- `papers/", summary_start + len(STATUS_CLAIM_INVENTORY_FILE))
    block_end = len(text) if next_bullet < 0 else next_bullet + 1
    summary_text = text[block_start:block_end]

    issues: list[PaperManifestIssue] = []
    for key, pattern in STATUS_CLAIM_INVENTORY_README_SUMMARY_PATTERNS:
        match = pattern.search(summary_text)
        if match is None:
            continue
        documented = int(match.group(1))
        current = inventory.get(key)
        if documented != current:
            issues.append(
                PaperManifestIssue(
                    f"status_claim_inventory_readme_summary_{key}_mismatch",
                    (
                        "papers/README.md status_claim_inventory summary "
                        f"documents {key}={documented} but sidecar has {current}"
                    ),
                    "status_claim_inventory",
                )
            )
    return issues


def _validate_status_claim_inventory_status_ledger_summary(
    root_path: Path,
    inventory: dict[str, Any],
) -> list[PaperManifestIssue]:
    status_path = root_path / STATUS_LEDGER_FILE
    if not status_path.exists():
        return []
    try:
        text = status_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [
            PaperManifestIssue(
                "status_claim_inventory_status_ledger_summary_unreadable",
                _manifest_diagnostic(status_path, root_path, exc),
                "status_claim_inventory",
            )
        ]
    if STATUS_CLAIM_INVENTORY_FILE not in text:
        return []
    summary_marker = "Paper-index implementation-status validation now records"
    summary_start = text.find(summary_marker)
    if summary_start < 0:
        return []
    next_bullet = text.find("\n-", summary_start + len(summary_marker))
    summary_text = text[summary_start:] if next_bullet < 0 else text[summary_start:next_bullet]

    issues: list[PaperManifestIssue] = []
    for key, pattern in STATUS_CLAIM_INVENTORY_README_SUMMARY_PATTERNS:
        match = pattern.search(summary_text)
        if match is None:
            continue
        documented = _documented_summary_count(match.group(1))
        current = inventory.get(key)
        if documented != current:
            issues.append(
                PaperManifestIssue(
                    f"status_claim_inventory_status_ledger_summary_{key}_mismatch",
                    (
                        "docs/status.md status_claim_inventory summary "
                        f"documents {key}={documented} but sidecar has {current}"
                    ),
                    "status_claim_inventory",
                )
            )
    return issues


def _validate_benchmark_coverage_inventory(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / BENCHMARK_COVERAGE_INVENTORY_FILE
    if not sidecar_path.exists():
        if not is_repo_root:
            return []
        return [
            PaperManifestIssue(
                "benchmark_coverage_inventory_missing",
                (
                    f"{BENCHMARK_COVERAGE_INVENTORY_FILE} must record "
                    "papers/README.md Implemented benchmark coverage bullets"
                ),
                "benchmark_coverage_inventory",
            )
        ]
    try:
        data = json.loads(sidecar_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [
            PaperManifestIssue(
                "benchmark_coverage_inventory_unreadable",
                _manifest_diagnostic(sidecar_path, root_path, exc),
                "benchmark_coverage_inventory",
            )
        ]
    if not isinstance(data, dict):
        return [
            PaperManifestIssue(
                "benchmark_coverage_inventory_schema",
                "benchmark coverage inventory must be a JSON object",
                "benchmark_coverage_inventory",
            )
        ]

    expected = paper_benchmark_coverage_inventory_record(root_path)
    issues: list[PaperManifestIssue] = []
    checks = (
        ("schema", "benchmark coverage inventory schema changed"),
        ("inventory_status", "benchmark coverage inventory status changed"),
        ("source_path", "benchmark coverage inventory source path changed"),
        ("implemented_bullet_count", "benchmark coverage implemented-bullet count drifted"),
        ("implemented_bullet_ids", "benchmark coverage implemented-bullet ids drifted"),
        ("source_ids_mentioned", "benchmark coverage source ids drifted"),
        ("source_id_mention_count", "benchmark coverage source id count drifted"),
        ("source_token_match_record_count", "benchmark coverage source-token match count drifted"),
        ("source_token_coverage_status", "benchmark coverage source-token status drifted"),
        ("implemented_bullet_source_span_status", "benchmark coverage bullet source-span status drifted"),
        (
            "implemented_bullet_mention_source_span_status",
            "benchmark coverage mention source-span status drifted",
        ),
        ("unique_local_artifact_paths", "benchmark coverage unique local artifact paths drifted"),
        ("unique_local_artifact_count", "benchmark coverage unique local artifact count drifted"),
        ("local_artifact_mention_record_count", "benchmark coverage local artifact mention count drifted"),
        ("missing_local_artifact_paths", "benchmark coverage missing local artifact paths drifted"),
        ("artifact_existence_status", "benchmark coverage artifact existence status drifted"),
        ("limitation_bullet_count", "benchmark coverage limitation bullet count drifted"),
        ("limitation_bullet_ids", "benchmark coverage limitation bullet ids drifted"),
        ("limitation_signal_record_count", "benchmark coverage limitation signal record count drifted"),
        ("limitation_signal_terms", "benchmark coverage limitation signal terms drifted"),
        ("limitation_signal_inventory_status", "benchmark coverage limitation signal status drifted"),
        ("not_implemented_contradiction_count", "benchmark coverage contradiction count drifted"),
        ("not_implemented_contradiction_bullet_ids", "benchmark coverage contradiction ids drifted"),
        ("missing_evidence", "benchmark coverage missing-evidence boundary drifted"),
        ("claim_boundary", "benchmark coverage claim boundary drifted"),
        ("implemented_bullets", "benchmark coverage implemented bullets drifted from papers/README.md"),
    )
    for key, message in checks:
        if data.get(key) != expected[key]:
            issues.append(
                PaperManifestIssue(
                    f"benchmark_coverage_inventory_{key}_mismatch",
                    message,
                    "benchmark_coverage_inventory",
                )
            )
    issues.extend(_validate_benchmark_coverage_readme_summary(root_path, data))
    for missing_path in expected["missing_local_artifact_paths"]:
        issues.append(
            PaperManifestIssue(
                "benchmark_coverage_inventory_missing_local_artifact",
                "implemented benchmark coverage bullet cites a missing local artifact path",
                _safe_manifest_label(str(missing_path)),
            )
        )
    return issues


def _validate_benchmark_coverage_readme_summary(
    root_path: Path,
    inventory: dict[str, Any],
) -> list[PaperManifestIssue]:
    readme_path = root_path / "papers" / "README.md"
    try:
        text = readme_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [
            PaperManifestIssue(
                "benchmark_coverage_inventory_readme_summary_unreadable",
                _manifest_diagnostic(readme_path, root_path, exc),
                "benchmark_coverage_inventory",
            )
        ]
    if BENCHMARK_COVERAGE_INVENTORY_FILE not in text:
        return []
    summary_start = text.find(f"`{BENCHMARK_COVERAGE_INVENTORY_FILE}`")
    if summary_start < 0:
        summary_start = text.find(BENCHMARK_COVERAGE_INVENTORY_FILE)
    line_start = text.rfind("\n- ", 0, summary_start)
    if line_start < 0:
        line_start = text.rfind("\n", 0, summary_start)
    block_start = 0 if line_start < 0 else line_start + 1
    next_bullet = text.find("\n- `papers/", summary_start + len(BENCHMARK_COVERAGE_INVENTORY_FILE))
    block_end = len(text) if next_bullet < 0 else next_bullet + 1
    summary_text = text[block_start:block_end]

    issues: list[PaperManifestIssue] = []
    for key, pattern in BENCHMARK_COVERAGE_README_SUMMARY_PATTERNS:
        match = pattern.search(summary_text)
        if match is None:
            continue
        documented = _documented_summary_count(match.group(1))
        if key == "missing_local_artifact_path_count":
            current = len(inventory.get("missing_local_artifact_paths") or [])
        else:
            current = inventory.get(key)
        if documented != current:
            issues.append(
                PaperManifestIssue(
                    f"benchmark_coverage_inventory_readme_summary_{key}_mismatch",
                    (
                        "papers/README.md benchmark_coverage_inventory summary "
                        f"documents {key}={documented} but sidecar has {current}"
                    ),
                    "benchmark_coverage_inventory",
                )
            )
    return issues


def _documented_summary_count(value: str) -> int:
    normalized = value.strip().strip("`").lower()
    if normalized == "zero":
        return 0
    return int(normalized)


def _validate_release_artifact_reproducibility_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / RELEASE_ARTIFACT_REPRODUCIBILITY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = release_artifact_reproducibility_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "release_artifact_reproducibility_boundary_manifest_missing",
                    (
                        f"{RELEASE_ARTIFACT_REPRODUCIBILITY_BOUNDARY_FILE} must emit "
                        "release-artifact reproducibility availability"
                    ),
                    "release_artifact_reproducibility",
                )
            ]
    report = validate_release_artifact_reproducibility_boundary(recordset)
    return [
        PaperManifestIssue(
            f"release_artifact_reproducibility_boundary_{issue.code}",
            issue.message,
            "release_artifact_reproducibility",
        )
        for issue in report.issues
    ]


def _validate_related_work_taxonomy_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / RELATED_WORK_TAXONOMY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = related_work_taxonomy_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "related_work_taxonomy_boundary_manifest_missing",
                    (
                        f"{RELATED_WORK_TAXONOMY_BOUNDARY_FILE} must emit "
                        "flat paper-index versus Related Work taxonomy scope"
                    ),
                    "related_work_taxonomy",
                )
            ]
    report = validate_related_work_taxonomy_boundary(recordset)
    return [
        PaperManifestIssue(
            f"related_work_taxonomy_boundary_{issue.code}",
            issue.message,
            "related_work_taxonomy",
        )
        for issue in report.issues
    ]


def _validate_acknowledgement_role_provenance_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ACKNOWLEDGEMENT_ROLE_PROVENANCE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = acknowledgement_role_provenance_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "acknowledgement_role_provenance_boundary_manifest_missing",
                    (
                        f"{ACKNOWLEDGEMENT_ROLE_PROVENANCE_BOUNDARY_FILE} must emit "
                        "acknowledgement-role provenance availability"
                    ),
                    "acknowledgement_role_provenance",
                )
            ]
    report = validate_acknowledgement_role_provenance_boundary(recordset)
    return [
        PaperManifestIssue(
            f"acknowledgement_role_provenance_boundary_{issue.code}",
            issue.message,
            "acknowledgement_role_provenance",
        )
        for issue in report.issues
    ]


def _validate_paper_author_metadata_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PAPER_AUTHOR_METADATA_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = paper_author_metadata_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "paper_author_metadata_boundary_manifest_missing",
                    (
                        f"{PAPER_AUTHOR_METADATA_BOUNDARY_FILE} must emit "
                        "publication-author metadata availability"
                    ),
                    "paper_author_metadata",
                )
            ]
    report = validate_paper_author_metadata_boundary(recordset)
    return [
        PaperManifestIssue(
            f"paper_author_metadata_boundary_{issue.code}",
            issue.message,
            "paper_author_metadata",
        )
        for issue in report.issues
    ]


def _validate_title_page_affiliation_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / TITLE_PAGE_AFFILIATION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = title_page_affiliation_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "title_page_affiliation_boundary_manifest_missing",
                    (
                        f"{TITLE_PAGE_AFFILIATION_BOUNDARY_FILE} must emit "
                        "title-page affiliation metadata availability"
                    ),
                    "title_page_affiliation",
                )
            ]
    report = validate_title_page_affiliation_boundary(recordset)
    return [
        PaperManifestIssue(
            f"title_page_affiliation_boundary_{issue.code}",
            issue.message,
            "title_page_affiliation",
        )
        for issue in report.issues
    ]


def _validate_system_contribution_provenance_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / SYSTEM_CONTRIBUTION_PROVENANCE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = system_contribution_provenance_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "system_contribution_provenance_boundary_manifest_missing",
                    (
                        f"{SYSTEM_CONTRIBUTION_PROVENANCE_BOUNDARY_FILE} must emit "
                        "system-contribution provenance availability"
                    ),
                    "system_contribution_provenance",
                )
            ]
    report = validate_system_contribution_provenance_boundary(recordset)
    return [
        PaperManifestIssue(
            f"system_contribution_provenance_boundary_{issue.code}",
            issue.message,
            "system_contribution_provenance",
        )
        for issue in report.issues
    ]


def _validate_initial_program_idea_provenance_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / INITIAL_PROGRAM_IDEA_PROVENANCE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = initial_program_idea_provenance_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "initial_program_idea_provenance_boundary_manifest_missing",
                    (
                        f"{INITIAL_PROGRAM_IDEA_PROVENANCE_BOUNDARY_FILE} must emit "
                        "initial-program idea provenance availability"
                    ),
                    "initial_program_idea_provenance",
                )
            ]
    report = validate_initial_program_idea_provenance_boundary(recordset)
    return [
        PaperManifestIssue(
            f"initial_program_idea_provenance_boundary_{issue.code}",
            issue.message,
            "initial_program_idea_provenance",
        )
        for issue in report.issues
    ]


def _validate_initial_program_seed_variant_matrix(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / INITIAL_PROGRAM_SEED_VARIANT_MATRIX_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = initial_program_seed_variant_matrix_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "initial_program_seed_variant_matrix_manifest_missing",
                    (
                        f"{INITIAL_PROGRAM_SEED_VARIANT_MATRIX_FILE} must emit "
                        "the initial-program seed-variant comparison matrix"
                    ),
                    "initial_program_seed_variants",
                )
            ]
    report = validate_initial_program_seed_variant_matrix(recordset)
    return [
        PaperManifestIssue(
            f"initial_program_seed_variant_matrix_{issue.code}",
            issue.message,
            "initial_program_seed_variants",
        )
        for issue in report.issues
    ]


def _validate_initial_program_validity_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / INITIAL_PROGRAM_VALIDITY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = initial_program_validity_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "initial_program_validity_boundary_manifest_missing",
                    (
                        f"{INITIAL_PROGRAM_VALIDITY_BOUNDARY_FILE} must emit "
                        "initial-program validity availability"
                    ),
                    "initial_program_validity",
                )
            ]
    report = validate_initial_program_validity_boundary(recordset)
    return [
        PaperManifestIssue(
            f"initial_program_validity_boundary_{issue.code}",
            issue.message,
            "initial_program_validity",
        )
        for issue in report.issues
    ]


def _validate_collaborator_feedback_provenance_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / COLLABORATOR_FEEDBACK_PROVENANCE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = collaborator_feedback_provenance_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "collaborator_feedback_provenance_boundary_manifest_missing",
                    (
                        f"{COLLABORATOR_FEEDBACK_PROVENANCE_BOUNDARY_FILE} must emit "
                        "collaborator-feedback provenance availability"
                    ),
                    "collaborator_feedback_provenance",
                )
            ]
    report = validate_collaborator_feedback_provenance_boundary(recordset)
    return [
        PaperManifestIssue(
            f"collaborator_feedback_provenance_boundary_{issue.code}",
            issue.message,
            "collaborator_feedback_provenance",
        )
        for issue in report.issues
    ]


def _validate_existing_codebase_integration_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / EXISTING_CODEBASE_INTEGRATION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = existing_codebase_integration_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "existing_codebase_integration_boundary_manifest_missing",
                    (
                        f"{EXISTING_CODEBASE_INTEGRATION_BOUNDARY_FILE} must emit "
                        "source-setup-level existing-codebase integration availability"
                    ),
                    "existing_codebase_integration",
                )
            ]
    report = validate_existing_codebase_integration_boundary(recordset)
    return [
        PaperManifestIssue(
            f"existing_codebase_integration_boundary_{issue.code}",
            issue.message,
            "existing_codebase_integration",
        )
        for issue in report.issues
    ]


def _validate_candidate_abstraction_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / CANDIDATE_ABSTRACTION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = candidate_abstraction_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "candidate_abstraction_boundary_manifest_missing",
                    (
                        f"{CANDIDATE_ABSTRACTION_BOUNDARY_FILE} must emit "
                        "candidate-abstraction and bias-evidence availability"
                    ),
                    "candidate_abstraction",
                )
            ]
    report = validate_candidate_abstraction_boundary(recordset)
    return [
        PaperManifestIssue(
            f"candidate_abstraction_boundary_{issue.code}",
            issue.message,
            "candidate_abstraction",
        )
        for issue in report.issues
    ]


def _validate_candidate_abstraction_bias_matrix(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / CANDIDATE_ABSTRACTION_BIAS_MATRIX_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = candidate_abstraction_bias_matrix_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "candidate_abstraction_bias_matrix_manifest_missing",
                    (
                        f"{CANDIDATE_ABSTRACTION_BIAS_MATRIX_FILE} must emit "
                        "the abstraction-family bias design matrix"
                    ),
                    "candidate_abstraction_bias",
                )
            ]
    report = validate_candidate_abstraction_bias_matrix(recordset)
    return [
        PaperManifestIssue(
            f"candidate_abstraction_bias_matrix_{issue.code}",
            issue.message,
            "candidate_abstraction_bias",
        )
        for issue in report.issues
    ]


def _validate_candidate_language_runner_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = candidate_language_runner_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "candidate_language_runner_boundary_manifest_missing",
                    (
                        f"{CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_FILE} must emit "
                        "candidate language/build runner evidence availability"
                    ),
                    "candidate_language_runner",
                )
            ]
    report = validate_candidate_language_runner_boundary(recordset)
    return [
        PaperManifestIssue(
            f"candidate_language_runner_boundary_{issue.code}",
            issue.message,
            "candidate_language_runner",
        )
        for issue in report.issues
    ]


def _validate_proposal_lifecycle_audit_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PROPOSAL_LIFECYCLE_AUDIT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = proposal_lifecycle_audit_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "proposal_lifecycle_audit_boundary_manifest_missing",
                    (
                        f"{PROPOSAL_LIFECYCLE_AUDIT_BOUNDARY_FILE} must emit "
                        "independent proposal lifecycle audit availability"
                    ),
                    "proposal_lifecycle_audit",
                )
            ]
    report = validate_proposal_lifecycle_audit_boundary(recordset)
    return [
        PaperManifestIssue(
            f"proposal_lifecycle_audit_boundary_{issue.code}",
            issue.message,
            "proposal_lifecycle_audit",
        )
        for issue in report.issues
    ]


def _validate_incorrect_suggestion_audit_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / INCORRECT_SUGGESTION_AUDIT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = incorrect_suggestion_audit_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "incorrect_suggestion_audit_boundary_manifest_missing",
                    (
                        f"{INCORRECT_SUGGESTION_AUDIT_BOUNDARY_FILE} must emit "
                        "incorrect-suggestion audit availability"
                    ),
                    "incorrect_suggestion_audit",
                )
            ]
    report = validate_incorrect_suggestion_audit_boundary(recordset)
    return [
        PaperManifestIssue(
            f"incorrect_suggestion_audit_boundary_{issue.code}",
            issue.message,
            "incorrect_suggestion_audit",
        )
        for issue in report.issues
    ]


def _validate_repeated_sampling_baseline_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / REPEATED_SAMPLING_BASELINE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = repeated_sampling_baseline_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "repeated_sampling_baseline_boundary_manifest_missing",
                    (
                        f"{REPEATED_SAMPLING_BASELINE_BOUNDARY_FILE} must emit "
                        "controlled repeated-sampling comparator availability"
                    ),
                    "repeated_sampling_baseline",
                )
            ]
    report = validate_repeated_sampling_baseline_boundary(recordset)
    return [
        PaperManifestIssue(
            f"repeated_sampling_baseline_boundary_{issue.code}",
            issue.message,
            "repeated_sampling_baseline",
        )
        for issue in report.issues
    ]


def _validate_sampling_balance_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / SAMPLING_BALANCE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = sampling_balance_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "sampling_balance_boundary_manifest_missing",
                    (
                        f"{SAMPLING_BALANCE_BOUNDARY_FILE} must emit "
                        "local sampling-counts versus calibrated balance"
                    ),
                    "sampling_balance",
                )
            ]
    report = validate_sampling_balance_boundary(recordset)
    return [
        PaperManifestIssue(
            f"sampling_balance_boundary_{issue.code}",
            issue.message,
            "sampling_balance",
        )
        for issue in report.issues
    ]


def _validate_sample_efficiency_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / SAMPLE_EFFICIENCY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = sample_efficiency_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "sample_efficiency_boundary_manifest_missing",
                    (
                        f"{SAMPLE_EFFICIENCY_BOUNDARY_FILE} must emit "
                        "benchmark-level sample-efficiency availability"
                    ),
                    "sample_efficiency",
                )
            ]
    report = validate_sample_efficiency_boundary(recordset)
    return [
        PaperManifestIssue(
            f"sample_efficiency_boundary_{issue.code}",
            issue.message,
            "sample_efficiency",
        )
        for issue in report.issues
    ]


def _validate_parallel_evaluation_readiness_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PARALLEL_EVALUATION_READINESS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = parallel_evaluation_readiness_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "parallel_evaluation_readiness_boundary_manifest_missing",
                    (
                        f"{PARALLEL_EVALUATION_READINESS_BOUNDARY_FILE} must emit "
                        "parallel-evaluation readiness availability"
                    ),
                    "parallel_evaluation_readiness",
                )
            ]
    report = validate_parallel_evaluation_readiness_boundary(recordset)
    return [
        PaperManifestIssue(
            f"parallel_evaluation_readiness_boundary_{issue.code}",
            issue.message,
            "parallel_evaluation_readiness",
        )
        for issue in report.issues
    ]


def _validate_expensive_evaluation_budget_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / EXPENSIVE_EVALUATION_BUDGET_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = expensive_evaluation_budget_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "expensive_evaluation_budget_boundary_manifest_missing",
                    (
                        f"{EXPENSIVE_EVALUATION_BUDGET_BOUNDARY_FILE} must emit "
                        "local cooperative budget versus compute-hour runtime scope"
                    ),
                    "expensive_evaluation_budget",
                )
            ]
    report = validate_expensive_evaluation_budget_boundary(recordset)
    return [
        PaperManifestIssue(
            f"expensive_evaluation_budget_boundary_{issue.code}",
            issue.message,
            "expensive_evaluation_budget",
        )
        for issue in report.issues
    ]


def _validate_distributed_pipeline_topology_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / DISTRIBUTED_PIPELINE_TOPOLOGY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = distributed_pipeline_topology_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "distributed_pipeline_topology_boundary_manifest_missing",
                    (
                        f"{DISTRIBUTED_PIPELINE_TOPOLOGY_BOUNDARY_FILE} must emit "
                        "distributed-pipeline topology availability"
                    ),
                    "distributed_pipeline_topology",
                )
            ]
    report = validate_distributed_pipeline_topology_boundary(recordset)
    return [
        PaperManifestIssue(
            f"distributed_pipeline_topology_boundary_{issue.code}",
            issue.message,
            "distributed_pipeline_topology",
        )
        for issue in report.issues
    ]


def _validate_workspace_materialization_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / WORKSPACE_MATERIALIZATION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = workspace_materialization_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "workspace_materialization_boundary_manifest_missing",
                    (
                        f"{WORKSPACE_MATERIALIZATION_BOUNDARY_FILE} must emit "
                        "workspace materialization diagnostics availability"
                    ),
                    "workspace_materialization",
                )
            ]
    report = validate_workspace_materialization_boundary(recordset)
    return [
        PaperManifestIssue(
            f"workspace_materialization_boundary_{issue.code}",
            issue.message,
            "workspace_materialization",
        )
        for issue in report.issues
    ]


def _validate_whole_run_source_workspace_integrity_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / WHOLE_RUN_SOURCE_WORKSPACE_INTEGRITY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = whole_run_source_workspace_integrity_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "whole_run_source_workspace_integrity_boundary_manifest_missing",
                    (
                        f"{WHOLE_RUN_SOURCE_WORKSPACE_INTEGRITY_BOUNDARY_FILE} must emit "
                        "whole-run source/workspace integrity availability"
                    ),
                    "whole_run_source_workspace_integrity",
                )
            ]
    report = validate_whole_run_source_workspace_integrity_boundary(recordset)
    return [
        PaperManifestIssue(
            f"whole_run_source_workspace_integrity_boundary_{issue.code}",
            issue.message,
            "whole_run_source_workspace_integrity",
        )
        for issue in report.issues
    ]


def _validate_codebase_scale_benchmark_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / CODEBASE_SCALE_BENCHMARK_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = codebase_scale_benchmark_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "codebase_scale_benchmark_boundary_manifest_missing",
                    (
                        f"{CODEBASE_SCALE_BENCHMARK_BOUNDARY_FILE} must emit "
                        "codebase-scale benchmark availability"
                    ),
                    "codebase_scale_benchmark",
                )
            ]
    report = validate_codebase_scale_benchmark_boundary(recordset)
    return [
        PaperManifestIssue(
            f"codebase_scale_benchmark_boundary_{issue.code}",
            issue.message,
            "codebase_scale_benchmark",
        )
        for issue in report.issues
    ]


def _validate_sorting_network_rediscovery_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / SORTING_NETWORK_REDISCOVERY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = sorting_network_rediscovery_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "sorting_network_rediscovery_boundary_manifest_missing",
                    (
                        f"{SORTING_NETWORK_REDISCOVERY_BOUNDARY_FILE} must emit "
                        "sorting-network rediscovery availability"
                    ),
                    "sorting_network_rediscovery",
                )
            ]
    report = validate_sorting_network_rediscovery_boundary(recordset)
    return [
        PaperManifestIssue(
            f"sorting_network_rediscovery_boundary_{issue.code}",
            issue.message,
            "sorting_network_rediscovery",
        )
        for issue in report.issues
    ]


def _validate_table1_capability_exhibit_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / TABLE1_CAPABILITY_EXHIBIT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = table1_capability_exhibit_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "table1_capability_exhibit_boundary_manifest_missing",
                    (
                        f"{TABLE1_CAPABILITY_EXHIBIT_BOUNDARY_FILE} must emit "
                        "Table 1 exhibit/parity availability"
                    ),
                    "table1_capability_exhibit",
                )
            ]
    report = validate_table1_capability_exhibit_boundary(recordset)
    return [
        PaperManifestIssue(
            f"table1_capability_exhibit_boundary_{issue.code}",
            issue.message,
            "table1_capability_exhibit",
        )
        for issue in report.issues
    ]


def _validate_self_improvement_distillation_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / SELF_IMPROVEMENT_DISTILLATION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = self_improvement_distillation_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "self_improvement_distillation_boundary_manifest_missing",
                    (
                        f"{SELF_IMPROVEMENT_DISTILLATION_BOUNDARY_FILE} must emit "
                        "self-improvement/distillation absence evidence"
                    ),
                    "self_improvement_distillation",
                )
            ]
    report = validate_self_improvement_distillation_boundary(recordset)
    return [
        PaperManifestIssue(
            f"self_improvement_distillation_boundary_{issue.code}",
            issue.message,
            "self_improvement_distillation",
        )
        for issue in report.issues
    ]


def _validate_self_improvement_cadence_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / SELF_IMPROVEMENT_CADENCE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = self_improvement_cadence_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "self_improvement_cadence_boundary_manifest_missing",
                    (
                        f"{SELF_IMPROVEMENT_CADENCE_BOUNDARY_FILE} must emit "
                        "self-improvement cadence/environment ROI absence evidence"
                    ),
                    "self_improvement_cadence",
                )
            ]
    report = validate_self_improvement_cadence_boundary(recordset)
    return [
        PaperManifestIssue(
            f"self_improvement_cadence_boundary_{issue.code}",
            issue.message,
            "self_improvement_cadence",
        )
        for issue in report.issues
    ]


def _validate_ci_workflow_coverage_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / CI_WORKFLOW_COVERAGE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = ci_workflow_coverage_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "ci_workflow_coverage_boundary_manifest_missing",
                    (
                        f"{CI_WORKFLOW_COVERAGE_BOUNDARY_FILE} must emit "
                        "CI workflow coverage availability"
                    ),
                    "ci_workflow_coverage",
                )
            ]
    report = validate_ci_workflow_coverage_boundary(recordset)
    return [
        PaperManifestIssue(
            f"ci_workflow_coverage_boundary_{issue.code}",
            issue.message,
            "ci_workflow_coverage",
        )
        for issue in report.issues
    ]


def _validate_config_validation_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / CONFIG_VALIDATION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = config_validation_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "config_validation_boundary_manifest_missing",
                    (
                        f"{CONFIG_VALIDATION_BOUNDARY_FILE} must emit "
                        "local config-validation versus live provider compatibility"
                    ),
                    "config_validation",
                )
            ]
    report = validate_config_validation_boundary(recordset)
    return [
        PaperManifestIssue(
            f"config_validation_boundary_{issue.code}",
            issue.message,
            "config_validation",
        )
        for issue in report.issues
    ]


def _validate_evaluator_oracle_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / EVALUATOR_ORACLE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = evaluator_oracle_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "evaluator_oracle_boundary_manifest_missing",
                    (
                        f"{EVALUATOR_ORACLE_BOUNDARY_FILE} must emit "
                        "independent evaluator-oracle evidence availability"
                    ),
                    "evaluator_oracle",
                )
            ]
    report = validate_evaluator_oracle_boundary(recordset)
    return [
        PaperManifestIssue(
            f"evaluator_oracle_boundary_{issue.code}",
            issue.message,
            "evaluator_oracle",
        )
        for issue in report.issues
    ]


def _validate_automated_evaluator_scope_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / AUTOMATED_EVALUATOR_SCOPE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = automated_evaluator_scope_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "automated_evaluator_scope_boundary_manifest_missing",
                    (
                        f"{AUTOMATED_EVALUATOR_SCOPE_BOUNDARY_FILE} must emit "
                        "machine-gradeable evaluator scope versus robust environment readiness"
                    ),
                    "automated_evaluator_scope",
                )
            ]
    report = validate_automated_evaluator_scope_boundary(recordset)
    return [
        PaperManifestIssue(
            f"automated_evaluator_scope_boundary_{issue.code}",
            issue.message,
            "automated_evaluator_scope",
        )
        for issue in report.issues
    ]


def _validate_embedded_evaluator_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / EMBEDDED_EVALUATOR_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = embedded_evaluator_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "embedded_evaluator_boundary_manifest_missing",
                    (
                        f"{EMBEDDED_EVALUATOR_BOUNDARY_FILE} must emit "
                        "embedded evaluator Figure 3 parity evidence availability"
                    ),
                    "embedded_evaluator",
                )
            ]
    report = validate_embedded_evaluator_boundary(recordset)
    return [
        PaperManifestIssue(
            f"embedded_evaluator_boundary_{issue.code}",
            issue.message,
            "embedded_evaluator",
        )
        for issue in report.issues
    ]


def _validate_figure3_supervised_exhibit_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / FIGURE3_SUPERVISED_EXHIBIT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = figure3_supervised_exhibit_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "figure3_supervised_exhibit_boundary_manifest_missing",
                    (
                        f"{FIGURE3_SUPERVISED_EXHIBIT_BOUNDARY_FILE} must emit "
                        "Figure 3 supervised-learning exhibit evidence availability"
                    ),
                    "figure3_supervised_exhibit",
                )
            ]
    report = validate_figure3_supervised_exhibit_boundary(recordset)
    return [
        PaperManifestIssue(
            f"figure3_supervised_exhibit_boundary_{issue.code}",
            issue.message,
            "figure3_supervised_exhibit",
        )
        for issue in report.issues
    ]


def _validate_figure6_scheduling_exhibit_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / FIGURE6_SCHEDULING_EXHIBIT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = figure6_scheduling_exhibit_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "figure6_scheduling_exhibit_boundary_manifest_missing",
                    (
                        f"{FIGURE6_SCHEDULING_EXHIBIT_BOUNDARY_FILE} must emit "
                        "Figure 6 scheduling-exhibit artifact scope"
                    ),
                    "figure6_scheduling_exhibit",
                )
            ]
    report = validate_figure6_scheduling_exhibit_boundary(recordset)
    return [
        PaperManifestIssue(
            f"figure6_scheduling_exhibit_boundary_{issue.code}",
            issue.message,
            "figure6_scheduling_exhibit",
        )
        for issue in report.issues
    ]


def _validate_figure7_pallas_tiling_exhibit_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / FIGURE7_PALLAS_TILING_EXHIBIT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = figure7_pallas_tiling_exhibit_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "figure7_pallas_tiling_exhibit_boundary_manifest_missing",
                    (
                        f"{FIGURE7_PALLAS_TILING_EXHIBIT_BOUNDARY_FILE} must emit "
                        "Figure 7 Pallas tiling-exhibit artifact scope"
                    ),
                    "figure7_pallas_tiling_exhibit",
                )
            ]
    report = validate_figure7_pallas_tiling_exhibit_boundary(recordset)
    return [
        PaperManifestIssue(
            f"figure7_pallas_tiling_exhibit_boundary_{issue.code}",
            issue.message,
            "figure7_pallas_tiling_exhibit",
        )
        for issue in report.issues
    ]


def _validate_process_exhibit_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PROCESS_EXHIBIT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = process_exhibit_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "process_exhibit_boundary_manifest_missing",
                    (
                        f"{PROCESS_EXHIBIT_BOUNDARY_FILE} must emit "
                        "Figure 1/Figure 2 process exhibit parity evidence availability"
                    ),
                    "process_exhibit",
                )
            ]
    report = validate_process_exhibit_boundary(recordset)
    return [
        PaperManifestIssue(
            f"process_exhibit_boundary_{issue.code}",
            issue.message,
            "process_exhibit",
        )
        for issue in report.issues
    ]


def _validate_evaluation_cascade_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / EVALUATION_CASCADE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = evaluation_cascade_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "evaluation_cascade_boundary_manifest_missing",
                    (
                        f"{EVALUATION_CASCADE_BOUNDARY_FILE} must emit "
                        "evaluation-cascade efficiency evidence availability"
                    ),
                    "evaluation_cascade",
                )
            ]
    report = validate_evaluation_cascade_boundary(recordset)
    return [
        PaperManifestIssue(
            f"evaluation_cascade_boundary_{issue.code}",
            issue.message,
            "evaluation_cascade",
        )
        for issue in report.issues
    ]


def _validate_cascade_hypothesis_test_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / CASCADE_HYPOTHESIS_TEST_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = cascade_hypothesis_test_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "cascade_hypothesis_test_boundary_manifest_missing",
                    (
                        f"{CASCADE_HYPOTHESIS_TEST_BOUNDARY_FILE} must emit "
                        "runtime hypothesis-test gates versus benchmark-calibrated cascade scope"
                    ),
                    "cascade_hypothesis_test",
                )
            ]
    report = validate_cascade_hypothesis_test_boundary(recordset)
    return [
        PaperManifestIssue(
            f"cascade_hypothesis_test_boundary_{issue.code}",
            issue.message,
            "cascade_hypothesis_test",
        )
        for issue in report.issues
    ]


def _validate_controller_backtracking_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / CONTROLLER_BACKTRACKING_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = controller_backtracking_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "controller_backtracking_boundary_manifest_missing",
                    (
                        f"{CONTROLLER_BACKTRACKING_BOUNDARY_FILE} must emit "
                        "controller backtracking policy evidence availability"
                    ),
                    "controller_backtracking",
                )
            ]
    report = validate_controller_backtracking_boundary(recordset)
    return [
        PaperManifestIssue(
            f"controller_backtracking_boundary_{issue.code}",
            issue.message,
            "controller_backtracking",
        )
        for issue in report.issues
    ]


def _validate_map_elites_illumination_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / MAP_ELITES_ILLUMINATION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = map_elites_illumination_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "map_elites_illumination_boundary_manifest_missing",
                    (
                        f"{MAP_ELITES_ILLUMINATION_BOUNDARY_FILE} must emit "
                        "MAP-Elites illumination-algorithm evidence availability"
                    ),
                    "map_elites_illumination",
                )
            ]
    report = validate_map_elites_illumination_boundary(recordset)
    return [
        PaperManifestIssue(
            f"map_elites_illumination_boundary_{issue.code}",
            issue.message,
            "map_elites_illumination",
        )
        for issue in report.issues
    ]


def _validate_map_elites_descriptor_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / MAP_ELITES_DESCRIPTOR_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = map_elites_descriptor_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "map_elites_descriptor_boundary_manifest_missing",
                    (
                        f"{MAP_ELITES_DESCRIPTOR_BOUNDARY_FILE} must emit "
                        "snapshot descriptor versus stable descriptor/rebin scope"
                    ),
                    "map_elites_descriptor",
                )
            ]
    report = validate_map_elites_descriptor_boundary(recordset)
    return [
        PaperManifestIssue(
            f"map_elites_descriptor_boundary_{issue.code}",
            issue.message,
            "map_elites_descriptor",
        )
        for issue in report.issues
    ]


def _validate_objective_archive_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / OBJECTIVE_ARCHIVE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = objective_archive_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "objective_archive_boundary_manifest_missing",
                    (
                        f"{OBJECTIVE_ARCHIVE_BOUNDARY_FILE} must emit "
                        "retained multi-objective overlays versus primary archive scope"
                    ),
                    "objective_archive",
                )
            ]
    report = validate_objective_archive_boundary(recordset)
    return [
        PaperManifestIssue(
            f"objective_archive_boundary_{issue.code}",
            issue.message,
            "objective_archive",
        )
        for issue in report.issues
    ]


def _validate_archive_event_replay_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ARCHIVE_EVENT_REPLAY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = archive_event_replay_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "archive_event_replay_boundary_manifest_missing",
                    (
                        f"{ARCHIVE_EVENT_REPLAY_BOUNDARY_FILE} must emit "
                        "archive snapshot restore versus ordered event replay scope"
                    ),
                    "archive_event_replay",
                )
            ]
    report = validate_archive_event_replay_boundary(recordset)
    return [
        PaperManifestIssue(
            f"archive_event_replay_boundary_{issue.code}",
            issue.message,
            "archive_event_replay",
        )
        for issue in report.issues
    ]


def _validate_controller_pending_work_resume_boundary(
    root_path: Path,
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / CONTROLLER_PENDING_WORK_RESUME_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = controller_pending_work_resume_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "controller_pending_work_resume_boundary_manifest_missing",
                    (
                        f"{CONTROLLER_PENDING_WORK_RESUME_BOUNDARY_FILE} must emit "
                        "terminal controller-state versus pending-work resume scope"
                    ),
                    "controller_pending_work_resume",
                )
            ]
    report = validate_controller_pending_work_resume_boundary(recordset)
    return [
        PaperManifestIssue(
            f"controller_pending_work_resume_boundary_{issue.code}",
            issue.message,
            "controller_pending_work_resume",
        )
        for issue in report.issues
    ]


def _validate_lineage_replay_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / LINEAGE_REPLAY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = lineage_replay_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "lineage_replay_boundary_manifest_missing",
                    (
                        f"{LINEAGE_REPLAY_BOUNDARY_FILE} must emit "
                        "deterministic lineage-id versus full-replay scope"
                    ),
                    "lineage_replay",
                )
            ]
    report = validate_lineage_replay_boundary(recordset)
    return [
        PaperManifestIssue(
            f"lineage_replay_boundary_{issue.code}",
            issue.message,
            "lineage_replay",
        )
        for issue in report.issues
    ]


def _validate_runtime_rng_replay_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / RUNTIME_RNG_REPLAY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = runtime_rng_replay_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "runtime_rng_replay_boundary_manifest_missing",
                    (
                        f"{RUNTIME_RNG_REPLAY_BOUNDARY_FILE} must emit "
                        "framework RNG restore versus full sampling replay scope"
                    ),
                    "runtime_rng_replay",
                )
            ]
    report = validate_runtime_rng_replay_boundary(recordset)
    return [
        PaperManifestIssue(
            f"runtime_rng_replay_boundary_{issue.code}",
            issue.message,
            "runtime_rng_replay",
        )
        for issue in report.issues
    ]


def _validate_validator_execution_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / VALIDATOR_EXECUTION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = validator_execution_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "validator_execution_boundary_manifest_missing",
                    (
                        f"{VALIDATOR_EXECUTION_BOUNDARY_FILE} must emit "
                        "local validator policy versus sandbox/resource scope"
                    ),
                    "validator_execution",
                )
            ]
    report = validate_validator_execution_boundary(recordset)
    return [
        PaperManifestIssue(
            f"validator_execution_boundary_{issue.code}",
            issue.message,
            "validator_execution",
        )
        for issue in report.issues
    ]


def _validate_validator_artifact_promotion_boundary(
    root_path: Path,
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / VALIDATOR_ARTIFACT_PROMOTION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = validator_artifact_promotion_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "validator_artifact_promotion_boundary_manifest_missing",
                    (
                        f"{VALIDATOR_ARTIFACT_PROMOTION_BOUNDARY_FILE} must emit "
                        "validator consistency gate versus promotion-enforcement scope"
                    ),
                    "validator_artifact_promotion",
                )
            ]
    report = validate_validator_artifact_promotion_boundary(recordset)
    return [
        PaperManifestIssue(
            f"validator_artifact_promotion_boundary_{issue.code}",
            issue.message,
            "validator_artifact_promotion",
        )
        for issue in report.issues
    ]


def _validate_metric_diverse_prompt_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / METRIC_DIVERSE_PROMPT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = metric_diverse_prompt_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "metric_diverse_prompt_boundary_manifest_missing",
                    (
                        f"{METRIC_DIVERSE_PROMPT_BOUNDARY_FILE} must emit "
                        "prompt-visible metric-diversity evidence versus benchmark policy scope"
                    ),
                    "metric_diverse_prompt",
                )
            ]
    report = validate_metric_diverse_prompt_boundary(recordset)
    return [
        PaperManifestIssue(
            f"metric_diverse_prompt_boundary_{issue.code}",
            issue.message,
            "metric_diverse_prompt",
        )
        for issue in report.issues
    ]


def _validate_proposal_score_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PROPOSAL_SCORE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = proposal_score_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "proposal_score_boundary_manifest_missing",
                    (
                        f"{PROPOSAL_SCORE_BOUNDARY_FILE} must emit "
                        "bounded proposal scores versus semantic idea-memory scope"
                    ),
                    "proposal_score",
                )
            ]
    report = validate_proposal_score_boundary(recordset)
    return [
        PaperManifestIssue(
            f"proposal_score_boundary_{issue.code}",
            issue.message,
            "proposal_score",
        )
        for issue in report.issues
    ]


def _validate_proposal_diversity_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PROPOSAL_DIVERSITY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = proposal_diversity_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "proposal_diversity_boundary_manifest_missing",
                    (
                        f"{PROPOSAL_DIVERSITY_BOUNDARY_FILE} must emit "
                        "exact proposal diversity versus semantic novelty scope"
                    ),
                    "proposal_diversity",
                )
            ]
    report = validate_proposal_diversity_boundary(recordset)
    return [
        PaperManifestIssue(
            f"proposal_diversity_boundary_{issue.code}",
            issue.message,
            "proposal_diversity",
        )
        for issue in report.issues
    ]


def _validate_failure_memory_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / FAILURE_MEMORY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = failure_memory_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "failure_memory_boundary_manifest_missing",
                    (
                        f"{FAILURE_MEMORY_BOUNDARY_FILE} must emit "
                        "run-local failure diagnostics versus semantic memory scope"
                    ),
                    "failure_memory",
                )
            ]
    report = validate_failure_memory_boundary(recordset)
    return [
        PaperManifestIssue(
            f"failure_memory_boundary_{issue.code}",
            issue.message,
            "failure_memory",
        )
        for issue in report.issues
    ]


def _validate_program_output_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PROGRAM_OUTPUT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = program_output_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "program_output_boundary_manifest_missing",
                    (
                        f"{PROGRAM_OUTPUT_BOUNDARY_FILE} must emit "
                        "exact current-run program-output lookup versus semantic retrieval scope"
                    ),
                    "program_output",
                )
            ]
    report = validate_program_output_boundary(recordset)
    return [
        PaperManifestIssue(
            f"program_output_boundary_{issue.code}",
            issue.message,
            "program_output",
        )
        for issue in report.issues
    ]


def _validate_artifact_index_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ARTIFACT_INDEX_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = artifact_index_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "artifact_index_boundary_manifest_missing",
                    (
                        f"{ARTIFACT_INDEX_BOUNDARY_FILE} must emit "
                        "bounded artifact metadata versus full-content search scope"
                    ),
                    "artifact_index",
                )
            ]
    report = validate_artifact_index_boundary(recordset)
    return [
        PaperManifestIssue(
            f"artifact_index_boundary_{issue.code}",
            issue.message,
            "artifact_index",
        )
        for issue in report.issues
    ]


def _validate_gemini_provider_parity_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / GEMINI_PROVIDER_PARITY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = gemini_provider_parity_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "gemini_provider_parity_boundary_manifest_missing",
                    (
                        f"{GEMINI_PROVIDER_PARITY_BOUNDARY_FILE} must emit "
                        "Google/Gemini provider-parity availability"
                    ),
                    "gemini_provider_parity",
                )
            ]
    report = validate_gemini_provider_parity_boundary(recordset)
    return [
        PaperManifestIssue(
            f"gemini_provider_parity_boundary_{issue.code}",
            issue.message,
            "gemini_provider_parity",
        )
        for issue in report.issues
    ]


def _validate_gemini_self_training_loop_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / GEMINI_SELF_TRAINING_LOOP_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = gemini_self_training_loop_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "gemini_self_training_loop_boundary_manifest_missing",
                    (
                        f"{GEMINI_SELF_TRAINING_LOOP_BOUNDARY_FILE} must emit "
                        "Gemini self-training loop versus Pallas deployment scope"
                    ),
                    "gemini_self_training_loop",
                )
            ]
    report = validate_gemini_self_training_loop_boundary(recordset)
    return [
        PaperManifestIssue(
            f"gemini_self_training_loop_boundary_{issue.code}",
            issue.message,
            "gemini_self_training_loop",
        )
        for issue in report.issues
    ]


def _validate_hardware_rtl_eda_evidence_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / HARDWARE_RTL_EDA_EVIDENCE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = hardware_rtl_eda_evidence_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "hardware_rtl_eda_evidence_boundary_manifest_missing",
                    (
                        f"{HARDWARE_RTL_EDA_EVIDENCE_BOUNDARY_FILE} must emit "
                        "hardware RTL/EDA metadata versus real artifact scope"
                    ),
                    "hardware_rtl_eda_evidence",
                )
            ]
    report = validate_hardware_rtl_eda_evidence_boundary(recordset)
    return [
        PaperManifestIssue(
            f"hardware_rtl_eda_evidence_boundary_{issue.code}",
            issue.message,
            "hardware_rtl_eda_evidence",
        )
        for issue in report.issues
    ]


def _validate_hardware_rewrite_artifact_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / HARDWARE_REWRITE_ARTIFACT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = hardware_rewrite_artifact_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "hardware_rewrite_artifact_boundary_manifest_missing",
                    (
                        f"{HARDWARE_REWRITE_ARTIFACT_BOUNDARY_FILE} must emit "
                        "TPU arithmetic-circuit rewrite metadata versus artifact scope"
                    ),
                    "hardware_rewrite_artifact",
                )
            ]
    report = validate_hardware_rewrite_artifact_boundary(recordset)
    return [
        PaperManifestIssue(
            f"hardware_rewrite_artifact_boundary_{issue.code}",
            issue.message,
            "hardware_rewrite_artifact",
        )
        for issue in report.issues
    ]


def _validate_hardware_contribution_attribution_boundary(
    root_path: Path,
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / HARDWARE_CONTRIBUTION_ATTRIBUTION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = hardware_contribution_attribution_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "hardware_contribution_attribution_boundary_manifest_missing",
                    (
                        f"{HARDWARE_CONTRIBUTION_ATTRIBUTION_BOUNDARY_FILE} must emit "
                        "Gemini-to-TPU contribution attribution metadata versus artifact scope"
                    ),
                    "hardware_contribution_attribution",
                )
            ]
    report = validate_hardware_contribution_attribution_boundary(recordset)
    return [
        PaperManifestIssue(
            f"hardware_contribution_attribution_boundary_{issue.code}",
            issue.message,
            "hardware_contribution_attribution",
        )
        for issue in report.issues
    ]


def _validate_compiler_ir_reference_check_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / COMPILER_IR_REFERENCE_CHECK_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = compiler_ir_reference_check_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "compiler_ir_reference_check_boundary_manifest_missing",
                    (
                        f"{COMPILER_IR_REFERENCE_CHECK_BOUNDARY_FILE} must emit "
                        "compiler IR metadata versus real reference-check artifact scope"
                    ),
                    "compiler_ir_reference_check",
                )
            ]
    report = validate_compiler_ir_reference_check_boundary(recordset)
    return [
        PaperManifestIssue(
            f"compiler_ir_reference_check_boundary_{issue.code}",
            issue.message,
            "compiler_ir_reference_check",
        )
        for issue in report.issues
    ]


def _validate_compiler_adoption_path_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / COMPILER_ADOPTION_PATH_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = compiler_adoption_path_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "compiler_adoption_path_boundary_manifest_missing",
                    (
                        f"{COMPILER_ADOPTION_PATH_BOUNDARY_FILE} must emit "
                        "compiler-adoption metadata versus integration artifact scope"
                    ),
                    "compiler_adoption_path",
                )
            ]
    report = validate_compiler_adoption_path_boundary(recordset)
    return [
        PaperManifestIssue(
            f"compiler_adoption_path_boundary_{issue.code}",
            issue.message,
            "compiler_adoption_path",
        )
        for issue in report.issues
    ]


def _validate_compiler_stack_context_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / COMPILER_STACK_CONTEXT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = compiler_stack_context_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "compiler_stack_context_boundary_manifest_missing",
                    (
                        f"{COMPILER_STACK_CONTEXT_BOUNDARY_FILE} must emit "
                        "FlashAttention compiler-stack metadata versus artifact scope"
                    ),
                    "compiler_stack_context",
                )
            ]
    report = validate_compiler_stack_context_boundary(recordset)
    return [
        PaperManifestIssue(
            f"compiler_stack_context_boundary_{issue.code}",
            issue.message,
            "compiler_stack_context",
        )
        for issue in report.issues
    ]


def _validate_gigaevo_framework_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / GIGAEVO_FRAMEWORK_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = gigaevo_framework_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "gigaevo_framework_boundary_manifest_missing",
                    (
                        f"{GIGAEVO_FRAMEWORK_BOUNDARY_FILE} must emit "
                        "GigaEvo framework-parity evidence availability"
                    ),
                    "gigaevo_framework",
                )
            ]
    report = validate_gigaevo_framework_boundary(recordset)
    return [
        PaperManifestIssue(
            f"gigaevo_framework_boundary_{issue.code}",
            issue.message,
            "gigaevo_framework",
        )
        for issue in report.issues
    ]


def _validate_kernel_tiling_shape_corpus_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / KERNEL_TILING_SHAPE_CORPUS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = kernel_tiling_shape_corpus_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "kernel_tiling_shape_corpus_boundary_manifest_missing",
                    (
                        f"{KERNEL_TILING_SHAPE_CORPUS_BOUNDARY_FILE} must emit "
                        "Pallas kernel shape-corpus and real-runtime scope"
                    ),
                    "kernel_tiling_shape_corpus",
                )
            ]
    report = validate_kernel_tiling_shape_corpus_boundary(recordset)
    return [
        PaperManifestIssue(
            f"kernel_tiling_shape_corpus_boundary_{issue.code}",
            issue.message,
            "kernel_tiling_shape_corpus",
        )
        for issue in report.issues
    ]


def _validate_pallas_workflow_baseline_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / PALLAS_WORKFLOW_BASELINE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = pallas_workflow_baseline_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "pallas_workflow_baseline_boundary_manifest_missing",
                    (
                        f"{PALLAS_WORKFLOW_BASELINE_BOUNDARY_FILE} must emit "
                        "Pallas autotuning and manual workflow-baseline scope"
                    ),
                    "pallas_workflow_baseline",
                )
            ]
    report = validate_pallas_workflow_baseline_boundary(recordset)
    return [
        PaperManifestIssue(
            f"pallas_workflow_baseline_boundary_{issue.code}",
            issue.message,
            "pallas_workflow_baseline",
        )
        for issue in report.issues
    ]


def _validate_codeevolve_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / CODEEVOLVE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = codeevolve_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "codeevolve_boundary_manifest_missing",
                    (
                        f"{CODEEVOLVE_BOUNDARY_FILE} must emit "
                        "CodeEvolve operator and benchmark evidence availability"
                    ),
                    "codeevolve",
                )
            ]
    report = validate_codeevolve_boundary(recordset)
    return [
        PaperManifestIssue(
            f"codeevolve_boundary_{issue.code}",
            issue.message,
            "codeevolve",
        )
        for issue in report.issues
    ]


def _validate_thetaevolve_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / THETAEVOLVE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = thetaevolve_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "thetaevolve_boundary_manifest_missing",
                    (
                        f"{THETAEVOLVE_BOUNDARY_FILE} must emit "
                        "ThetaEvolve test-time-learning evidence availability"
                    ),
                    "thetaevolve",
                )
            ]
    report = validate_thetaevolve_boundary(recordset)
    return [
        PaperManifestIssue(
            f"thetaevolve_boundary_{issue.code}",
            issue.message,
            "thetaevolve",
        )
        for issue in report.issues
    ]


def _validate_improvevolve_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / IMPROVEVOLVE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = improvevolve_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "improvevolve_boundary_manifest_missing",
                    (
                        f"{IMPROVEVOLVE_BOUNDARY_FILE} must emit "
                        "ImprovEvolve modular-execution evidence availability"
                    ),
                    "improvevolve",
                )
            ]
    report = validate_improvevolve_boundary(recordset)
    return [
        PaperManifestIssue(
            f"improvevolve_boundary_{issue.code}",
            issue.message,
            "improvevolve",
        )
        for issue in report.issues
    ]


def _validate_madevolve_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / MADEVOLVE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = madevolve_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "madevolve_boundary_manifest_missing",
                    (
                        f"{MADEVOLVE_BOUNDARY_FILE} must emit "
                        "MadEvolve domain-optimization evidence availability"
                    ),
                    "madevolve",
                )
            ]
    report = validate_madevolve_boundary(recordset)
    return [
        PaperManifestIssue(
            f"madevolve_boundary_{issue.code}",
            issue.message,
            "madevolve",
        )
        for issue in report.issues
    ]


def _validate_causalevolve_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / CAUSALEVOLVE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = causalevolve_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "causalevolve_boundary_manifest_missing",
                    (
                        f"{CAUSALEVOLVE_BOUNDARY_FILE} must emit "
                        "CausalEvolve causal-scratchpad evidence availability"
                    ),
                    "causalevolve",
                )
            ]
    report = validate_causalevolve_boundary(recordset)
    return [
        PaperManifestIssue(
            f"causalevolve_boundary_{issue.code}",
            issue.message,
            "causalevolve",
        )
        for issue in report.issues
    ]


def _validate_deepevolve_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / DEEPEVOLVE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = deepevolve_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "deepevolve_boundary_manifest_missing",
                    (
                        f"{DEEPEVOLVE_BOUNDARY_FILE} must emit "
                        "DeepEvolve research/debug-loop evidence availability"
                    ),
                    "deepevolve",
                )
            ]
    report = validate_deepevolve_boundary(recordset)
    return [
        PaperManifestIssue(
            f"deepevolve_boundary_{issue.code}",
            issue.message,
            "deepevolve",
        )
        for issue in report.issues
    ]


def _validate_magellan_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / MAGELLAN_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = magellan_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "magellan_boundary_manifest_missing",
                    (
                        f"{MAGELLAN_BOUNDARY_FILE} must emit "
                        "Magellan compiler-optimization evidence availability"
                    ),
                    "magellan",
                )
            ]
    report = validate_magellan_boundary(recordset)
    return [
        PaperManifestIssue(
            f"magellan_boundary_{issue.code}",
            issue.message,
            "magellan",
        )
        for issue in report.issues
    ]


def _validate_archagent_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ARCHAGENT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = archagent_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "archagent_boundary_manifest_missing",
                    (
                        f"{ARCHAGENT_BOUNDARY_FILE} must emit "
                        "ArchAgent computer-architecture evidence availability"
                    ),
                    "archagent",
                )
            ]
    report = validate_archagent_boundary(recordset)
    return [
        PaperManifestIssue(
            f"archagent_boundary_{issue.code}",
            issue.message,
            "archagent",
        )
        for issue in report.issues
    ]


def _validate_multiagent_learning_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / MULTIAGENT_LEARNING_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = multiagent_learning_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "multiagent_learning_boundary_manifest_missing",
                    (
                        f"{MULTIAGENT_LEARNING_BOUNDARY_FILE} must emit "
                        "Multiagent Learning CFR/PSRO evidence availability"
                    ),
                    "multiagent_learning",
                )
            ]
    report = validate_multiagent_learning_boundary(recordset)
    return [
        PaperManifestIssue(
            f"multiagent_learning_boundary_{issue.code}",
            issue.message,
            "multiagent_learning",
        )
        for issue in report.issues
    ]


def _validate_ramsey_numbers_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / RAMSEY_NUMBERS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = ramsey_numbers_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "ramsey_numbers_boundary_manifest_missing",
                    (
                        f"{RAMSEY_NUMBERS_BOUNDARY_FILE} must emit "
                        "Ramsey Numbers graph-witness evidence availability"
                    ),
                    "ramsey_numbers",
                )
            ]
    report = validate_ramsey_numbers_boundary(recordset)
    return [
        PaperManifestIssue(
            f"ramsey_numbers_boundary_{issue.code}",
            issue.message,
            "ramsey_numbers",
        )
        for issue in report.issues
    ]


def _validate_combinatorics_berczy_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / COMBINATORICS_BERCZY_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = combinatorics_berczy_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "combinatorics_berczy_boundary_manifest_missing",
                    (
                        f"{COMBINATORICS_BERCZY_BOUNDARY_FILE} must emit "
                        "Berczy combinatorics experiment evidence availability"
                    ),
                    "combinatorics_berczy",
                )
            ]
    report = validate_combinatorics_berczy_boundary(recordset)
    return [
        PaperManifestIssue(
            f"combinatorics_berczy_boundary_{issue.code}",
            issue.message,
            "combinatorics_berczy",
        )
        for issue in report.issues
    ]


def _validate_ttt_discover_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / TTT_DISCOVER_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = ttt_discover_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "ttt_discover_boundary_manifest_missing",
                    (
                        f"{TTT_DISCOVER_BOUNDARY_FILE} must emit "
                        "TTT-Discover test-time-training evidence availability"
                    ),
                    "ttt_discover",
                )
            ]
    report = validate_ttt_discover_boundary(recordset)
    return [
        PaperManifestIssue(
            f"ttt_discover_boundary_{issue.code}",
            issue.message,
            "ttt_discover",
        )
        for issue in report.issues
    ]


def _validate_bruhat_intervals_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / BRUHAT_INTERVALS_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = bruhat_intervals_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "bruhat_intervals_boundary_manifest_missing",
                    (
                        f"{BRUHAT_INTERVALS_BOUNDARY_FILE} must emit "
                        "Bruhat interval hypercube evidence availability"
                    ),
                    "bruhat_intervals",
                )
            ]
    report = validate_bruhat_intervals_boundary(recordset)
    return [
        PaperManifestIssue(
            f"bruhat_intervals_boundary_{issue.code}",
            issue.message,
            "bruhat_intervals",
        )
        for issue in report.issues
    ]


def _validate_fault2flow_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / FAULT2FLOW_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = fault2flow_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "fault2flow_boundary_manifest_missing",
                    (
                        f"{FAULT2FLOW_BOUNDARY_FILE} must emit "
                        "Fault2Flow workflow-automation evidence availability"
                    ),
                    "fault2flow",
                )
            ]
    report = validate_fault2flow_boundary(recordset)
    return [
        PaperManifestIssue(
            f"fault2flow_boundary_{issue.code}",
            issue.message,
            "fault2flow",
        )
        for issue in report.issues
    ]


def _validate_global_nlp_optimization_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / GLOBAL_NLP_OPTIMIZATION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = global_nlp_optimization_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "global_nlp_optimization_boundary_manifest_missing",
                    (
                        f"{GLOBAL_NLP_OPTIMIZATION_BOUNDARY_FILE} must emit "
                        "global-NLP solver comparator evidence availability"
                    ),
                    "global_nlp_optimization",
                )
            ]
    report = validate_global_nlp_optimization_boundary(recordset)
    return [
        PaperManifestIssue(
            f"global_nlp_optimization_boundary_{issue.code}",
            issue.message,
            "global_nlp_optimization",
        )
        for issue in report.issues
    ]


def _validate_autoconvolution_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / AUTOCONVOLUTION_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = autoconvolution_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "autoconvolution_boundary_manifest_missing",
                    (
                        f"{AUTOCONVOLUTION_BOUNDARY_FILE} must emit "
                        "post-AlphaEvolve autoconvolution evidence availability"
                    ),
                    "autoconvolution",
                )
            ]
    report = validate_autoconvolution_boundary(recordset)
    return [
        PaperManifestIssue(
            f"autoconvolution_boundary_{issue.code}",
            issue.message,
            "autoconvolution",
        )
        for issue in report.issues
    ]


def _validate_sums_differences_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / SUMS_DIFFERENCES_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = sums_differences_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "sums_differences_boundary_manifest_missing",
                    (
                        f"{SUMS_DIFFERENCES_BOUNDARY_FILE} must emit "
                        "post-AlphaEvolve sums-and-differences evidence availability"
                    ),
                    "sums_differences",
                )
            ]
    report = validate_sums_differences_boundary(recordset)
    return [
        PaperManifestIssue(
            f"sums_differences_boundary_{issue.code}",
            issue.message,
            "sums_differences",
        )
        for issue in report.issues
    ]


def _validate_sums_differences_sequence_boundary(
    root_path: Path,
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / SUMS_DIFFERENCES_SEQUENCE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = sums_differences_sequence_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "sums_differences_sequence_boundary_manifest_missing",
                    (
                        f"{SUMS_DIFFERENCES_SEQUENCE_BOUNDARY_FILE} must emit "
                        "post-AlphaEvolve sums-and-differences sequence evidence availability"
                    ),
                    "sums_differences_sequence",
                )
            ]
    report = validate_sums_differences_sequence_boundary(recordset)
    return [
        PaperManifestIssue(
            f"sums_differences_sequence_boundary_{issue.code}",
            issue.message,
            "sums_differences_sequence",
        )
        for issue in report.issues
    ]


def _validate_ucb1_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / UCB1_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = ucb1_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "ucb1_boundary_manifest_missing",
                    (
                        f"{UCB1_BOUNDARY_FILE} must emit UCB1 heuristic "
                        "scheduler evidence availability"
                    ),
                    "ucb1",
                )
            ]
    report = validate_ucb1_boundary(recordset)
    return [
        PaperManifestIssue(
            f"ucb1_boundary_{issue.code}",
            issue.message,
            "ucb1",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_2026_impact_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / ALPHAEVOLVE_2026_IMPACT_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = alphaevolve_2026_impact_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_2026_impact_boundary_manifest_missing",
                    (
                        f"{ALPHAEVOLVE_2026_IMPACT_BOUNDARY_FILE} must emit "
                        "official 2026 AlphaEvolve impact-source claim boundaries"
                    ),
                    "alphaevolve_2026_impact",
                )
            ]
    report = validate_alphaevolve_2026_impact_boundary(recordset)
    return [
        PaperManifestIssue(
            f"alphaevolve_2026_impact_boundary_{issue.code}",
            issue.message,
            "alphaevolve_2026_impact",
        )
        for issue in report.issues
    ]


def _validate_bilateral_trade_boundary(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    sidecar_path = root_path / BILATERAL_TRADE_BOUNDARY_FILE
    if sidecar_path.exists():
        recordset: object | str | Path = sidecar_path
    else:
        recordset = bilateral_trade_boundary_record()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "bilateral_trade_boundary_manifest_missing",
                    (
                        f"{BILATERAL_TRADE_BOUNDARY_FILE} must emit "
                        "Bilateral Trade mechanism-design evidence availability"
                    ),
                    "bilateral_trade",
                )
            ]
    report = validate_bilateral_trade_boundary(recordset)
    return [
        PaperManifestIssue(
            f"bilateral_trade_boundary_{issue.code}",
            issue.message,
            "bilateral_trade",
        )
        for issue in report.issues
    ]


def _validate_example_benchmark_scope_records(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    scope_path = root_path / EXAMPLE_BENCHMARK_SCOPE_FILE
    if scope_path.exists():
        try:
            recordset: object = json.loads(scope_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return [
                PaperManifestIssue(
                    "example_scope_manifest_unreadable",
                    _manifest_diagnostic(scope_path, root_path, exc),
                    "example_benchmark_scope",
                )
            ]
    else:
        recordset = example_benchmark_scope_records()
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "example_scope_manifest_missing",
                    f"{EXAMPLE_BENCHMARK_SCOPE_FILE} must emit shipped-example benchmark scope records",
                    "example_benchmark_scope",
                )
            ]
    report = validate_example_benchmark_scope(recordset)
    return [
        PaperManifestIssue(
            f"example_scope_{issue.code}",
            issue.message,
        )
        for issue in report.issues
    ]


def _validate_math_outcome_boundaries(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False

    specs = (
        (
            MATH_OUTCOME_BOUNDARY_FILE,
            alphaevolve_math_outcome_boundary,
            validate_math_outcome_boundary,
            "math_outcome_boundary",
            "math_outcome_boundary_manifest_missing",
            "math_outcome",
            "Section 3.2 aggregate constructive-math outcome boundary",
        ),
        (
            MATH_STARTING_CONSTRUCTION_BOUNDARY_FILE,
            alphaevolve_math_starting_construction_boundary,
            validate_math_starting_construction_boundary,
            "math_starting_construction_boundary",
            "math_starting_construction_boundary_manifest_missing",
            "math_starting_construction",
            "Section 3.2 simple-or-random starting-construction boundary",
        ),
        (
            MATH_HEURISTIC_HANDOFF_BOUNDARY_FILE,
            alphaevolve_math_heuristic_handoff_boundary,
            validate_math_heuristic_handoff_boundary,
            "math_heuristic_handoff_boundary",
            "math_heuristic_handoff_boundary_manifest_missing",
            "math_heuristic_handoff",
            "Section 3.2 heuristic-to-construction handoff boundary",
        ),
        (
            MATH_HEURISTIC_STAGE_SEQUENCE_BOUNDARY_FILE,
            alphaevolve_math_heuristic_stage_sequence_boundary,
            validate_math_heuristic_stage_sequence_boundary,
            "math_heuristic_stage_sequence_boundary",
            "math_heuristic_stage_sequence_boundary_manifest_missing",
            "math_heuristic_stage_sequence",
            "Section 3.2 staged-heuristic sequence boundary",
        ),
    )
    issues: list[PaperManifestIssue] = []
    for relative_file, factory, validator, label, missing_code, issue_prefix, description in specs:
        boundary_path = root_path / relative_file
        if boundary_path.exists():
            try:
                boundary: object = json.loads(boundary_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                issues.append(
                    PaperManifestIssue(
                        f"{issue_prefix}_manifest_unreadable",
                        _manifest_diagnostic(boundary_path, root_path, exc),
                        label,
                    )
                )
                continue
        else:
            boundary = factory()
            if is_repo_root:
                issues.append(
                    PaperManifestIssue(
                        missing_code,
                        f"{relative_file} must emit the {description}",
                        label,
                    )
                )
        report = validator(boundary)
        issues.extend(
            PaperManifestIssue(
                f"{issue_prefix}_{issue.code}",
                issue.message,
                label,
            )
            for issue in report.issues
        )
    return issues


def _validate_paper_source_identity_manifest(
    root_path: Path,
    manifest_rows: list[dict[str, Any]],
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / PAPER_SOURCE_IDENTITY_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "paper_source_identity_manifest_missing",
                    "papers/row_identity.json must emit source-identity rows for the paper cache",
                )
            ]
        return []
    report = validate_paper_source_identity_manifest(
        manifest_path,
        manifest_rows=manifest_rows,
    )
    return [
        PaperManifestIssue(
            f"paper_source_identity_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.row_id) if issue.row_id else None,
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_source_pdf_version_manifest(
    root_path: Path,
    manifest_rows_by_id: dict[str, dict[str, Any]],
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_SOURCE_VERSION_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_source_pdf_version_manifest_missing",
                    "papers/source_versions.json must emit the AlphaEvolve source-version row",
                    "2506.13131",
                )
            ]
        return []
    first_page_text = None
    if is_repo_root:
        pdf_path = root_path / "papers/2506.13131__AlphaEvolve.pdf"
        if pdf_path.exists():
            try:
                first_page_text = _read_pdf_quietly(pdf_path).pages[0].extract_text() or ""
            except Exception as exc:
                return [
                    PaperManifestIssue(
                        "alphaevolve_source_pdf_version_manifest_header_read_error",
                        _safe_pdf_parse_error(exc),
                        "2506.13131",
                    )
                ]
    report = validate_alphaevolve_source_pdf_version_manifest(
        manifest_path,
        first_page_text=first_page_text,
    )
    issues = [
        PaperManifestIssue(
            f"alphaevolve_source_pdf_version_manifest_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]
    record = alphaevolve_source_pdf_version_record()
    row = manifest_rows_by_id.get("2506.13131")
    if row is None:
        issues.append(
            PaperManifestIssue(
                "alphaevolve_source_pdf_version_manifest_missing_manifest_row",
                "source-version manifest requires a matching paper manifest row",
                "2506.13131",
            )
        )
        return issues
    manifest_row = record["manifest_row"]
    for field in ("id", "title", "url", "file", "bytes", "sha256"):
        if row.get(field) != manifest_row[field]:
            issues.append(
                PaperManifestIssue(
                    f"alphaevolve_source_pdf_version_manifest_{field}_mismatch",
                    f"paper manifest row {field} does not match papers/source_versions.json",
                    "2506.13131",
                )
            )
    return issues


def _validate_alphaevolve_source_pdf_rights_manifest(
    root_path: Path,
    manifest_rows_by_id: dict[str, dict[str, Any]],
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_SOURCE_RIGHTS_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_source_pdf_rights_manifest_missing",
                    "papers/source_rights.json must emit AlphaEvolve source-rights rows",
                    "2506.13131",
                )
            ]
        return []
    first_page_text = None
    if is_repo_root:
        pdf_path = root_path / "papers/2506.13131__AlphaEvolve.pdf"
        if pdf_path.exists():
            try:
                first_page_text = _read_pdf_quietly(pdf_path).pages[0].extract_text() or ""
            except Exception as exc:
                return [
                    PaperManifestIssue(
                        "alphaevolve_source_pdf_rights_manifest_text_read_error",
                        _safe_pdf_parse_error(exc),
                        "2506.13131",
                    )
                ]
    report = validate_alphaevolve_source_pdf_rights_manifest(
        manifest_path,
        first_page_text=first_page_text,
    )
    issues = [
        PaperManifestIssue(
            f"alphaevolve_source_pdf_rights_manifest_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]
    record = alphaevolve_source_pdf_rights_record()
    row = manifest_rows_by_id.get("2506.13131")
    if row is None:
        issues.append(
            PaperManifestIssue(
                "alphaevolve_source_pdf_rights_manifest_missing_manifest_row",
                "source-rights manifest requires a matching paper manifest row",
                "2506.13131",
            )
        )
        return issues
    manifest_row = record["manifest_row"]
    for field in ("id", "title", "url", "file", "bytes", "sha256"):
        if row.get(field) != manifest_row[field]:
            issues.append(
                PaperManifestIssue(
                    f"alphaevolve_source_pdf_rights_manifest_{field}_mismatch",
                    f"paper manifest row {field} does not match papers/source_rights.json",
                    "2506.13131",
                )
            )
    return issues


def _validate_alphaevolve_source_pdf_version_record(
    root_path: Path,
    manifest_rows_by_id: dict[str, dict[str, Any]],
) -> list[PaperManifestIssue]:
    record = alphaevolve_source_pdf_version_record()
    report = validate_alphaevolve_source_pdf_version(record)
    issues = [
        PaperManifestIssue(
            f"alphaevolve_source_pdf_version_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    if not is_repo_root:
        return issues
    row = manifest_rows_by_id.get("2506.13131")
    if row is None:
        issues.append(
            PaperManifestIssue(
                "alphaevolve_source_pdf_version_missing_manifest_row",
                "AlphaEvolve source-version record requires a matching manifest row",
                "2506.13131",
            )
        )
        return issues
    manifest_row = record["manifest_row"]
    for field in ("id", "title", "url", "file", "bytes", "sha256"):
        if row.get(field) != manifest_row[field]:
            issues.append(
                PaperManifestIssue(
                    f"alphaevolve_source_pdf_version_manifest_{field}_mismatch",
                    f"manifest row {field} does not match the source-version record",
                    "2506.13131",
                )
            )
    file_value = row.get("file")
    if isinstance(file_value, str):
        pdf_path = root_path / file_value
        if pdf_path.exists():
            try:
                first_page_text = _read_pdf_quietly(pdf_path).pages[0].extract_text() or ""
            except Exception as exc:
                issues.append(
                    PaperManifestIssue(
                        "alphaevolve_source_pdf_version_header_read_error",
                        _safe_pdf_parse_error(exc),
                        "2506.13131",
                    )
                )
            else:
                header_report = validate_alphaevolve_source_pdf_version(
                    record,
                    first_page_text=first_page_text,
                )
                issues.extend(
                    PaperManifestIssue(
                        f"alphaevolve_source_pdf_version_{issue.code}",
                        issue.message,
                        "2506.13131",
                    )
                    for issue in header_report.issues
                )
    return issues


def _validate_alphaevolve_source_pdf_rights_record(
    root_path: Path,
    manifest_rows_by_id: dict[str, dict[str, Any]],
) -> list[PaperManifestIssue]:
    record = alphaevolve_source_pdf_rights_record()
    report = validate_alphaevolve_source_pdf_rights(record)
    issues = [
        PaperManifestIssue(
            f"alphaevolve_source_pdf_rights_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    if not is_repo_root:
        return issues
    row = manifest_rows_by_id.get("2506.13131")
    if row is None:
        issues.append(
            PaperManifestIssue(
                "alphaevolve_source_pdf_rights_missing_manifest_row",
                "AlphaEvolve source-rights record requires a matching manifest row",
                "2506.13131",
            )
        )
        return issues
    manifest_row = record["manifest_row"]
    for field in ("id", "title", "url", "file", "bytes", "sha256"):
        if row.get(field) != manifest_row[field]:
            issues.append(
                PaperManifestIssue(
                    f"alphaevolve_source_pdf_rights_manifest_{field}_mismatch",
                    f"manifest row {field} does not match the source-rights record",
                    "2506.13131",
                )
            )
    file_value = row.get("file")
    if isinstance(file_value, str):
        pdf_path = root_path / file_value
        if pdf_path.exists():
            try:
                first_page_text = _read_pdf_quietly(pdf_path).pages[0].extract_text() or ""
            except Exception as exc:
                issues.append(
                    PaperManifestIssue(
                        "alphaevolve_source_pdf_rights_text_read_error",
                        _safe_pdf_parse_error(exc),
                        "2506.13131",
                    )
                )
            else:
                rights_report = validate_alphaevolve_source_pdf_rights(
                    record,
                    first_page_text=first_page_text,
                )
                issues.extend(
                    PaperManifestIssue(
                        f"alphaevolve_source_pdf_rights_{issue.code}",
                        issue.message,
                        "2506.13131",
                    )
                    for issue in rights_report.issues
                )
    return issues


def _validate_alphaevolve_references_bibliography(
    root_path: Path,
    manifest_rows_by_id: dict[str, dict[str, Any]],
    manifest_rows: list[dict[str, Any]],
) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    bibliography_path = root_path / EXPECTED_REFERENCES_BIBLIOGRAPHY_FILE
    if not bibliography_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_references_bibliography_missing",
                    "papers/references.json must emit normalized AlphaEvolve bibliography rows",
                    "2506.13131",
                )
            ]
        return []
    page_text_by_number = None
    if is_repo_root:
        row = manifest_rows_by_id.get("2506.13131")
        file_value = row.get("file") if isinstance(row, dict) else None
        if isinstance(file_value, str):
            pdf_path = root_path / file_value
            if pdf_path.exists():
                try:
                    reader = _read_pdf_quietly(pdf_path)
                    page_text_by_number = {
                        page_number: reader.pages[page_number - 1].extract_text() or ""
                        for page_number in range(23, 34)
                    }
                except Exception as exc:
                    return [
                        PaperManifestIssue(
                            "alphaevolve_references_bibliography_read_error",
                            _safe_pdf_parse_error(exc),
                            "2506.13131",
                        )
                    ]
    report = validate_alphaevolve_references_bibliography(
        bibliography_path,
        page_text_by_number=page_text_by_number,
        manifest_rows=manifest_rows,
    )
    return [
        PaperManifestIssue(
            f"alphaevolve_references_bibliography_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.reference_id) if issue.reference_id else "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_references_section_record(
    root_path: Path,
    manifest_rows_by_id: dict[str, dict[str, Any]],
) -> list[PaperManifestIssue]:
    record = alphaevolve_references_section_record()
    report = validate_alphaevolve_references_section(record)
    issues = [
        PaperManifestIssue(
            f"alphaevolve_references_section_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.reference_id) if issue.reference_id else "2506.13131",
        )
        for issue in report.issues
    ]
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    if not is_repo_root:
        return issues
    row = manifest_rows_by_id.get("2506.13131")
    if row is None:
        issues.append(
            PaperManifestIssue(
                "alphaevolve_references_section_missing_manifest_row",
                "AlphaEvolve references-section record requires a matching manifest row",
                "2506.13131",
            )
        )
        return issues
    file_value = row.get("file")
    if isinstance(file_value, str):
        pdf_path = root_path / file_value
        if pdf_path.exists():
            try:
                reader = _read_pdf_quietly(pdf_path)
                page_text_by_number = {
                    page_number: reader.pages[page_number - 1].extract_text() or ""
                    for page_number in range(23, 33)
                }
            except Exception as exc:
                issues.append(
                    PaperManifestIssue(
                        "alphaevolve_references_section_read_error",
                        _safe_pdf_parse_error(exc),
                        "2506.13131",
                    )
                )
            else:
                references_report = validate_alphaevolve_references_section(
                    record,
                    page_text_by_number=page_text_by_number,
                )
                issues.extend(
                    PaperManifestIssue(
                        f"alphaevolve_references_section_{issue.code}",
                        issue.message,
                        _safe_manifest_label(issue.reference_id) if issue.reference_id else "2506.13131",
                    )
                    for issue in references_report.issues
                )
    return issues


def _validate_alphaevolve_companion_source_manifest(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_COMPANION_SOURCE_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_companion_source_manifest_missing",
                    "papers/companion_sources.json must emit the AlphaEvolve companion Colab source row",
                    "2506.13131",
                )
            ]
        return []
    report = validate_alphaevolve_companion_source_manifest(manifest_path)
    return [
        PaperManifestIssue(
            f"alphaevolve_companion_source_manifest_{issue.code}",
            issue.message,
            "2506.13131",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_follow_on_math_source_record(
    root_path: Path,
    manifest_rows_by_id: dict[str, dict[str, Any]],
) -> list[PaperManifestIssue]:
    record = alphaevolve_follow_on_math_source_record()
    report = validate_alphaevolve_follow_on_math_source(record)
    issues = [
        PaperManifestIssue(
            f"alphaevolve_follow_on_math_source_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.source_id) if issue.source_id else "2511.02864",
        )
        for issue in report.issues
    ]
    manifest_row = manifest_rows_by_id.get("2511.02864")
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    requires_cache_row = (
        is_repo_root
        or manifest_row is not None
        or (root_path / EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE).exists()
    )
    if not requires_cache_row:
        return issues
    local_cache = record["paper"]["local_cache"]
    if manifest_row is None:
        issues.append(
            PaperManifestIssue(
                "alphaevolve_follow_on_math_source_manifest_cache_row_missing",
                "Follow-on source record says arXiv 2511.02864 is locally cached, but the download manifest row is missing",
                "2511.02864",
            )
        )
    else:
        expected = {
            "file": local_cache["file"],
            "bytes": local_cache["bytes"],
            "sha256": local_cache["sha256"],
            "url": record["paper"]["floating_pdf_url"],
        }
        for field, expected_value in expected.items():
            if manifest_row.get(field) != expected_value:
                issues.append(
                    PaperManifestIssue(
                        f"alphaevolve_follow_on_math_source_manifest_cache_{field}_mismatch",
                        f"Follow-on source local cache {field} must match the download manifest row",
                        "2511.02864",
                    )
                )
    return issues


def _validate_alphaevolve_paper_artifact_role_linkage(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False

    role_path = root_path / PAPER_ARTIFACT_ROLES_FILE
    if role_path.exists():
        role_recordset: object | str | Path = role_path
    else:
        role_recordset = alphaevolve_paper_artifact_role_records()

    role_report = validate_paper_artifact_roles(role_recordset)
    issues = [
        PaperManifestIssue(
            f"alphaevolve_paper_artifact_roles_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.artifact_id) if issue.artifact_id else None,
        )
        for issue in role_report.issues
    ]
    if not role_path.exists() and is_repo_root:
        issues.append(
            PaperManifestIssue(
                "alphaevolve_paper_artifact_roles_manifest_missing",
                f"{PAPER_ARTIFACT_ROLES_FILE} must emit the AlphaEvolve paper artifact-role records",
                "paper_artifact_roles",
            )
        )

    linkage_path = root_path / PAPER_ARTIFACT_LINKAGE_FILE
    if linkage_path.exists():
        linkage_recordset: object | str | Path = linkage_path
    else:
        linkage_recordset = alphaevolve_paper_artifact_linkage_record(
            alphaevolve_paper_artifact_role_records()
        )
    linkage_report = validate_paper_artifact_linkage(linkage_recordset, role_recordset)
    issues.extend(
        PaperManifestIssue(
            f"alphaevolve_paper_artifact_linkage_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.artifact_id) if issue.artifact_id else None,
        )
        for issue in linkage_report.issues
    )
    if not linkage_path.exists() and is_repo_root:
        issues.append(
            PaperManifestIssue(
                "alphaevolve_paper_artifact_linkage_manifest_missing",
                f"{PAPER_ARTIFACT_LINKAGE_FILE} must emit the AlphaEvolve paper artifact-linkage boundary",
                "paper_artifact_linkage",
            )
        )
    return issues


def _validate_alphaevolve_follow_on_source_manifest(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_FOLLOW_ON_SOURCE_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_follow_on_source_manifest_missing",
                    "papers/follow_on_sources.json must emit the AlphaEvolve follow-on math source row",
                    "2511.02864",
                )
            ]
        return []
    report = validate_alphaevolve_follow_on_source_manifest(manifest_path)
    return [
        PaperManifestIssue(
            f"alphaevolve_follow_on_source_manifest_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.source_id) if issue.source_id else "2511.02864",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_follow_on_repository_rights_manifest(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_FOLLOW_ON_REPOSITORY_RIGHTS_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_follow_on_repository_rights_manifest_missing",
                    "papers/follow_on_repository_rights.json must emit the problem repository rights row",
                    "2511.02864",
                )
            ]
        return []
    report = validate_alphaevolve_follow_on_repository_rights_manifest(manifest_path)
    return [
        PaperManifestIssue(
            f"alphaevolve_follow_on_repository_rights_manifest_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.source_id) if issue.source_id else "2511.02864",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_follow_on_runtime_absence_manifest(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_FOLLOW_ON_RUNTIME_ABSENCE_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_follow_on_runtime_absence_manifest_missing",
                    "papers/follow_on_runtime_absence.json must emit the problem repository runtime-absence row",
                    "2511.02864",
                )
            ]
        return []
    report = validate_alphaevolve_follow_on_runtime_absence_manifest(manifest_path)
    return [
        PaperManifestIssue(
            f"alphaevolve_follow_on_runtime_absence_manifest_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.source_id) if issue.source_id else "2511.02864",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_follow_on_tao_blog_manifest(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_FOLLOW_ON_TAO_BLOG_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_follow_on_tao_blog_manifest_missing",
                    "papers/follow_on_tao_blog.json must emit the Terence Tao follow-on blog source row",
                    "2511.02864",
                )
            ]
        return []
    report = validate_alphaevolve_follow_on_tao_blog_manifest(manifest_path)
    return [
        PaperManifestIssue(
            f"alphaevolve_follow_on_tao_blog_manifest_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.source_id) if issue.source_id else "2511.02864",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_follow_on_problem_coverage_record() -> list[PaperManifestIssue]:
    report = validate_alphaevolve_follow_on_problem_coverage(
        alphaevolve_follow_on_problem_coverage_record()
    )
    return [
        PaperManifestIssue(
            f"alphaevolve_follow_on_problem_coverage_{issue.code}",
            issue.message,
            str(issue.problem_id) if issue.problem_id is not None else "2511.02864",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_theoretical_cs_source_manifest(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_THEORETICAL_CS_SOURCE_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_theoretical_cs_source_manifest_missing",
                    "papers/theoretical_cs_sources.json must emit the theoretical-CS proof-element source row",
                    "2509.18057",
                )
            ]
        return []
    report = validate_alphaevolve_theoretical_cs_source_manifest(manifest_path)
    return [
        PaperManifestIssue(
            f"alphaevolve_theoretical_cs_source_manifest_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.source_id) if issue.source_id else "2509.18057",
        )
        for issue in report.issues
    ]


def _validate_alphaevolve_official_blog_manifest(root_path: Path) -> list[PaperManifestIssue]:
    try:
        is_repo_root = root_path.resolve() == _repo_root().resolve()
    except OSError:
        is_repo_root = False
    manifest_path = root_path / EXPECTED_OFFICIAL_BLOG_MANIFEST_FILE
    if not manifest_path.exists():
        if is_repo_root:
            return [
                PaperManifestIssue(
                    "alphaevolve_official_blog_manifest_missing",
                    "papers/official_deepmind_blog.json must emit the official DeepMind announcement source row",
                    "2506.13131",
                )
            ]
        return []
    report = validate_alphaevolve_official_blog_manifest(manifest_path)
    return [
        PaperManifestIssue(
            f"alphaevolve_official_blog_manifest_{issue.code}",
            issue.message,
            _safe_manifest_label(issue.source_id) if issue.source_id else "2506.13131",
        )
        for issue in report.issues
    ]


def rehydrate_paper_cache(
    root: str | Path = ".",
    *,
    force: bool = False,
    timeout: float = PAPER_DOWNLOAD_TIMEOUT_SECONDS,
) -> PaperRehydrateReport:
    root_path = Path(root)
    rows, issues = _load_rehydrate_rows(root_path)
    if timeout <= 0:
        issues.append(PaperManifestIssue("invalid_download_timeout", "download timeout must be positive"))
    if issues:
        return PaperRehydrateReport(
            ok=False,
            row_count=len(rows),
            verified_existing_count=0,
            downloaded_count=0,
            failed_count=0,
            results=[],
            issues=issues,
        )

    results: list[PaperRehydrateResult] = []
    for row in rows:
        row_id = _safe_manifest_label(str(row["id"]))
        file_value = str(row["file"])
        target = root_path / file_value
        if row["ok"] is not True:
            results.append(
                PaperRehydrateResult(
                    row_id=row_id,
                    file=file_value,
                    status="failed",
                    bytes=None,
                    sha256=None,
                    message=_sanitize_download_message(
                        f"manifest row records failed download: {row['message']}"
                    ),
                )
            )
            continue

        existing = _existing_rehydrate_match(row, target, row_id)
        if existing.status == "verified_existing" and not force:
            results.append(existing)
            continue
        if existing.status == "failed":
            results.append(existing)
            continue

        results.append(_download_rehydrate_row(row, root_path, timeout))

    verified_existing_count = sum(1 for result in results if result.status == "verified_existing")
    downloaded_count = sum(1 for result in results if result.status == "downloaded")
    failed_count = sum(1 for result in results if result.status == "failed")
    return PaperRehydrateReport(
        ok=failed_count == 0,
        row_count=len(rows),
        verified_existing_count=verified_existing_count,
        downloaded_count=downloaded_count,
        failed_count=failed_count,
        results=results,
        issues=[],
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the committed paper cache manifests.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to the current directory.")
    parser.add_argument(
        "--require-local-pdfs",
        action="store_true",
        help="Fail when ignored local PDF cache files are absent.",
    )
    parser.add_argument(
        "--rehydrate",
        action="store_true",
        help="Download missing or forced local paper PDFs from the committed manifests.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="With --rehydrate, redownload files even when byte count and SHA-256 already match.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=PAPER_DOWNLOAD_TIMEOUT_SECONDS,
        help=f"Per-paper download timeout in seconds for --rehydrate. Defaults to {PAPER_DOWNLOAD_TIMEOUT_SECONDS:g}.",
    )
    parser.add_argument("--json", action="store_true", help="Print the report as JSON.")
    args = parser.parse_args(argv)

    if args.force and not args.rehydrate:
        parser.error("--force requires --rehydrate")
    if args.rehydrate:
        report = rehydrate_paper_cache(args.root, force=args.force, timeout=args.timeout)
        if args.json:
            print(json.dumps(_rehydrate_report_to_dict(report), indent=2, sort_keys=True))
        else:
            print(
                "paper cache rehydrate: "
                f"{report.row_count} rows, "
                f"{report.verified_existing_count} existing verified, "
                f"{report.downloaded_count} downloaded, "
                f"{report.failed_count} failed"
            )
            for issue in report.issues:
                prefix = f"{issue.row_id}: " if issue.row_id else ""
                print(f"{issue.code}: {prefix}{issue.message}")
            for result in report.results:
                if result.status == "failed":
                    print(f"failed: {result.row_id}: {result.file}: {result.message}")
        return 0 if report.ok else 1

    report = validate_paper_manifest(args.root, require_local_pdfs=args.require_local_pdfs)
    if args.json:
        print(json.dumps(_report_to_dict(report), indent=2, sort_keys=True))
    else:
        print(
            "paper manifest: "
            f"{report.row_count} rows, "
            f"{report.local_unique_file_count} unique local PDFs, "
            f"{report.local_present_count} local PDFs present, "
            f"{report.local_missing_count} missing"
        )
        for issue in report.issues:
            prefix = f"{issue.row_id}: " if issue.row_id else ""
            print(f"{issue.code}: {prefix}{issue.message}")
    return 0 if report.ok else 1


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_rehydrate_rows(root: Path) -> tuple[list[dict[str, Any]], list[PaperManifestIssue]]:
    json_rows, issues = _load_json_manifest(root / "papers" / "download_manifest.json", root)
    csv_rows, csv_issues = _load_csv_manifest(root / "papers" / "download_manifest.csv", root)
    issues.extend(csv_issues)

    if len(json_rows) != len(csv_rows):
        issues.append(
            PaperManifestIssue(
                "manifest_count_mismatch",
                f"JSON has {len(json_rows)} rows but CSV has {len(csv_rows)} rows",
            )
        )
    csv_by_id: dict[str, dict[str, Any]] = {}
    for row in csv_rows:
        row_id = str(row.get("id", ""))
        if row_id in csv_by_id:
            issues.append(PaperManifestIssue("duplicate_csv_id", "duplicate CSV paper id", _safe_manifest_label(row_id)))
            continue
        csv_by_id[row_id] = row

    seen_ids: set[str] = set()
    seen_files: dict[str, str] = {}
    seen_sha256: dict[str, str] = {}
    for index, row in enumerate(json_rows):
        row_id = str(row.get("id", f"row-{index}"))
        row_label = _safe_manifest_label(row_id)
        issues.extend(_validate_row_schema(row, row_label))
        if row_id in seen_ids:
            issues.append(PaperManifestIssue("duplicate_id", "duplicate paper id", row_label))
        seen_ids.add(row_id)

        csv_row = csv_by_id.get(row_id)
        if csv_row is None:
            issues.append(PaperManifestIssue("missing_csv_row", "missing matching CSV row", row_label))
        elif _canonical_row(row) != _canonical_row(csv_row):
            issues.append(PaperManifestIssue("csv_json_mismatch", "CSV row does not match JSON row", row_label))

        file_value = row.get("file")
        if isinstance(file_value, str) and _is_safe_paper_path(file_value):
            file_key = _normalized_paper_file_key(file_value)
            if file_key in seen_files:
                issues.append(
                    PaperManifestIssue(
                        "duplicate_file_path",
                        f"file path also appears in row {seen_files[file_key]}",
                        row_label,
                    )
                )
            else:
                seen_files[file_key] = row_label

        sha256 = row.get("sha256")
        if isinstance(sha256, str) and SHA256_RE.fullmatch(sha256):
            if sha256 in seen_sha256:
                issues.append(
                    PaperManifestIssue(
                        "duplicate_sha256",
                        f"sha256 also appears in row {seen_sha256[sha256]}",
                        row_label,
                    )
                )
            else:
                seen_sha256[sha256] = row_label

    for row_id in sorted(set(csv_by_id) - seen_ids):
        issues.append(PaperManifestIssue("extra_csv_row", "CSV row has no JSON row", _safe_manifest_label(row_id)))
    return json_rows, issues


def _load_json_manifest(path: Path, root: Path) -> tuple[list[dict[str, Any]], list[PaperManifestIssue]]:
    issues: list[PaperManifestIssue] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_json_object_without_duplicate_keys)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [], [PaperManifestIssue("json_manifest_unreadable", _manifest_diagnostic(path, root, exc))]
    if not isinstance(data, list):
        return [], [PaperManifestIssue("json_manifest_schema", "JSON manifest must be a list")]
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(data):
        if isinstance(item, dict):
            row_id = str(item.get("id") or f"row-{index}")
            for key in item.pop(JSON_DUPLICATE_KEYS_FIELD, ()):
                issues.append(
                    PaperManifestIssue(
                        "duplicate_json_key",
                        f"duplicate JSON key {key!r}",
                        _safe_manifest_label(row_id),
                    )
                )
            rows.append(item)
        else:
            issues.append(PaperManifestIssue("json_row_schema", "JSON row must be an object", f"row-{index}"))
    return rows, issues


def _load_csv_manifest(path: Path, root: Path) -> tuple[list[dict[str, Any]], list[PaperManifestIssue]]:
    issues: list[PaperManifestIssue] = []
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, strict=True)
            fieldnames = list(reader.fieldnames or [])
            issues.extend(_validate_csv_header(fieldnames))
            rows = list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        return [], [PaperManifestIssue("csv_manifest_unreadable", _manifest_diagnostic(path, root, exc))]
    normalized_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        row_id = str(row.get("id") or f"row-{index}")
        try:
            normalized_rows.append(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "url": row["url"],
                    "file": row["file"],
                    "ok": _parse_csv_bool(row["ok"]),
                    "bytes": int(row["bytes"]),
                    "sha256": row["sha256"],
                    "message": row["message"],
                }
            )
        except (KeyError, TypeError, ValueError) as exc:
            issues.append(PaperManifestIssue("csv_row_schema", f"invalid CSV row: {exc}", row_id))
    return normalized_rows, issues


def _validate_row_schema(row: dict[str, Any], row_id: str) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    missing = [field for field in REQUIRED_FIELDS if field not in row]
    if missing:
        issues.append(PaperManifestIssue("missing_fields", f"missing fields {missing}", row_id))
    extra = sorted(set(row) - set(REQUIRED_FIELDS))
    for field in extra:
        issues.append(
            PaperManifestIssue(
                "unsupported_json_field",
                f"unsupported JSON field {_safe_manifest_label(field)!r}",
                row_id,
            )
        )
    for field in ("id", "title", "url", "file", "sha256", "message"):
        if field in row and not isinstance(row[field], str):
            issues.append(PaperManifestIssue("invalid_field_type", f"{field} must be a string", row_id))
    if "ok" in row and not isinstance(row["ok"], bool):
        issues.append(PaperManifestIssue("invalid_field_type", "ok must be boolean", row_id))
    if "bytes" in row and (isinstance(row["bytes"], bool) or not isinstance(row["bytes"], int) or row["bytes"] < 0):
        issues.append(PaperManifestIssue("invalid_field_type", "bytes must be a non-negative integer", row_id))
    if isinstance(row.get("id"), str):
        issues.extend(_validate_paper_id(row["id"], row_id))
    if isinstance(row.get("title"), str):
        issues.extend(_validate_paper_title(row["title"], row_id))
    if isinstance(row.get("url"), str):
        issues.extend(_validate_paper_url(row["url"], row_id))
    if (
        isinstance(row.get("id"), str)
        and isinstance(row.get("url"), str)
        and isinstance(row.get("file"), str)
    ):
        issues.extend(_validate_paper_row_identity(row["id"], row["url"], row["file"], row_id))
    if isinstance(row.get("message"), str):
        issues.extend(_validate_download_message(row["message"], row_id))
    return issues


def _validate_local_pdf(row: dict[str, Any], path: Path, row_id: str) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    expected_bytes = row.get("bytes")
    expected_sha = row.get("sha256")
    file_label = _paper_file_label(row, path)
    try:
        if _is_link_backed_path(path):
            issues.append(
                PaperManifestIssue(
                    "linked_pdf",
                    f"{file_label}: local PDF must not be a symlink or reparse-point entry",
                    row_id,
                )
            )
            return issues
    except OSError as exc:
        issues.append(
            PaperManifestIssue(
                "local_pdf_stat_error",
                f"{file_label}: could not inspect local PDF link state: {redact_sensitive_text(str(exc))}",
                row_id,
            )
        )
        return issues
    try:
        local_stat = path.stat()
    except OSError as exc:
        issues.append(
            PaperManifestIssue(
                "local_pdf_stat_error",
                f"{file_label}: could not inspect local PDF: {redact_sensitive_text(str(exc))}",
                row_id,
            )
        )
        return issues
    if not stat.S_ISREG(local_stat.st_mode):
        issues.append(
            PaperManifestIssue(
                "local_pdf_not_file",
                f"{file_label}: local PDF must be a regular file",
                row_id,
            )
        )
        return issues
    actual_bytes = local_stat.st_size
    if isinstance(expected_bytes, int) and actual_bytes != expected_bytes:
        issues.append(
            PaperManifestIssue(
                "byte_count_mismatch",
                f"expected {expected_bytes} bytes but found {actual_bytes}",
                row_id,
            )
        )
    try:
        if not _has_pdf_header(path):
            issues.append(
                PaperManifestIssue(
                    "invalid_pdf_header",
                    f"{file_label}: local PDF does not start with %PDF-",
                    row_id,
                )
            )
    except OSError as exc:
        issues.append(
            PaperManifestIssue(
                "local_pdf_read_error",
                f"{file_label}: could not read local PDF header: {redact_sensitive_text(str(exc))}",
                row_id,
            )
        )
        return issues
    try:
        reader = _read_pdf_quietly(path)
        if len(reader.pages) < 1:
            issues.append(
                PaperManifestIssue(
                    "invalid_pdf_structure",
                    f"{file_label}: local PDF has no readable pages",
                    row_id,
                )
            )
    except Exception as exc:
        issues.append(
            PaperManifestIssue(
                "invalid_pdf_structure",
                f"{file_label}: local PDF could not be parsed: {_safe_pdf_parse_error(exc)}",
                row_id,
            )
        )
        return issues
    if isinstance(expected_sha, str) and SHA256_RE.fullmatch(expected_sha):
        try:
            actual_sha = _sha256_file(path)
        except OSError as exc:
            issues.append(
                PaperManifestIssue(
                    "local_pdf_read_error",
                    f"{file_label}: could not read local PDF: {redact_sensitive_text(str(exc))}",
                    row_id,
                )
            )
            return issues
        if actual_sha != expected_sha:
            issues.append(PaperManifestIssue("sha256_mismatch", "local PDF digest does not match manifest", row_id))
    return issues


def _read_expected_count(root: Path) -> tuple[int | None, list[PaperManifestIssue]]:
    count_sources: list[ReadmeCountSource] = []
    issues: list[PaperManifestIssue] = []
    for relative_path in (Path("README.md"), Path("papers") / "README.md"):
        path = root / relative_path
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(
                PaperManifestIssue(
                    "readme_count_source_unreadable",
                    _manifest_diagnostic(path, root, exc),
                )
            )
            continue
        for match in README_COUNT_RE.finditer(text):
            count_sources.append(
                ReadmeCountSource(
                    source=relative_path.as_posix(),
                    kind="prose",
                    value=int(match.group(1)),
                    phrase=match.group(0),
                )
            )
        if relative_path == Path("README.md"):
            for match in README_BADGE_RE.finditer(text):
                raw_count = match.group(1)
                if raw_count.isdigit():
                    count_sources.append(
                        ReadmeCountSource(
                            source=relative_path.as_posix(),
                            kind="badge",
                            value=int(raw_count),
                            phrase="local paper cache badge",
                        )
                    )
                else:
                    issues.append(
                        PaperManifestIssue(
                            "malformed_paper_count_badge",
                            "README local paper cache badge count must be numeric",
                        )
                    )
    counts = {source.value for source in count_sources}
    if len(counts) == 1:
        return next(iter(counts)), issues
    if len(counts) > 1:
        issues.append(
            PaperManifestIssue(
                "documented_count_conflict",
                "documented paper counts disagree: "
                + "; ".join(_format_count_source(source) for source in count_sources),
            )
        )
    return None, issues


def _validate_root_readme_paper_summary(root: Path, manifest_ids: set[str]) -> list[PaperManifestIssue]:
    path = root / "README.md"
    if not path.exists() or not manifest_ids:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    section_match = LOCAL_PAPER_CACHE_SECTION_RE.search(text)
    section = section_match.group(0) if section_match else text
    summary_ids = {row_id for row_id in manifest_ids if row_id in section}
    if not summary_ids:
        return []
    if manifest_ids <= summary_ids:
        return []

    normalized_section = section.casefold()
    has_curated_marker = (
        "curated subset" in normalized_section
        and "papers/readme.md" in normalized_section
        and "complete implementation-status index" in normalized_section
    )
    if has_curated_marker:
        return []
    return [
        PaperManifestIssue(
            "readme_paper_summary_incomplete",
            "README.md local paper cache lists "
            f"{len(summary_ids)} of {len(manifest_ids)} manifest ids without saying the tables are a "
            "curated subset and papers/README.md is the complete implementation-status index",
        )
    ]


def _validate_todo_coverage_table(
    root: Path,
    manifest_ids: set[str],
    manifest_rows_by_id: dict[str, dict[str, Any]] | None = None,
) -> list[PaperManifestIssue]:
    path = root / "papers" / "README.md"
    if not path.exists() or not manifest_ids:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [
            PaperManifestIssue(
                "todo_coverage_table_unreadable",
                _manifest_diagnostic(path, root, exc),
            )
        ]

    section = _markdown_section(text, "## TODO coverage cross-references")
    if section is None:
        return []
    issues = _validate_todo_coverage_scope_text(section)
    status_by_id = _status_table_status_cells(text)

    rows: dict[str, tuple[str, str]] = {}
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3 or cells[0] == "ID" or set(cells[0]) <= {"-", ":"}:
            continue
        row_id = cells[0]
        row_label = _safe_manifest_label(row_id)
        if row_id in rows:
            issues.append(
                PaperManifestIssue(
                    "duplicate_todo_coverage_row",
                    "duplicate papers/README.md TODO coverage row",
                    row_label,
                )
            )
            continue
        rows[row_id] = (cells[1], cells[2])

    for row_id in sorted(manifest_ids - set(rows)):
        issues.append(
            PaperManifestIssue(
                "missing_todo_coverage_row",
                "manifest row is missing from papers/README.md TODO coverage table",
                _safe_manifest_label(row_id),
            )
        )
    for row_id in sorted(set(rows) - manifest_ids):
        issues.append(
            PaperManifestIssue(
                "extra_todo_coverage_row",
                "papers/README.md TODO coverage row has no manifest row",
                _safe_manifest_label(row_id),
            )
        )

    for row_id in sorted(manifest_ids & set(rows)):
        active_cell, completed_cell = rows[row_id]
        issues.extend(_validate_active_todo_coverage_cell(root, row_id, active_cell))
        issues.extend(
            _validate_completed_todo_coverage_cell(
                root,
                row_id,
                completed_cell,
                (manifest_rows_by_id or {}).get(row_id),
            )
        )
        issues.extend(
            _validate_status_evidence_links(
                root,
                row_id,
                active_cell,
                completed_cell,
                status_by_id.get(row_id),
                (manifest_rows_by_id or {}).get(row_id),
            )
        )
    return issues


def _validate_todo_coverage_scope_text(section: str) -> list[PaperManifestIssue]:
    normalized = section.casefold()
    advertises_grouped_labels = (
        "grouped open gap" in normalized
        or "grouped labels are accepted" in normalized
        or "grouped labels are allowed" in normalized
    )
    if advertises_grouped_labels:
        return [
            PaperManifestIssue(
                "todo_coverage_grouped_label_policy_ambiguous",
                "papers/README.md TODO coverage prose must not advertise grouped labels unless a grouped-label taxonomy is validated",
            )
        ]
    return []


def _markdown_section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    section_start: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            section_start = index + 1
            break
    if section_start is None:
        return None
    section_lines: list[str] = []
    for line in lines[section_start:]:
        if line.startswith("## "):
            break
        section_lines.append(line)
    return "\n".join(section_lines)


def _validate_active_todo_coverage_cell(root: Path, row_id: str, cell: str) -> list[PaperManifestIssue]:
    row_label = _safe_manifest_label(row_id)
    listed_paths = set(TODO_COVERAGE_PATH_RE.findall(cell))
    issues: list[PaperManifestIssue] = []
    for relative_path in sorted(listed_paths):
        if relative_path not in ACTIVE_TODO_LEDGER_PATHS:
            issues.append(
                PaperManifestIssue(
                    "invalid_active_todo_coverage_path",
                    f"{relative_path} is not an active TODO ledger path",
                    row_label,
                )
            )
        if not (root / relative_path).exists():
            issues.append(
                PaperManifestIssue(
                    "missing_todo_coverage_path",
                    f"{relative_path} does not exist",
                    row_label,
                )
            )

    expected_paths: set[str] = set()
    for relative_path in ACTIVE_TODO_LEDGER_PATHS:
        todo_path = root / relative_path
        if not todo_path.exists():
            continue
        try:
            text = todo_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(
                PaperManifestIssue(
                    "active_todo_coverage_unreadable",
                    _manifest_diagnostic(todo_path, root, exc),
                    row_label,
                )
            )
            continue
        matching_blocks = [block for block in _open_todo_blocks(text) if row_id in block]
        if matching_blocks:
            expected_paths.add(relative_path)
        for block in matching_blocks:
            if not ACTIVE_TODO_GAP_CONTEXT_RE.search(block):
                issues.append(
                    PaperManifestIssue(
                        "active_todo_coverage_block_missing_gap_context",
                        f"{relative_path} has a row-specific open TODO block without Current/Remaining gap or Current evidence context",
                        row_label,
                    )
                )
            if not ACTIVE_TODO_REQUIRED_RESULT_RE.search(block):
                issues.append(
                    PaperManifestIssue(
                        "active_todo_coverage_block_missing_required_result",
                        f"{relative_path} has a row-specific open TODO block without Required result",
                        row_label,
                    )
                )

    if listed_paths != expected_paths:
        missing = sorted(expected_paths - listed_paths)
        extra = sorted(listed_paths - expected_paths)
        parts: list[str] = []
        if missing:
            parts.append(f"missing active paths {missing}")
        if extra:
            parts.append(f"extra active paths {extra}")
        issues.append(
            PaperManifestIssue(
                "todo_coverage_active_mismatch",
                "; ".join(parts) or "active TODO coverage paths do not match open TODO blocks",
                row_label,
            )
        )
    return issues


def _validate_completed_todo_coverage_cell(
    root: Path,
    row_id: str,
    cell: str,
    manifest_row: dict[str, Any] | None = None,
) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    row_label = _safe_manifest_label(row_id)
    source_tokens = _completed_todo_source_tokens(row_id, manifest_row)
    for relative_path in sorted(TODO_COVERAGE_PATH_RE.findall(cell)):
        if not relative_path.startswith("docs/todo/Completed/"):
            issues.append(
                PaperManifestIssue(
                    "invalid_completed_todo_coverage_path",
                    f"{relative_path} is not a completed TODO ledger path",
                    row_label,
                )
            )
            continue
        todo_path = root / relative_path
        if not todo_path.exists():
            issues.append(
                PaperManifestIssue(
                    "missing_todo_coverage_path",
                    f"{relative_path} does not exist",
                    row_label,
                )
            )
            continue
        try:
            text = todo_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(
                PaperManifestIssue(
                    "completed_todo_coverage_unreadable",
                    _manifest_diagnostic(todo_path, root, exc),
                    row_label,
                )
            )
            continue
        if not COMPLETED_TODO_ITEM_RE.search(text):
            issues.append(
                PaperManifestIssue(
                    "completed_todo_coverage_without_completed_item",
                    f"{relative_path} does not contain a completed checklist item",
                    row_label,
                )
            )
            continue
        if not _completed_todo_blocks_contain_any(text, source_tokens):
            issues.append(
                PaperManifestIssue(
                    "completed_todo_coverage_not_source_specific",
                    f"{relative_path} does not contain a completed checklist item for this paper id or source file",
                    row_label,
                )
            )
    return issues


def _completed_todo_source_tokens(row_id: str, manifest_row: dict[str, Any] | None) -> tuple[str, ...]:
    tokens = [row_id]
    if manifest_row is not None:
        file_value = manifest_row.get("file")
        if isinstance(file_value, str) and file_value:
            tokens.append(file_value)
            tokens.append(Path(file_value).name)
            tokens.append(Path(file_value).stem)
    return tuple(dict.fromkeys(tokens))


def _validate_status_evidence_links(
    root: Path,
    row_id: str,
    active_cell: str,
    completed_cell: str,
    status: str | None,
    manifest_row: dict[str, Any] | None = None,
) -> list[PaperManifestIssue]:
    row_label = _safe_manifest_label(row_id)
    active_paths = TODO_COVERAGE_PATH_RE.findall(active_cell)
    completed_paths = TODO_COVERAGE_PATH_RE.findall(completed_cell)
    issues: list[PaperManifestIssue] = []
    if not active_paths:
        issues.append(
            PaperManifestIssue(
                "missing_active_status_evidence",
                "paper status row must link at least one active TODO evidence path",
                row_label,
            )
        )
    if (
        status is not None
        and status.startswith(STATUS_TABLE_STATUSES_REQUIRING_COMPLETED_EVIDENCE)
        and not completed_paths
    ):
        issues.append(
            PaperManifestIssue(
                "missing_completed_status_evidence",
                "paper status row claims implemented or local-only support without completed evidence paths",
                row_label,
            )
        )
    if status is not None:
        status_artifact_paths = _status_local_artifact_paths(status)
        if status_artifact_paths:
            evidence_text = _status_evidence_text(root, row_id, active_paths + completed_paths, manifest_row)
            missing_artifacts = sorted(path for path in status_artifact_paths if path not in evidence_text)
            if missing_artifacts:
                issues.append(
                    PaperManifestIssue(
                        "status_table_local_artifact_unlinked_evidence",
                        "status local artifact paths must also appear in linked active or completed TODO evidence: "
                        f"{[_safe_manifest_label(path) for path in missing_artifacts]}",
                        row_label,
                    )
                )
    return issues


def _status_local_artifact_paths(status: str) -> set[str]:
    return {match.group(0).strip("`") for match in LOCAL_ARTIFACT_PATH_RE.finditer(status)}


def _status_local_artifact_mention_records(
    status_text: str,
    line_number: int,
    *,
    status_text_char_offset: int = 0,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for match in LOCAL_ARTIFACT_PATH_RE.finditer(status_text):
        start = status_text_char_offset + match.start()
        end = status_text_char_offset + match.end()
        records.append(
            {
                "path": match.group(0).strip("`"),
                "status_text_char_start": start,
                "status_text_char_end": end,
                "source_span": {
                    "path": "papers/README.md",
                    "section": "Implementation status",
                    "line_start": line_number,
                    "line_end": line_number,
                    "status_text_char_start": start,
                    "status_text_char_end": end,
                },
            }
        )
    return records


def _local_artifact_path_records(root: Path, paths: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for relative_path in paths:
        path = root / relative_path
        exists = path.exists()
        if path.is_file():
            kind = "file"
        elif path.is_dir():
            kind = "directory"
        elif exists:
            kind = "other"
        else:
            kind = "missing"
        records.append(
            {
                "path": relative_path,
                "exists": exists,
                "kind": kind,
            }
        )
    return records


def _status_evidence_text(
    root: Path,
    row_id: str,
    evidence_paths: list[str],
    manifest_row: dict[str, Any] | None,
) -> str:
    source_tokens = _completed_todo_source_tokens(row_id, manifest_row)
    evidence_blocks: list[str] = []
    for relative_path in dict.fromkeys(evidence_paths):
        path = root / relative_path
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        evidence_blocks.extend(block for block in _open_todo_blocks(text) if any(token in block for token in source_tokens))
        evidence_blocks.extend(block for block in _completed_todo_blocks(text) if any(token in block for token in source_tokens))
    return "\n".join(evidence_blocks)


def _status_todo_evidence_content_records(
    root: Path,
    row_id: str,
    evidence_paths: list[str],
    manifest_row: dict[str, Any] | None,
    row_local_artifact_paths: list[str],
    evidence_kind: str,
) -> list[dict[str, Any]]:
    source_tokens = _completed_todo_source_tokens(row_id, manifest_row)
    records: list[dict[str, Any]] = []
    for relative_path in dict.fromkeys(evidence_paths):
        path = root / relative_path
        base_record = _local_artifact_path_records(root, [relative_path])[0]
        readable = False
        matching_blocks: list[str] = []
        matching_block_records: list[dict[str, Any]] = []
        matched_tokens: set[str] = set()
        if path.exists():
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                text = ""
            else:
                readable = True
                for block_record in _todo_block_span_records(text):
                    block = block_record["text"]
                    block_tokens = sorted(token for token in source_tokens if token in block)
                    if block_tokens:
                        block_artifact_records = _todo_content_local_artifact_mention_records(
                            block,
                            row_local_artifact_paths,
                        )
                        matching_blocks.append(block)
                        matched_tokens.update(block_tokens)
                        matching_block_records.append(
                            {
                                "block_kind": block_record["block_kind"],
                                "block_ordinal": block_record["block_ordinal"],
                                "file_text_char_start": block_record["file_text_char_start"],
                                "file_text_char_end": block_record["file_text_char_end"],
                                "line_start": block_record["line_start"],
                                "line_end": block_record["line_end"],
                                "block_sha256": block_record["block_sha256"],
                                "matched_source_tokens": block_tokens,
                                "mentioned_local_artifact_records": block_artifact_records,
                                "mentioned_local_artifact_paths": sorted(
                                    {record["path"] for record in block_artifact_records}
                                ),
                            }
                        )
        evidence_text = "\n".join(matching_blocks)
        mentioned_artifact_records = _todo_content_local_artifact_mention_records(
            evidence_text,
            row_local_artifact_paths,
        )
        mentioned_artifacts = sorted({record["path"] for record in mentioned_artifact_records})
        missing_artifacts = sorted(set(row_local_artifact_paths) - set(mentioned_artifacts))
        records.append(
            {
                **base_record,
                "evidence_kind": evidence_kind,
                "readable": readable,
                "row_source_tokens_matched": sorted(matched_tokens),
                "row_source_token_match_count": len(matched_tokens),
                "row_specific_block_count": len(matching_blocks),
                "row_specific_block_records": matching_block_records,
                "mentioned_local_artifact_records": mentioned_artifact_records,
                "mentioned_local_artifact_paths": mentioned_artifacts,
                "missing_local_artifact_paths": missing_artifacts,
                "content_evidence_status": (
                    "row_local_artifacts_mentioned"
                    if row_local_artifact_paths and not missing_artifacts
                    else "missing_row_local_artifact_mentions"
                    if missing_artifacts
                    else "no_row_local_artifacts_referenced"
                ),
            }
        )
    return records


def _todo_content_local_artifact_mention_records(
    evidence_text: str,
    row_local_artifact_paths: list[str],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for artifact in row_local_artifact_paths:
        start = 0
        while True:
            index = evidence_text.find(artifact, start)
            if index < 0:
                break
            end = index + len(artifact)
            records.append(
                {
                    "path": artifact,
                    "evidence_text_char_start": index,
                    "evidence_text_char_end": end,
                }
            )
            start = end
    return sorted(
        records,
        key=lambda record: (
            record["evidence_text_char_start"],
            record["evidence_text_char_end"],
            record["path"],
        ),
    )


def _status_table_status_cells(text: str) -> dict[str, str]:
    section = _markdown_section(text, "## Implementation status")
    if section is None:
        return {}
    statuses: dict[str, str] = {}
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(STATUS_TABLE_HEADER) or cells[0] == "ID" or set(cells[0]) <= {"-", ":"}:
            continue
        statuses[cells[0]] = cells[3]
    return statuses


def _read_todo_coverage_table_cells(root: Path) -> tuple[dict[str, tuple[str, str]], list[PaperManifestIssue]]:
    path = root / "papers" / "README.md"
    if not path.exists():
        return {}, []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return {}, [
            PaperManifestIssue(
                "todo_coverage_table_unreadable",
                _manifest_diagnostic(path, root, exc),
            )
        ]
    section = _markdown_section(text, "## TODO coverage cross-references")
    if section is None:
        return {}, []
    rows: dict[str, tuple[str, str]] = {}
    issues: list[PaperManifestIssue] = []
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3 or cells[0] == "ID" or set(cells[0]) <= {"-", ":"}:
            continue
        row_id = cells[0]
        row_label = _safe_manifest_label(row_id)
        if row_id in rows:
            issues.append(
                PaperManifestIssue(
                    "duplicate_todo_coverage_row",
                    "duplicate papers/README.md TODO coverage row",
                    row_label,
                )
            )
            continue
        rows[row_id] = (cells[1], cells[2])
    return rows, issues


def _status_claim_inventory_class(status_text: str) -> str:
    for prefix in ALLOWED_STATUS_TABLE_STATUS_PREFIXES:
        if status_text.startswith(prefix):
            return prefix.rstrip(" :;")
    return "unknown"


def _status_claim_inventory_paths(cell: str) -> list[str]:
    return list(dict.fromkeys(TODO_COVERAGE_PATH_RE.findall(cell)))


def _status_todo_evidence_path_mention_records(cell: str, evidence_kind: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for match in TODO_COVERAGE_PATH_RE.finditer(cell):
        records.append(
            {
                "path": match.group(1),
                "evidence_kind": evidence_kind,
                "todo_cell_char_start": match.start(),
                "todo_cell_char_end": match.end(),
            }
        )
    return records


def _status_claim_inventory_phrases(
    root: Path,
    row_id: str,
    status_text: str,
    line_number: int,
    active_paths: list[str],
    completed_paths: list[str],
    active_todo_records: list[dict[str, Any]],
    completed_todo_records: list[dict[str, Any]],
    active_todo_content_records: list[dict[str, Any]],
    completed_todo_content_records: list[dict[str, Any]],
    row_local_artifact_paths: list[str],
) -> list[dict[str, Any]]:
    phrases: list[dict[str, Any]] = []
    todo_content_records = [*active_todo_content_records, *completed_todo_content_records]
    for ordinal, (start, end) in enumerate(_status_claim_phrase_spans(status_text), start=1):
        phrase = status_text[start:end]
        phrase_local_artifact_mention_records = _status_local_artifact_mention_records(
            phrase,
            line_number,
            status_text_char_offset=start,
        )
        phrase_local_artifact_paths = sorted(
            {record["path"] for record in phrase_local_artifact_mention_records}
        )
        phrase_local_artifact_records = _local_artifact_path_records(root, phrase_local_artifact_paths)
        phrase_missing_local_artifacts = [
            record["path"] for record in phrase_local_artifact_records if not record["exists"]
        ]
        phrase_artifacts_mentioned_in_todo = sorted(
            {
                artifact
                for record in todo_content_records
                for artifact in record["mentioned_local_artifact_paths"]
                if artifact in phrase_local_artifact_paths
            }
        )
        phrase_artifacts_missing_from_todo = sorted(
            set(phrase_local_artifact_paths) - set(phrase_artifacts_mentioned_in_todo)
        )
        phrase_todo_content_block_records = _phrase_todo_content_block_records(
            todo_content_records,
            phrase_local_artifact_paths,
        )
        absence_signal_records = _status_absence_signal_records(
            phrase,
            line_number,
            status_text_char_offset=start,
        )
        absence_signal_terms = list(
            dict.fromkeys(record["term"] for record in absence_signal_records)
        )
        phrases.append(
            {
                "claim_id": f"{row_id}:status_phrase_{ordinal:03d}",
                "phrase_ordinal": ordinal,
                "status_text_char_start": start,
                "status_text_char_end": end,
                "phrase_sha256": hashlib.sha256(phrase.encode("utf-8")).hexdigest(),
                "source_span": {
                    "path": "papers/README.md",
                    "section": "Implementation status",
                    "line_start": line_number,
                    "line_end": line_number,
                    "status_text_char_start": start,
                    "status_text_char_end": end,
                },
                "evidence_links": {
                    "phrase_local_artifact_paths": phrase_local_artifact_paths,
                    "phrase_local_artifact_mention_records": phrase_local_artifact_mention_records,
                    "phrase_local_artifact_records": phrase_local_artifact_records,
                    "phrase_local_artifact_missing_paths": phrase_missing_local_artifacts,
                    "phrase_artifact_existence_status": (
                        "all_referenced_local_artifacts_present"
                        if phrase_local_artifact_paths and not phrase_missing_local_artifacts
                        else "missing_referenced_local_artifacts"
                        if phrase_missing_local_artifacts
                        else "no_local_artifacts_referenced"
                    ),
                    "row_local_artifact_paths": row_local_artifact_paths,
                    "row_active_todo_paths": active_paths,
                    "row_completed_todo_paths": completed_paths,
                    "row_active_todo_records": active_todo_records,
                    "row_completed_todo_records": completed_todo_records,
                    "phrase_local_artifacts_mentioned_in_todo_evidence": phrase_artifacts_mentioned_in_todo,
                    "phrase_local_artifacts_missing_from_todo_evidence": phrase_artifacts_missing_from_todo,
                    "phrase_todo_content_block_records": phrase_todo_content_block_records,
                    "phrase_todo_content_evidence_status": (
                        "all_phrase_local_artifacts_mentioned_in_todo_evidence"
                        if phrase_local_artifact_paths and not phrase_artifacts_missing_from_todo
                        else "missing_phrase_local_artifact_mentions_in_todo_evidence"
                        if phrase_artifacts_missing_from_todo
                        else "no_phrase_local_artifacts_referenced"
                    ),
                },
                "absence_signal_records": absence_signal_records,
                "absence_signal_terms": absence_signal_terms,
                "has_absence_signal": bool(absence_signal_terms),
                "absence_signal_status": (
                    "absence_signal_structurally_classified"
                    if absence_signal_terms
                    else "no_absence_signal_detected"
                ),
                "freshness_status": "not_verified",
                "evidence_link_status": "candidate_links_recorded_without_semantic_verification",
                "semantic_status": "not_verified",
            }
        )
    return phrases


def _phrase_todo_content_block_records(
    todo_content_records: list[dict[str, Any]],
    phrase_local_artifact_paths: list[str],
) -> list[dict[str, Any]]:
    phrase_artifacts = set(phrase_local_artifact_paths)
    if not phrase_artifacts:
        return []
    records: list[dict[str, Any]] = []
    for content_record in todo_content_records:
        for block_record in content_record["row_specific_block_records"]:
            block_artifacts = [
                path
                for path in block_record["mentioned_local_artifact_paths"]
                if path in phrase_artifacts
            ]
            if not block_artifacts:
                continue
            artifact_records = [
                record
                for record in block_record["mentioned_local_artifact_records"]
                if record["path"] in phrase_artifacts
            ]
            records.append(
                {
                    "path": content_record["path"],
                    "evidence_kind": content_record["evidence_kind"],
                    "block_kind": block_record["block_kind"],
                    "block_ordinal": block_record["block_ordinal"],
                    "file_text_char_start": block_record["file_text_char_start"],
                    "file_text_char_end": block_record["file_text_char_end"],
                    "line_start": block_record["line_start"],
                    "line_end": block_record["line_end"],
                    "block_sha256": block_record["block_sha256"],
                    "matched_source_tokens": block_record["matched_source_tokens"],
                    "phrase_local_artifact_paths_mentioned": sorted(block_artifacts),
                    "mentioned_local_artifact_records": artifact_records,
                }
            )
    return sorted(
        records,
        key=lambda record: (
            record["path"],
            record["evidence_kind"],
            record["block_kind"],
            record["block_ordinal"],
            record["file_text_char_start"],
        ),
    )


def _status_absence_signal_records(
    phrase: str,
    line_number: int,
    *,
    status_text_char_offset: int = 0,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for match in STATUS_ABSENCE_SIGNAL_RE.finditer(phrase):
        term = re.sub(r"\s+", " ", match.group(0).strip().lower())
        if not term:
            continue
        phrase_start = match.start()
        phrase_end = match.end()
        status_start = status_text_char_offset + phrase_start
        status_end = status_text_char_offset + phrase_end
        records.append(
            {
                "term": term,
                "phrase_text_char_start": phrase_start,
                "phrase_text_char_end": phrase_end,
                "status_text_char_start": status_start,
                "status_text_char_end": status_end,
                "source_span": {
                    "path": "papers/README.md",
                    "section": "Implementation status",
                    "line_start": line_number,
                    "line_end": line_number,
                    "status_text_char_start": status_start,
                    "status_text_char_end": status_end,
                },
            }
        )
    return records


def _status_claim_phrase_spans(status_text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    start = 0
    in_code = False
    for index, char in enumerate(status_text):
        if char == "`":
            in_code = not in_code
            continue
        if in_code or char not in ".;":
            continue
        next_index = index + 1
        if next_index < len(status_text) and not status_text[next_index].isspace():
            continue
        segment_start = start
        segment_end = next_index
        while segment_start < segment_end and status_text[segment_start].isspace():
            segment_start += 1
        while segment_end > segment_start and status_text[segment_end - 1].isspace():
            segment_end -= 1
        if segment_start < segment_end:
            spans.append((segment_start, segment_end))
        start = next_index
    segment_start = start
    segment_end = len(status_text)
    while segment_start < segment_end and status_text[segment_start].isspace():
        segment_start += 1
    while segment_end > segment_start and status_text[segment_end - 1].isspace():
        segment_end -= 1
    if segment_start < segment_end:
        spans.append((segment_start, segment_end))
    return spans


def _validate_todo_absence_wording(root: Path, manifest_ids: set[str]) -> list[PaperManifestIssue]:
    if not manifest_ids:
        return []
    issues: list[PaperManifestIssue] = []
    blocks_by_path: dict[str, list[str]] = {}
    for relative_path in ACTIVE_TODO_LEDGER_PATHS:
        todo_path = root / relative_path
        if not todo_path.exists():
            continue
        try:
            text = todo_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(
                PaperManifestIssue(
                    "active_todo_absence_wording_unreadable",
                    _manifest_diagnostic(todo_path, root, exc),
                )
            )
            continue
        blocks_by_path[relative_path] = _open_todo_blocks(text)

    for row_id in sorted(manifest_ids):
        row_label = _safe_manifest_label(row_id)
        active_paths = {
            relative_path
            for relative_path, blocks in blocks_by_path.items()
            if any(row_id in block for block in blocks)
        }
        if not active_paths:
            continue
        for source_path, blocks in blocks_by_path.items():
            for block in blocks:
                if row_id not in block:
                    continue
                for match in SOURCE_SPECIFIC_ABSENCE_RE.finditer(block):
                    for target_name in match.group(1).split("/"):
                        target_path = SOURCE_SPECIFIC_TODO_TARGET_PATHS.get(target_name.casefold())
                        if target_path is None or target_path not in active_paths:
                            continue
                        issues.append(
                            PaperManifestIssue(
                                "stale_source_specific_absence_wording",
                                f"{source_path} says no source-specific {target_name} TODO, "
                                f"but {target_path} has an open TODO block for this paper id",
                                row_label,
                            )
                        )
    return issues


def _validate_benchmark_coverage_decisions(root: Path) -> list[PaperManifestIssue]:
    bullets, read_issues = _read_implemented_benchmark_bullet_records(root)
    if read_issues:
        return read_issues
    issues: list[PaperManifestIssue] = []
    for bullet in bullets:
        block = bullet["text"]
        summary = block.splitlines()[0].strip()
        if not BENCHMARK_IMPLEMENTED_LOCAL_ARTIFACT_RE.search(block):
            issues.append(
                PaperManifestIssue(
                    "benchmark_implemented_missing_local_artifact",
                    f"Implemented benchmark coverage bullet must cite a local code or artifact path: {summary}",
                )
            )
        if not BENCHMARK_IMPLEMENTED_LIMITATION_BOUNDARY_RE.search(block):
            issues.append(
                PaperManifestIssue(
                    "benchmark_implemented_missing_limitation_boundary",
                    f"Implemented benchmark coverage bullet must state the remaining scope or limitation: {summary}",
                )
            )
        if not BENCHMARK_IMPLEMENTED_NOT_IMPLEMENTED_RE.search(block):
            continue
        issues.append(
            PaperManifestIssue(
                "benchmark_implemented_not_implemented_contradiction",
                f"Implemented benchmark coverage bullet is phrased as not implemented: {summary}",
            )
        )
    return issues


def _open_todo_blocks(text: str) -> list[str]:
    starts = [match.start() for match in re.finditer(r"(?m)^- \[ \] ", text)]
    starts.append(len(text))
    return [text[start:end] for start, end in zip(starts, starts[1:])]


def _todo_block_span_records(text: str) -> list[dict[str, Any]]:
    return [
        *_todo_block_span_records_for_marker(text, r"(?m)^- \[ \] ", "active"),
        *_todo_block_span_records_for_marker(text, r"(?m)^- \[x\] ", "completed"),
    ]


def _todo_block_span_records_for_marker(
    text: str,
    pattern: str,
    block_kind: str,
) -> list[dict[str, Any]]:
    starts = [match.start() for match in re.finditer(pattern, text)]
    starts.append(len(text))
    records: list[dict[str, Any]] = []
    for ordinal, (start, end) in enumerate(zip(starts, starts[1:]), start=1):
        block = text[start:end]
        if not block:
            continue
        records.append(
            {
                "text": block,
                "block_kind": block_kind,
                "block_ordinal": ordinal,
                "file_text_char_start": start,
                "file_text_char_end": end,
                "line_start": text.count("\n", 0, start) + 1,
                "line_end": text.count("\n", 0, end) + 1,
                "block_sha256": hashlib.sha256(block.encode("utf-8")).hexdigest(),
            }
        )
    return records


def _markdown_bullet_blocks(text: str) -> list[str]:
    starts = [match.start() for match in re.finditer(r"(?m)^- ", text)]
    starts.append(len(text))
    return [text[start:end] for start, end in zip(starts, starts[1:])]


def _read_implemented_benchmark_bullet_records(root: Path) -> tuple[list[dict[str, Any]], list[PaperManifestIssue]]:
    path = root / "papers" / "README.md"
    if not path.exists():
        return [], []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [], [
            PaperManifestIssue(
                "benchmark_coverage_unreadable",
                _manifest_diagnostic(path, root, exc),
            )
        ]
    section = _markdown_section(text, "## Benchmark coverage decisions")
    if section is None or "Implemented:" not in section:
        return [], []
    section_start = text.find(section)
    if section_start < 0:
        return [], []
    implemented_start = section.find("Implemented:")
    implemented_end = section.find("\nPlanned or background-only:", implemented_start)
    if implemented_end < 0:
        implemented_end = len(section)
    implemented_text = section[implemented_start + len("Implemented:") : implemented_end]
    implemented_absolute_start = section_start + implemented_start + len("Implemented:")
    starts = [match.start() for match in re.finditer(r"(?m)^- ", implemented_text)]
    starts.append(len(implemented_text))
    records: list[dict[str, Any]] = []
    for start, end in zip(starts, starts[1:]):
        block = implemented_text[start:end].rstrip()
        if not block:
            continue
        absolute_start = implemented_absolute_start + start
        absolute_end = absolute_start + len(block)
        records.append(
            {
                "text": block,
                "file_text_char_start": absolute_start,
                "file_text_char_end": absolute_end,
                "line_start": text.count("\n", 0, absolute_start) + 1,
                "line_end": text.count("\n", 0, absolute_end) + 1,
            }
        )
    return records, []


def _benchmark_local_artifact_mention_records(
    text: str,
    bullet_line_start: int,
    bullet_file_start: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for match in LOCAL_ARTIFACT_PATH_RE.finditer(text):
        path = match.group(0).strip("`")
        start = match.start()
        end = match.end()
        records.append(
            {
                "path": path,
                "bullet_text_char_start": start,
                "bullet_text_char_end": end,
                "source_span": {
                    "path": "papers/README.md",
                    "section": "Benchmark coverage decisions",
                    "line_start": bullet_line_start + text.count("\n", 0, start),
                    "line_end": bullet_line_start + text.count("\n", 0, end),
                    "bullet_text_char_start": start,
                    "bullet_text_char_end": end,
                    "file_text_char_start": bullet_file_start + start,
                    "file_text_char_end": bullet_file_start + end,
                },
            }
        )
    return records


def _benchmark_source_token_match_records(
    text: str,
    bullet_line_start: int,
    bullet_file_start: int,
    manifest_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for manifest_row in manifest_rows:
        row_id = manifest_row.get("id")
        if not isinstance(row_id, str) or not row_id:
            continue
        for token in _completed_todo_source_tokens(row_id, manifest_row):
            start = 0
            while True:
                index = text.find(token, start)
                if index < 0:
                    break
                end = index + len(token)
                records.append(
                    {
                        "row_id": row_id,
                        "token": token,
                        "bullet_text_char_start": index,
                        "bullet_text_char_end": end,
                        "source_span": {
                            "path": "papers/README.md",
                            "section": "Benchmark coverage decisions",
                            "line_start": bullet_line_start + text.count("\n", 0, index),
                            "line_end": bullet_line_start + text.count("\n", 0, end),
                            "bullet_text_char_start": index,
                            "bullet_text_char_end": end,
                            "file_text_char_start": bullet_file_start + index,
                            "file_text_char_end": bullet_file_start + end,
                        },
                    }
                )
                start = end
    return sorted(
        records,
        key=lambda record: (
            record["bullet_text_char_start"],
            record["bullet_text_char_end"],
            record["row_id"],
            record["token"],
        ),
    )


def _benchmark_limitation_signal_records(
    text: str,
    bullet_line_start: int,
    bullet_file_start: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for match in BENCHMARK_IMPLEMENTED_LIMITATION_BOUNDARY_RE.finditer(text):
        term = re.sub(r"\s+", " ", match.group(0).strip().lower())
        if not term:
            continue
        start = match.start()
        end = match.end()
        records.append(
            {
                "term": term,
                "bullet_text_char_start": start,
                "bullet_text_char_end": end,
                "source_span": {
                    "path": "papers/README.md",
                    "section": "Benchmark coverage decisions",
                    "line_start": bullet_line_start + text.count("\n", 0, start),
                    "line_end": bullet_line_start + text.count("\n", 0, end),
                    "bullet_text_char_start": start,
                    "bullet_text_char_end": end,
                    "file_text_char_start": bullet_file_start + start,
                    "file_text_char_end": bullet_file_start + end,
                },
            }
        )
    return records


def _open_todo_blocks_contain(text: str, needle: str) -> bool:
    return any(needle in block for block in _open_todo_blocks(text))


def _completed_todo_blocks(text: str) -> list[str]:
    starts = [match.start() for match in re.finditer(r"(?m)^- \[x\] ", text)]
    starts.append(len(text))
    return [text[start:end] for start, end in zip(starts, starts[1:])]


def _completed_todo_blocks_contain_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(any(needle in block for needle in needles) for block in _completed_todo_blocks(text))


def _format_count_source(source: ReadmeCountSource) -> str:
    phrase = redact_sensitive_text(source.phrase.strip())
    if len(phrase) > 80:
        phrase = f"{phrase[:77]}..."
    return f"{source.source} {source.kind}={source.value} ({phrase})"


def _manifest_diagnostic(path: Path, root: Path, exc: BaseException) -> str:
    label = _manifest_path_label(path, root)
    message = str(exc)
    replacements = {
        str(path): label,
        path.as_posix(): label,
        str(path.absolute()): label,
        path.absolute().as_posix(): label,
    }
    try:
        resolved_path = path.resolve(strict=False)
    except OSError:
        resolved_path = None
    if resolved_path is not None:
        replacements[str(resolved_path)] = label
        replacements[resolved_path.as_posix()] = label
    for raw, safe in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        if raw:
            message = message.replace(raw, safe)
    return f"{label}: {redact_sensitive_text(message)}"


def _manifest_path_label(path: Path, root: Path) -> str:
    try:
        label = path.relative_to(root).as_posix()
    except ValueError:
        label = path.name
    safe_label = redact_sensitive_text(label)
    if safe_label == label:
        return label
    digest = hashlib.sha256(label.encode("utf-8", errors="surrogatepass")).hexdigest()[:12]
    return f"{safe_label}#sha256={digest}"


def _read_status_table_ids(root: Path) -> tuple[list[str] | None, list[PaperManifestIssue]]:
    rows, issues = _read_status_table_rows(root)
    if rows is None:
        return None, issues
    return [cells[0] for cells in rows], issues


def _read_status_table_rows(root: Path) -> tuple[list[list[str]] | None, list[PaperManifestIssue]]:
    records, issues = _read_status_table_row_records(root)
    if records is None:
        return None, issues
    return [record["cells"] for record in records], issues


def _read_status_table_row_records(root: Path) -> tuple[list[dict[str, Any]] | None, list[PaperManifestIssue]]:
    path = root / "papers" / "README.md"
    if not path.exists():
        return None, []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return None, [
            PaperManifestIssue(
                "status_table_unreadable",
                _manifest_diagnostic(path, root, exc),
            )
        ]
    in_section = False
    header_seen = False
    rows: list[dict[str, Any]] = []
    issues: list[PaperManifestIssue] = []
    seen: set[str] = set()
    table_closed = False
    non_contiguous_reported = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.strip() == "## Implementation status":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        if not line.startswith("|"):
            if header_seen and rows and line.strip():
                table_closed = True
            continue
        if table_closed and not non_contiguous_reported:
            issues.append(
                PaperManifestIssue(
                    "status_table_non_contiguous",
                    "implementation status rows must be one contiguous markdown table before prose notes",
                )
            )
            non_contiguous_reported = True
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells:
            continue
        if cells[0] == "ID":
            header_seen = True
            if tuple(cells) != STATUS_TABLE_HEADER:
                issues.append(
                    PaperManifestIssue(
                        "status_table_header_mismatch",
                        f"implementation status header must exactly match {list(STATUS_TABLE_HEADER)}",
                    )
                )
            continue
        if set(cells[0]) <= {"-", ":"}:
            continue
        if len(cells) != len(STATUS_TABLE_HEADER):
            row_label = _safe_manifest_label(cells[0]) if cells else None
            issues.append(
                PaperManifestIssue(
                    "status_table_row_shape",
                    "implementation status rows must have exactly four cells",
                    row_label,
                )
            )
            continue
        row_id = cells[0]
        safe_row_id = _safe_manifest_label(row_id)
        issues.extend(_validate_status_table_row_cells(cells, safe_row_id))
        if row_id in seen:
            issues.append(
                PaperManifestIssue(
                    "duplicate_status_table_row",
                    "duplicate papers/README.md implementation status row",
                    safe_row_id,
                )
            )
        seen.add(row_id)
        rows.append({"line_number": line_number, "cells": cells})
    if not in_section or not rows:
        return None, issues
    if not header_seen:
        issues.append(PaperManifestIssue("missing_status_table_header", "implementation status header is missing"))
    return rows, issues


def _validate_status_table_row_cells(cells: list[str], row_id: str) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    for index, field_name in enumerate(STATUS_TABLE_HEADER):
        value = cells[index]
        if not value.strip():
            issues.append(PaperManifestIssue("empty_status_table_cell", f"{field_name} cell must be non-empty", row_id))
        if _has_unsafe_text(value) or redact_sensitive_text(value) != value:
            issues.append(
                PaperManifestIssue(
                    "unsafe_status_table_cell",
                    f"{field_name} cell must be display-safe and secret-free",
                    row_id,
                )
            )
    role = cells[2]
    if role and role not in ALLOWED_STATUS_TABLE_ROLES:
        issues.append(
            PaperManifestIssue(
                "invalid_status_table_role",
                "implementation status role is not in the allowed paper-facing taxonomy",
                row_id,
            )
        )
    status = cells[3]
    if status and not status.startswith(ALLOWED_STATUS_TABLE_STATUS_PREFIXES):
        issues.append(
            PaperManifestIssue(
                "invalid_status_table_status",
                "implementation status must start with an allowed support/status class",
                row_id,
            )
        )
    allowed_status_prefixes = STATUS_TABLE_ROLE_STATUS_PREFIXES.get(role)
    if role and status and allowed_status_prefixes is not None and not status.startswith(allowed_status_prefixes):
        issues.append(
            PaperManifestIssue(
                "status_table_role_status_mismatch",
                "implementation status class is not compatible with the paper-facing role",
                row_id,
            )
        )
    if (
        status
        and STATUS_TABLE_ALPHAEVOLVE_COMPARABLE_RE.search(status)
        and not STATUS_TABLE_ALPHAEVOLVE_COMPARABLE_BOUNDARY_RE.search(status)
    ):
        issues.append(
            PaperManifestIssue(
                "status_table_alphaevolve_comparable_overclaim",
                "AlphaEvolve-comparable status claims must be framed as missing, scoped, or requirement-bound evidence",
                row_id,
            )
        )
    if (
        status
        and status.startswith(STATUS_TABLE_STATUSES_REQUIRING_COMPLETED_EVIDENCE)
        and not LOCAL_ARTIFACT_PATH_RE.search(status)
    ):
        issues.append(
            PaperManifestIssue(
                "status_table_supported_status_missing_local_artifact",
                "implemented, partial, limited, and static-guidance status claims must cite a local code or artifact path",
                row_id,
            )
        )
    for prefix in STATUS_TABLE_NEGATIVE_IMPLEMENTATION_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if STATUS_TABLE_POSITIVE_IMPLEMENTATION_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_negative_status_contradiction",
                    "negative or background-only status classes must not include positive implementation claims",
                    row_id,
                )
            )
        break
    for prefix in STATUS_TABLE_BACKGROUND_ONLY_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if not STATUS_TABLE_LIMITATION_BOUNDARY_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_background_only_missing_boundary",
                    "background-only status classes must name a missing or unsupported paper behavior",
                    row_id,
                )
            )
        break
    for prefix in STATUS_TABLE_FUTURE_BENCHMARK_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if not STATUS_TABLE_LIMITATION_BOUNDARY_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_future_benchmark_missing_boundary",
                    "future-benchmark status classes must name a missing verifier, harness, or unsupported paper behavior",
                    row_id,
                )
            )
        break
    for prefix in STATUS_TABLE_IMPLEMENTED_STATUS_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if not STATUS_TABLE_LIMITATION_BOUNDARY_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_implemented_status_missing_boundary",
                    "implemented status classes must include an explicit scoped, open, or out-of-scope behavior boundary",
                    row_id,
                )
            )
        break
    for prefix in STATUS_TABLE_LIMITED_STATUS_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if not STATUS_TABLE_LIMITATION_BOUNDARY_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_limited_status_missing_boundary",
                    "limited-support status classes must include an explicit missing or unsupported behavior boundary",
                    row_id,
                )
            )
        break
    for prefix in STATUS_TABLE_PARTIAL_STATUS_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if not STATUS_TABLE_LIMITATION_BOUNDARY_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_partial_status_missing_boundary",
                    "partial status classes must include an explicit remaining, missing, or unsupported behavior boundary",
                    row_id,
                )
            )
        break
    for prefix in STATUS_TABLE_STATIC_GUIDANCE_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if not STATUS_TABLE_STATIC_GUIDANCE_EXECUTION_BOUNDARY_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_static_guidance_missing_execution_boundary",
                    "static-guidance status classes must state that the guided operation is not executed or enforced",
                    row_id,
                )
            )
        break
    for prefix in STATUS_TABLE_NOT_IMPLEMENTED_AS_DESCRIBED_PREFIXES:
        if not status.startswith(prefix):
            continue
        suffix = status[len(prefix) :]
        if not STATUS_TABLE_LIMITATION_BOUNDARY_RE.search(suffix):
            issues.append(
                PaperManifestIssue(
                    "status_table_not_implemented_missing_boundary",
                    "not-implemented-as-described status classes must name a missing or unsupported paper behavior",
                    row_id,
                )
            )
        break
    return issues


def _canonical_row(row: dict[str, Any]) -> dict[str, Any]:
    return {field: row.get(field) for field in REQUIRED_FIELDS}


def _is_safe_paper_path(value: str) -> bool:
    if "\\" in value or _has_unsafe_text(value):
        return False
    path = PurePosixPath(value)
    name = path.name
    stem = path.stem
    first_stem_segment = stem.split(".", 1)[0].upper()
    return (
        len(path.parts) == 2
        and path.parts[0] == "papers"
        and path.suffix == ".pdf"
        and PAPER_FILE_NAME_RE.fullmatch(name) is not None
        and not name.startswith(".")
        and not name.endswith((".", " "))
        and first_stem_segment not in WINDOWS_RESERVED_NAMES
    )


def _normalized_paper_file_key(value: str) -> str:
    return PurePosixPath(value).as_posix().casefold()


def _json_object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    duplicate_keys: list[str] = []
    for key, value in pairs:
        if key in result:
            duplicate_keys.append(key)
            continue
        result[key] = value
    if duplicate_keys:
        result[JSON_DUPLICATE_KEYS_FIELD] = duplicate_keys
    return result


def _validate_csv_header(fieldnames: list[str]) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    if not fieldnames:
        return [PaperManifestIssue("csv_header_missing", "CSV manifest must include a header")]
    seen: set[str] = set()
    for index, field in enumerate(fieldnames):
        if field in seen:
            issues.append(
                PaperManifestIssue(
                    "duplicate_csv_header",
                    f"duplicate CSV header {field!r} at position {index + 1}",
                )
            )
        seen.add(field)
    missing = [field for field in REQUIRED_FIELDS if field not in fieldnames]
    extra = [field for field in fieldnames if field not in REQUIRED_FIELDS]
    if missing:
        issues.append(PaperManifestIssue("missing_csv_header", f"missing CSV headers {missing}"))
    for field in extra:
        issues.append(
            PaperManifestIssue(
                "unsupported_csv_header",
                f"unsupported CSV header {_safe_manifest_label(field)!r}",
            )
        )
    if fieldnames != list(REQUIRED_FIELDS):
        issues.append(
            PaperManifestIssue(
                "csv_header_order",
                f"CSV headers must exactly match {list(REQUIRED_FIELDS)}",
            )
        )
    return issues


def _validate_paper_id(value: str, row_id: str) -> list[PaperManifestIssue]:
    if (
        not value
        or _has_unsafe_text(value)
        or redact_sensitive_text(value) != value
        or PAPER_ID_RE.fullmatch(value) is None
    ):
        return [
            PaperManifestIssue(
                "invalid_id",
                "id must be an arXiv id or lowercase foundational-paper slug",
                row_id,
            )
        ]
    return []


def _validate_paper_title(value: str, row_id: str) -> list[PaperManifestIssue]:
    if (
        not value.strip()
        or _has_unsafe_text(value)
        or redact_sensitive_text(value) != value
        or len(value) > MAX_TITLE_CHARS
    ):
        return [
            PaperManifestIssue(
                "invalid_title",
                f"title must be non-empty, display-safe, and at most {MAX_TITLE_CHARS} characters",
                row_id,
            )
        ]
    return []


def _validate_paper_url(value: str, row_id: str) -> list[PaperManifestIssue]:
    if _has_unsafe_text(value) or redact_sensitive_text(value) != value:
        return [PaperManifestIssue("invalid_url", "url must be share-safe HTTPS source URL", row_id)]
    parsed = urlparse(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.hostname.casefold() not in ALLOWED_PAPER_URL_HOSTS
        or parsed.username is not None
        or parsed.password is not None
    ):
        return [PaperManifestIssue("invalid_url", "url must use an allowed HTTPS paper source host", row_id)]
    return []


def _validate_paper_row_identity(
    row_id_value: str,
    url_value: str,
    file_value: str,
    row_id: str,
) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    if _validate_paper_id(row_id_value, row_id) or not _is_safe_paper_path(file_value):
        return issues
    parsed = urlparse(url_value)
    host = parsed.hostname.casefold() if parsed.hostname else ""
    file_stem = PurePosixPath(file_value).stem
    file_source_id = file_stem.split("__", 1)[0]
    if file_source_id != row_id_value:
        issues.append(
            PaperManifestIssue(
                "file_source_id_mismatch",
                "local PDF filename stem must start with the manifest id before any __ title suffix",
                row_id,
            )
        )
    if host in {"arxiv.org", "www.arxiv.org"}:
        arxiv_id = _arxiv_id_from_url_path(parsed.path)
        if arxiv_id is None:
            issues.append(
                PaperManifestIssue(
                    "missing_arxiv_url_id",
                    "arXiv source URL path must include an arXiv id",
                    row_id,
                )
            )
            return issues
        arxiv_base_id = arxiv_id.split("v", 1)[0]
        if arxiv_base_id != row_id_value:
            issues.append(
                PaperManifestIssue(
                    "arxiv_url_id_mismatch",
                    "arXiv source URL id must match the manifest id",
                    row_id,
                )
            )
    elif file_source_id != row_id_value:
        issues.append(
            PaperManifestIssue(
                "non_arxiv_source_identity_missing",
                "non-arXiv source rows must use the manifest id as the local filename source prefix",
                row_id,
            )
        )
    return issues


def _arxiv_id_from_url_path(path: str) -> str | None:
    parts = [part for part in PurePosixPath(path).parts if part not in {"/", ""}]
    if len(parts) < 2 or parts[0] not in {"abs", "pdf"}:
        return None
    candidate = parts[1]
    if candidate.endswith(".pdf"):
        candidate = candidate[:-4]
    if ARXIV_ID_RE.fullmatch(candidate) is None:
        return None
    return candidate


def _validate_download_message(value: str, row_id: str) -> list[PaperManifestIssue]:
    issues: list[PaperManifestIssue] = []
    if _has_unsafe_text(value):
        issues.append(PaperManifestIssue("invalid_message", "message must not contain control characters", row_id))
    if redact_sensitive_text(value) != value:
        issues.append(PaperManifestIssue("unsafe_message", "message must not contain secret-like text", row_id))
    if len(value) > MAX_DOWNLOAD_MESSAGE_CHARS:
        issues.append(
            PaperManifestIssue(
                "message_too_long",
                f"message must be at most {MAX_DOWNLOAD_MESSAGE_CHARS} characters",
                row_id,
            )
        )
    return issues


def _sanitize_download_message(value: Any) -> str:
    text = redact_sensitive_text(str(value))
    text = "".join(" " if _is_control_or_format(character) else character for character in text)
    if len(text) > MAX_DOWNLOAD_MESSAGE_CHARS:
        return text[: MAX_DOWNLOAD_MESSAGE_CHARS - 3] + "..."
    return text


def _safe_manifest_label(value: str) -> str:
    redacted = redact_sensitive_text(value)
    redacted = "".join("?" if _is_control_or_format(character) else character for character in redacted)
    if len(redacted) > 96:
        return redacted[:93] + "..."
    return redacted


def _has_unsafe_text(value: str) -> bool:
    return any(_is_control_or_format(character) for character in value)


def _is_control_or_format(character: str) -> bool:
    category = unicodedata.category(character)
    return category.startswith("C")


def _parse_csv_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise ValueError(f"invalid boolean {value!r}")


def _has_pdf_header(path: Path) -> bool:
    with path.open("rb") as handle:
        return handle.read(5) == b"%PDF-"


def _read_pdf_quietly(path: Path) -> PdfReader:
    pypdf_logger = logging.getLogger("pypdf")
    previous_level = pypdf_logger.level
    pypdf_logger.setLevel(logging.ERROR)
    try:
        with redirect_stderr(io.StringIO()):
            return PdfReader(path, strict=True)
    finally:
        pypdf_logger.setLevel(previous_level)


def _safe_pdf_parse_error(exc: BaseException) -> str:
    message = redact_sensitive_text(str(exc))
    if len(message) > 160:
        message = message[:157] + "..."
    return f"{exc.__class__.__name__}: {message}"


def _is_link_backed_path(path: Path) -> bool:
    if path.is_symlink():
        return True
    local_stat = path.lstat()
    file_attributes = getattr(local_stat, "st_file_attributes", 0)
    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(reparse_point and file_attributes & reparse_point)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(PDF_HASH_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _existing_rehydrate_match(row: dict[str, Any], target: Path, row_id: str) -> PaperRehydrateResult:
    file_value = str(row["file"])
    if not target.exists():
        return PaperRehydrateResult(row_id, file_value, "missing", None, None, "local PDF is missing")
    try:
        if _is_link_backed_path(target):
            return PaperRehydrateResult(
                row_id,
                file_value,
                "failed",
                None,
                None,
                "local PDF path is symlink or reparse-point backed; refusing to overwrite",
            )
    except OSError as exc:
        return PaperRehydrateResult(
            row_id,
            file_value,
            "failed",
            None,
            None,
            _sanitize_download_message(f"could not inspect local PDF link state: {exc}"),
        )
    try:
        local_stat = target.stat()
    except OSError as exc:
        return PaperRehydrateResult(
            row_id,
            file_value,
            "failed",
            None,
            None,
            _sanitize_download_message(f"could not inspect local PDF: {exc}"),
        )
    if not stat.S_ISREG(local_stat.st_mode):
        return PaperRehydrateResult(
            row_id,
            file_value,
            "failed",
            None,
            None,
            "local PDF path exists but is not a regular file; refusing to overwrite",
        )
    try:
        actual_sha = _sha256_file(target)
    except OSError as exc:
        return PaperRehydrateResult(
            row_id,
            file_value,
            "failed",
            local_stat.st_size,
            None,
            _sanitize_download_message(f"could not read local PDF: {exc}"),
        )
    if local_stat.st_size == row["bytes"] and actual_sha == row["sha256"]:
        return PaperRehydrateResult(
            row_id,
            file_value,
            "verified_existing",
            local_stat.st_size,
            actual_sha,
            "byte count and SHA-256 match manifest",
        )
    return PaperRehydrateResult(
        row_id,
        file_value,
        "stale",
        local_stat.st_size,
        actual_sha,
        "local byte count or SHA-256 differs from manifest",
    )


def _download_rehydrate_row(row: dict[str, Any], root: Path, timeout: float) -> PaperRehydrateResult:
    row_id = _safe_manifest_label(str(row["id"]))
    file_value = str(row["file"])
    target = root / file_value
    temp_path: Path | None = None
    bytes_seen = 0
    digest = hashlib.sha256()
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        request = Request(str(row["url"]), headers={"User-Agent": PAPER_DOWNLOAD_USER_AGENT})
        response = urlopen(request, timeout=timeout)
        try:
            status = getattr(response, "status", 200)
            if status >= 400:
                return PaperRehydrateResult(
                    row_id,
                    file_value,
                    "failed",
                    None,
                    None,
                    _sanitize_download_message(f"download returned HTTP {status}"),
                )
            with tempfile.NamedTemporaryFile(
                "wb",
                delete=False,
                dir=target.parent,
                prefix=f".{target.name}.",
                suffix=".download",
            ) as handle:
                temp_path = Path(handle.name)
                while chunk := response.read(PAPER_DOWNLOAD_CHUNK_SIZE):
                    bytes_seen += len(chunk)
                    digest.update(chunk)
                    handle.write(chunk)
        finally:
            close = getattr(response, "close", None)
            if callable(close):
                close()

        actual_sha = digest.hexdigest()
        if bytes_seen != row["bytes"]:
            return PaperRehydrateResult(
                row_id,
                file_value,
                "failed",
                bytes_seen,
                actual_sha,
                f"downloaded byte count {bytes_seen} does not match manifest {row['bytes']}",
            )
        if actual_sha != row["sha256"]:
            return PaperRehydrateResult(
                row_id,
                file_value,
                "failed",
                bytes_seen,
                actual_sha,
                "downloaded SHA-256 does not match manifest",
            )
        os.replace(temp_path, target)
        temp_path = None
        post_download_issues = _validate_local_pdf(row, target, row_id)
        if post_download_issues:
            return PaperRehydrateResult(
                row_id,
                file_value,
                "failed",
                bytes_seen,
                actual_sha,
                "; ".join(issue.code for issue in post_download_issues),
            )
        return PaperRehydrateResult(
            row_id,
            file_value,
            "downloaded",
            bytes_seen,
            actual_sha,
            "downloaded and verified against manifest",
        )
    except Exception as exc:
        return PaperRehydrateResult(
            row_id,
            file_value,
            "failed",
            bytes_seen or None,
            digest.hexdigest() if bytes_seen else None,
            _sanitize_download_message(f"download failed: {exc}"),
        )
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def _local_pdf_files(root: Path) -> set[str]:
    papers = root / "papers"
    if not papers.exists():
        return set()
    files: set[str] = set()
    for path in papers.glob("*.pdf"):
        try:
            is_file = path.is_file()
        except OSError:
            continue
        if is_file:
            files.add(path.relative_to(root).as_posix())
    return files


def _paper_file_label(row: dict[str, Any], path: Path) -> str:
    file_value = row.get("file")
    if isinstance(file_value, str):
        return file_value.replace("\\", "/")
    return str(path)


def _report_to_dict(report: PaperManifestReport) -> dict[str, Any]:
    return {
        "ok": report.ok,
        "row_count": report.row_count,
        "local_present_count": report.local_present_count,
        "local_missing_count": report.local_missing_count,
        "local_unique_file_count": report.local_unique_file_count,
        "availability": [asdict(item) for item in report.availability],
        "issues": [asdict(issue) for issue in report.issues],
    }


def _rehydrate_report_to_dict(report: PaperRehydrateReport) -> dict[str, Any]:
    return {
        "ok": report.ok,
        "row_count": report.row_count,
        "verified_existing_count": report.verified_existing_count,
        "downloaded_count": report.downloaded_count,
        "failed_count": report.failed_count,
        "results": [asdict(result) for result in report.results],
        "issues": [asdict(issue) for issue in report.issues],
    }


def _availability(
    row: dict[str, Any],
    file_value: str,
    local_status: str,
    git_tracked_files: set[str] | None,
) -> PaperAvailability:
    return PaperAvailability(
        row_id=_safe_manifest_label(str(row.get("id", ""))),
        file=file_value,
        download_ok=row.get("ok") is True,
        download_message=_sanitize_download_message(row.get("message", "")),
        local_status=local_status,
        git_tracked=None if git_tracked_files is None else file_value.replace("\\", "/") in git_tracked_files,
    )


def _is_allowed_tracked_paper_pdf(row: dict[str, Any], file_value: str) -> bool:
    row_id = _safe_manifest_label(str(row.get("id", "")))
    sha256 = row.get("sha256")
    if not isinstance(sha256, str):
        return False
    return (row_id, file_value.replace("\\", "/"), sha256) in ALLOWED_TRACKED_PAPER_PDFS


def _git_tracked_files(root: Path) -> set[str] | None:
    if not (root / ".git").exists():
        return None
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--", "papers/*.pdf"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return {line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()}


if __name__ == "__main__":
    raise SystemExit(main())
