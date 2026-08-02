from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_tex_prose_inventory_boundary import (
    ALPHAEVOLVE_TEX_PROSE_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_tex_prose_inventory_boundary_record,
    render_alphaevolve_tex_prose_inventory_boundary_summary,
    validate_alphaevolve_tex_prose_inventory_boundary,
)


def test_tex_prose_inventory_accepts_complete_sentence_disposition_scope():
    boundary = alphaevolve_tex_prose_inventory_boundary_record()

    validation = validate_alphaevolve_tex_prose_inventory_boundary(boundary)

    assert validation.ok is True
    assert boundary["schema"] == ALPHAEVOLVE_TEX_PROSE_INVENTORY_BOUNDARY_SCHEMA
    assert boundary["source_artifact"]["identity_ok"] is True
    assert boundary["prose_inventory_ready"] is True
    assert boundary["prose_disposition_ready"] is True
    assert boundary["whole_paper_semantic_exhaustiveness_claim_ready"] is False
    assert boundary["mathematical_correctness_claim_ready"] is False
    assert boundary["result_reproduction_claim_ready"] is False
    assert boundary["alphaevolve_parity_claim_ready"] is False
    assert validation.paragraph_count == 128
    assert validation.sentence_count == 402
    assert boundary["disposition_counts"] == {
        "existing_bounded_claim_mapping": 372,
        "reviewed_nonclaim": 30,
    }
    assert boundary["excluded_range_count"] == 37


def test_tex_prose_inventory_preserves_file_counts_and_resolved_dispositions():
    boundary = alphaevolve_tex_prose_inventory_boundary_record()

    assert boundary["paragraph_counts_by_file"] == {
        "ablations.tex": 7,
        "acknowledgement.tex": 6,
        "appendix.tex": 34,
        "discussion.tex": 5,
        "introduction.tex": 8,
        "main.tex": 1,
        "methods.tex": 24,
        "related_work.tex": 11,
        "results.tex": 32,
    }
    assert boundary["sentence_counts_by_file"] == {
        "ablations.tex": 24,
        "acknowledgement.tex": 7,
        "appendix.tex": 96,
        "discussion.tex": 14,
        "introduction.tex": 29,
        "main.tex": 8,
        "methods.tex": 61,
        "related_work.tex": 41,
        "results.tex": 122,
    }
    assert boundary["unmapped_sentence_count"] == 0
    assert boundary["unresolved_reference_count"] == 0
    assert all(
        record["claim_refs"] or record["nonclaim_disposition"]
        for record in boundary["sentence_records"]
    )
    assert all(
        ref["resolved"]
        for record in boundary["sentence_records"]
        for ref in record["claim_refs"]
    )


def test_tex_prose_inventory_maps_new_claims_and_disambiguates_repeated_anchors():
    boundary = alphaevolve_tex_prose_inventory_boundary_record()
    records = {
        (
            record["source_file"],
            record["source_line"],
            record["line_ordinal"],
        ): record
        for record in boundary["sentence_records"]
    }
    mapped_ids = {
        ref["claim_id"]
        for record in boundary["sentence_records"]
        for ref in record["claim_refs"]
    }

    assert {
        "abstract_complex_4x4_matrix_48_multiplications",
        "introduction_algorithm_search_outperforms_direct_solution_search",
        "introduction_complex_4x4_matrix_48_multiplications",
        "introduction_erdos_minimum_overlap_result",
        "introduction_seventy_five_percent_math_best_known",
        "task_metric_maximization_convention",
        "task_problem_specific_abstraction_choice",
        "task_symmetry_guided_abstraction_bias",
        "evaluation_order_hundred_compute_hours_per_candidate",
        "evaluation_sample_efficiency_enables_expensive_evaluation",
        "evaluation_multi_metric_single_target_uplift",
        "section3_1_tensor_decomposition_algorithm_representation",
        "section3_1_low_rank_decomposition_search_objective",
        "section3_1_standard_gradient_baseline_components",
        "section3_1_natural_language_near_integrality_prompt",
        "section3_1_most_table2_simple_initial_program",
        "section3_2_evolve_heuristics_not_direct_constructions",
        "section3_2_fast_objective_evaluations_common_in_math",
        "section3_3_1_continuous_average_point_7_percent_recovery",
        "section3_3_1_debuggability_advantage",
        "section3_3_1_ease_of_deployment_advantage",
        "section3_3_1_mission_critical_operational_qualities",
        "section3_3_1_post_deployment_confirms_simulator",
        "section3_3_1_predictability_advantage",
        "section3_3_2_average_twenty_three_percent_kernel_speedup",
        "section3_3_2_one_percent_gemini_training_reduction",
        "section3_3_2_team_research_engineering_velocity",
        "direct_verilog_fosters_trust",
        "direct_verilog_simplifies_adoption",
        "gemini_first_direct_tpu_arithmetic_contribution",
        "jax_output_postprocessing",
        "pre_postprocessing_speedup_15_percent",
    } <= mapped_ids
    assert {
        ref["claim_id"] for ref in records[("main.tex", 34, 0)]["claim_refs"]
    } == {
        "abstract_complex_4x4_matrix_48_multiplications",
        "abstract_first_strassen_improvement_56_years",
    }
    assert {
        ref["claim_id"]
        for ref in records[("introduction.tex", 48, 0)]["claim_refs"]
    } == {
        "introduction_complex_4x4_matrix_48_multiplications",
        "introduction_fourteen_matrix_sota_improvements",
    }
    assert {
        ref["claim_id"]
        for ref in records[("introduction.tex", 52, 0)]["claim_refs"]
    } == {
        "introduction_over_fifty_math_problems_best_known",
        "introduction_seventy_five_percent_math_best_known",
    }
    assert {
        ref["claim_id"]
        for ref in records[("introduction.tex", 53, 0)]["claim_refs"]
    } == {
        "introduction_erdos_minimum_overlap_result",
        "introduction_kissing_number_d11_improvement",
    }
    assert {
        ref["claim_id"] for ref in records[("methods.tex", 32, 0)]["claim_refs"]
    } == {
        "introduction_automatically_evaluable_problem_scope",
        "task_scalar_metric_mapping",
    }
    assert {
        ref["claim_id"] for ref in records[("methods.tex", 48, 0)]["claim_refs"]
    } == {
        "introduction_algorithm_discovery_instrumental_goal",
        "task_problem_specific_abstraction_choice",
    }
    assert {
        ref["claim_id"] for ref in records[("methods.tex", 118, 0)]["claim_refs"]
    } == {
        "evaluation_order_hundred_compute_hours_per_candidate",
        "evaluation_sample_efficiency_enables_expensive_evaluation",
    }
    assert {
        ref["claim_id"] for ref in records[("methods.tex", 107, 0)]["claim_refs"]
    } == {
        "evaluation_every_proposal",
        "evolution_database_resurfacing",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 45, 0)]["claim_refs"]
    } == {
        "prompt_explicit_context",
        "section3_1_sophisticated_algorithms_outperform_approaches",
        "section3_1_standard_gradient_baseline_components",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 46, 0)]["claim_refs"]
    } == {
        "evaluation_every_proposal",
        "section3_1_multi_seed_evaluation_cascade",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 47, 0)]["claim_refs"]
    } == {
        "section2_evolutionary_metric_improvement",
        "section3_1_best_rank_and_seed_hit_fraction",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 48, 0)]["claim_refs"]
    } == {
        "section3_1_integer_half_integer_rounding_exactness",
        "section3_1_natural_language_near_integrality_prompt",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 60, 0)]["claim_refs"]
    } == {
        "section3_1_most_table2_simple_initial_program",
        "section3_1_researcher_ideas_boost_performance",
        "section3_1_scientific_collaboration_possibility",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 78, 1)]["claim_refs"]
    } == {
        "section3_2_diverse_constructions_and_conjectures",
        "section3_2_evolve_heuristics_not_direct_constructions",
        "section3_2_less_expert_tailoring_than_bespoke",
        "section3_2_rapid_deployment",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 80, 1)]["claim_refs"]
    } == {
        "section3_2_fast_objective_evaluations_common_in_math",
        "section3_2_iterative_refinement_strategy",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 119, 4)]["claim_refs"]
    } == {
        "section3_3_1_continuous_average_point_7_percent_recovery",
        "section3_3_1_post_deployment_confirms_simulator",
        "section3_3_1_recovered_resources_otherwise_stranded",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 119, 5)]["claim_refs"]
    } == {
        "section3_3_1_chosen_over_deep_reinforcement_learning",
        "section3_3_1_code_solution_better_performance",
        "section3_3_1_debuggability_advantage",
        "section3_3_1_ease_of_deployment_advantage",
        "section3_3_1_interpretability_advantage",
        "section3_3_1_mission_critical_operational_qualities",
        "section3_3_1_predictability_advantage",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 161, 0)]["claim_refs"]
    } == {
        "section3_3_2_average_twenty_three_percent_kernel_speedup",
        "section3_3_2_expert_designed_heuristic_comparator",
        "section3_3_2_one_percent_gemini_training_reduction",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 161, 4)]["claim_refs"]
    } == {
        "section3_3_2_deployment_enhanced_training_efficiency",
        "section3_3_2_team_research_engineering_velocity",
        "section3_3_2_tiling_heuristic_deployed_production",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 170, 0)]["claim_refs"]
    } == {
        "alphaevolve_mediated_hardware_contribution",
        "gemini_first_direct_tpu_arithmetic_contribution",
        "integrated_into_upcoming_tpu",
        "path_for_future_hardware_contributions",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 170, 1)]["claim_refs"]
    } == {
        "changes_communicated_directly_in_verilog",
        "direct_verilog_fosters_trust",
        "direct_verilog_simplifies_adoption",
        "verilog_standard_hardware_engineering_language",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 177, 0)]["claim_refs"]
    } == {
        "flashattention_accelerator_kernel_in_stack",
        "higher_level_jax_wrapper",
        "jax_input_preparation",
        "jax_output_postprocessing",
        "pallas_flashattention_implementation",
    }
    assert {
        ref["claim_id"] for ref in records[("results.tex", 182, 2)]["claim_refs"]
    } == {
        "pre_postprocessing_improvements_found",
        "pre_postprocessing_speedup_15_percent",
    }
    assert {
        ref["claim_id"] for ref in records[("ablations.tex", 7, 2)]["claim_refs"]
    } == {
        "no_evolution_repeats_same_initial_program",
        "section4_component_efficacy_goal",
    }
    assert {
        ref["claim_id"] for ref in records[("ablations.tex", 8, 2)]["claim_refs"]
    } == {
        "no_context_removes_explicit_context",
        "section4_component_efficacy_goal",
    }
    assert [
        ref["claim_id"] for ref in records[("ablations.tex", 8, 3)]["claim_refs"]
    ] == ["no_context_variant_name"]
    assert {
        ref["claim_id"] for ref in records[("ablations.tex", 9, 3)]["claim_refs"]
    } == {
        "meta_prompt_disabled_for_tensor_task",
        "section4_component_efficacy_goal",
    }
    assert {
        ref["claim_id"] for ref in records[("ablations.tex", 10, 2)]["claim_refs"]
    } == {
        "full_file_ablation_tensor_context",
        "no_full_file_only_loss_function_evolved",
        "section4_component_efficacy_goal",
    }
    assert {
        ref["claim_id"] for ref in records[("ablations.tex", 11, 2)]["claim_refs"]
    } == {
        "section4_component_efficacy_goal",
        "small_base_only_alternative",
    }
    assert "already_highly_optimized_baseline" not in {
        ref["claim_id"] for ref in records[("results.tex", 168, 0)]["claim_refs"]
    }
    assert "b8_3d_prior_sqrt_4_168" not in {
        ref["claim_id"] for ref in records[("appendix.tex", 209, 0)]["claim_refs"]
    }
    assert "b8_2d_prior_sqrt_12_890" not in {
        ref["claim_id"] for ref in records[("appendix.tex", 212, 0)]["claim_refs"]
    }


def test_tex_prose_inventory_rejects_record_count_and_overclaim_drift():
    boundary = deepcopy(alphaevolve_tex_prose_inventory_boundary_record())
    boundary["sentence_records"][0]["rendered_text"] = "drift"
    boundary["sentence_count"] = 401
    boundary["whole_paper_semantic_exhaustiveness_claim_ready"] = True
    boundary["alphaevolve_parity_claim_ready"] = True

    validation = validate_alphaevolve_tex_prose_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_sentence_records" in codes
    assert "invalid_sentence_count" in codes
    assert "whole_paper_semantic_exhaustiveness_claim_ready_overclaim" in codes
    assert "alphaevolve_parity_claim_ready_overclaim" in codes


def test_tex_prose_inventory_rejects_missing_pinned_source(tmp_path):
    boundary = alphaevolve_tex_prose_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_tex_prose_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["prose_inventory_ready"] is False
    assert boundary["prose_disposition_ready"] is False
    assert "source_archive_identity_mismatch" in codes
    assert "source_inventory_incomplete" in codes


def test_render_tex_prose_inventory_summary_reports_shape():
    summary = render_alphaevolve_tex_prose_inventory_boundary_summary(
        alphaevolve_tex_prose_inventory_boundary_record()
    )

    assert "AlphaEvolve TeX prose inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| paragraph_count | 128 |" in summary
    assert "| sentence_count | 402 |" in summary
    assert "| unmapped_sentence_count | 0 |" in summary
    assert "| unresolved_reference_count | 0 |" in summary
