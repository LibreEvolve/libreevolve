from copy import deepcopy

from libreevolve.problems.benchmarks.alphaevolve_tex_proposition_inventory_boundary import (
    ALPHAEVOLVE_TEX_PROPOSITION_INVENTORY_BOUNDARY_SCHEMA,
    alphaevolve_tex_proposition_inventory_boundary_record,
    render_alphaevolve_tex_proposition_inventory_boundary_summary,
    validate_alphaevolve_tex_proposition_inventory_boundary,
)


def test_tex_proposition_inventory_accepts_section3_3_3_hardware_scope():
    boundary = alphaevolve_tex_proposition_inventory_boundary_record()

    validation = validate_alphaevolve_tex_proposition_inventory_boundary(boundary)

    assert validation.ok is True
    assert (
        boundary["schema"]
        == ALPHAEVOLVE_TEX_PROPOSITION_INVENTORY_BOUNDARY_SCHEMA
    )
    assert boundary["source_prose_ready"] is True
    assert boundary["proposition_inventory_ready"] is True
    assert boundary["review_scope_complete"] is True
    assert boundary["whole_paper_semantic_exhaustiveness_claim_ready"] is False
    assert boundary["independent_semantic_review_ready"] is False
    assert validation.reviewed_sentence_count == 206
    assert validation.proposition_count == 673
    assert validation.remaining_sentence_count == 196
    assert validation.unmapped_proposition_count == 0
    assert validation.unresolved_reference_count == 0
    assert boundary["reviewed_sentence_fraction"] == 206 / 402
    assert boundary["reviewed_source_files"] == [
        "introduction.tex",
        "main.tex",
        "methods.tex",
        "results.tex",
    ]
    assert boundary["disposition_counts"] == {
        "author_interpretation": 11,
        "author_outlook": 2,
        "existing_bounded_claim_mapping": 619,
        "source_context_only": 41,
    }
    assert boundary["claim_reference_count"] == 643
    assert boundary["unique_claim_reference_count"] == 286
    assert boundary["implementation_relevant_proposition_count"] == 609


def test_tex_proposition_inventory_resolves_every_reviewed_record():
    boundary = alphaevolve_tex_proposition_inventory_boundary_record()

    assert len(boundary["reviewed_sentence_records"]) == 206
    assert len(boundary["proposition_records"]) == 673
    assert all(
        record["review_status"]
        == "manual_static_semantic_decomposition_complete"
        for record in boundary["reviewed_sentence_records"]
    )
    assert all(
        ref["resolved"]
        for record in boundary["proposition_records"]
        for ref in record["claim_refs"]
    )
    assert all(
        record["source_quote_start"] >= 0
        and record["source_quote_end"] > record["source_quote_start"]
        for record in boundary["proposition_records"]
    )


def test_tex_proposition_inventory_records_new_and_repaired_claims():
    boundary = alphaevolve_tex_proposition_inventory_boundary_record()
    mapped_ids = {
        ref["claim_id"]
        for record in boundary["proposition_records"]
        for ref in record["claim_refs"]
    }

    assert boundary["new_bounded_claim_ids"] == [
        "introduction_algorithm_search_outperforms_direct_solution_search",
        "evaluation_sample_efficiency_enables_expensive_evaluation",
    ]
    assert set(boundary["repaired_sentence_claim_ids"]) == {
        "abstract_complex_4x4_matrix_48_multiplications",
        "evolution_database_resurfacing",
        "introduction_algorithm_discovery_instrumental_goal",
        "introduction_automatically_evaluable_problem_scope",
        "introduction_complex_4x4_matrix_48_multiplications",
        "introduction_erdos_minimum_overlap_result",
        "introduction_seventy_five_percent_math_best_known",
        "evaluation_every_proposal",
        "prompt_explicit_context",
        "section2_evolutionary_metric_improvement",
        "section3_1_most_table2_simple_initial_program",
        "section3_1_natural_language_near_integrality_prompt",
        "section3_1_standard_gradient_baseline_components",
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
        "task_problem_specific_abstraction_choice",
    }
    assert set(boundary["new_bounded_claim_ids"]) <= mapped_ids
    assert set(boundary["repaired_sentence_claim_ids"]) <= mapped_ids
    assert {
        "section3_2_ai_human_math_partnership_potential",
        "section3_2_autocorrelation_bounds_improved",
        "section3_2_erdos_new_upper_bound",
        "section3_2_external_advice_on_input_formulation",
        "section3_2_heilbronn_small_triangle_avoidance",
        "section3_2_javier_gomez_serrano_and_terence_tao",
        "section3_2_kissing_number_d11_593_vs_592",
        "section3_2_most_discoveries_externally_suggested",
        "section3_2_n_point_max_min_distance_packing",
        "section3_2_new_constructions_in_companion_colab",
        "section3_2_polygon_in_polygon_packing",
        "section3_2_uncertainty_fourier_upper_bound",
        "section3_2_upcoming_math_paper_follow_on",
    } <= mapped_ids
    assert {
        "section3_3_1_assign_jobs_from_requirements_and_capacity",
        "section3_3_1_borg_uses_highest_priority_among_other_objectives",
        "section3_3_1_chosen_over_deep_reinforcement_learning",
        "section3_3_1_code_solution_better_performance",
        "section3_3_1_continuous_average_point_7_percent_recovery",
        "section3_3_1_debuggability_advantage",
        "section3_3_1_debuggability_scale_and_bin_packing_challenge",
        "section3_3_1_early_alphaevolve_version",
        "section3_3_1_ease_of_deployment_advantage",
        "section3_3_1_effectively_correct_by_construction",
        "section3_3_1_entire_fleet_rollout",
        "section3_3_1_evolved_from_production_incumbent",
        "section3_3_1_google_scale_borg_scheduling_problem",
        "section3_3_1_growth_without_proportional_resource_increase",
        "section3_3_1_heuristic_outputs_machine_priority",
        "section3_3_1_heuristic_required_and_free_inputs",
        "section3_3_1_historical_fleet_snapshot_simulator_feedback",
        "section3_3_1_inefficient_assignments_strand_resources",
        "section3_3_1_interpretability_advantage",
        "section3_3_1_jobs_items_resource_demands",
        "section3_3_1_machines_bins_cpu_memory_capacity",
        "section3_3_1_mission_critical_operational_qualities",
        "section3_3_1_more_jobs_same_compute_footprint",
        "section3_3_1_one_resource_exhausted_other_resource_free",
        "section3_3_1_online_two_variable_vector_bin_packing",
        "section3_3_1_outperforms_production_heuristic",
        "section3_3_1_post_deployment_confirms_simulator",
        "section3_3_1_predictability_advantage",
        "section3_3_1_rank_only_borg_feasible_machines",
        "section3_3_1_recovered_resources_otherwise_stranded",
        "section3_3_1_simple_effective_heuristic_discovery",
        "section3_3_1_unseen_recent_workload_capacity_generalization",
        "section3_3_mission_critical_infrastructure_real_world_impact",
    } <= mapped_ids
    assert {
        "section3_3_2_gemini_training_compute_demand",
        "section3_3_2_gemini_built_on_jax",
        "section3_3_2_pallas_extends_jax",
        "section3_3_2_custom_specialized_kernel_programs",
        "section3_3_2_optimal_accelerator_execution",
        "section3_3_2_pallas_kernel_training_importance",
        "section3_3_2_matmul_tiling_is_critical_optimization",
        "section3_3_2_tiling_divides_large_matmul",
        "section3_3_2_balance_compute_and_data_movement",
        "section3_3_2_tiling_accelerates_overall_computation",
        "section3_3_2_search_based_autotuning_baseline",
        "section3_3_2_manual_heuristic_baseline",
        "section3_3_2_near_optimal_configs_varied_shapes",
        "section3_3_2_autotuning_interrupts_workflow",
        "section3_3_2_retune_every_shape_change",
        "section3_3_2_manual_heuristic_bottleneck",
        "section3_3_2_deep_kernel_functionality_expertise",
        "section3_3_2_deep_hardware_expertise",
        "section3_3_2_high_performance_arbitrary_shapes",
        "section3_3_2_expedite_emerging_hardware_kernels",
        "section3_3_2_simplify_model_developer_utilization",
        "section3_3_2_facilitate_heuristic_generation",
        "section3_3_2_optimize_tiling_heuristics",
        "section3_3_2_gemini_training_matmul_kernel",
        "section3_3_2_minimize_actual_kernel_runtime",
        "section3_3_2_iterative_tiling_refinement",
        "section3_3_2_candidate_code_proposals",
        "section3_3_2_runtime_across_various_shapes",
        "section3_3_2_real_tpu_accelerator_measurement",
        "section3_3_2_correctness_by_construction",
        "section3_3_2_tiling_strategy_only_candidate_scope",
        "section3_3_2_underlying_math_unchanged",
        "section3_3_2_automatic_realistic_shape_collection",
        "section3_3_2_shape_corpus_from_kernel_users",
        "section3_3_2_half_training_shape_split",
        "section3_3_2_training_shapes_are_optimization_targets",
        "section3_3_2_half_evaluation_shape_split",
        "section3_3_2_evaluation_tests_general_applicability",
        "section3_3_2_average_twenty_three_percent_kernel_speedup",
        "section3_3_2_expert_designed_heuristic_comparator",
        "section3_3_2_one_percent_gemini_training_reduction",
        "section3_3_2_optimization_months_to_days",
        "section3_3_2_dedicated_effort_to_automated_experimentation",
        "section3_3_2_faster_optimized_kernel_deployment",
        "section3_3_2_engineers_focus_higher_level_work",
        "section3_3_2_path_to_automated_manual_tuning",
        "section3_3_2_improved_gemini_kernel_ergonomics",
        "section3_3_2_tiling_heuristic_deployed_production",
        "section3_3_2_deployment_enhanced_training_efficiency",
        "section3_3_2_team_research_engineering_velocity",
        "section3_3_2_gemini_optimizes_own_training",
    } <= mapped_ids
    assert {
        "specialized_hardware_tpu_example",
        "specialized_hardware_resource_efficiency_at_scale",
        "chip_design_complexity",
        "chip_design_often_spans_years",
        "rtl_optimization_critical_step",
        "rtl_manual_hardware_description_rewriting",
        "rtl_power_metric",
        "rtl_performance_metric",
        "rtl_area_metric",
        "rtl_manual_iteration_can_take_months",
        "rtl_requires_highly_skilled_engineers",
        "already_highly_optimized_verilog_target",
        "key_tpu_arithmetic_circuit_target",
        "matrix_multiplication_unit_context",
        "reduce_area_objective",
        "reduce_power_objective",
        "preserve_core_functionality_objective",
        "robust_verification_requirement",
        "verification_confirms_functional_correctness",
        "simple_code_rewrite_discovered",
        "unnecessary_bits_removed",
        "tpu_designer_correctness_validation",
        "downstream_synthesis_independent_rediscovery",
        "refine_source_rtl_capability",
        "early_design_flow_optimization_value",
        "integrated_into_upcoming_tpu",
        "gemini_first_direct_tpu_arithmetic_contribution",
        "alphaevolve_mediated_hardware_contribution",
        "path_for_future_hardware_contributions",
        "changes_communicated_directly_in_verilog",
        "verilog_standard_hardware_engineering_language",
        "direct_verilog_fosters_trust",
        "direct_verilog_simplifies_adoption",
        "llm_code_evolution_assists_hardware_design",
        "potential_time_to_market_reduction",
    } <= mapped_ids


def test_tex_proposition_inventory_rejects_record_and_overclaim_drift():
    boundary = deepcopy(alphaevolve_tex_proposition_inventory_boundary_record())
    boundary["proposition_records"][0]["statement"] = "drift"
    boundary["proposition_count"] = 92
    boundary["reviewed_source_files"] = []
    boundary["parse_errors"] = ["fabricated_error"]
    boundary["whole_paper_semantic_exhaustiveness_claim_ready"] = True
    boundary["independent_semantic_review_ready"] = True
    boundary["alphaevolve_parity_claim_ready"] = True

    validation = validate_alphaevolve_tex_proposition_inventory_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_proposition_records" in codes
    assert "invalid_proposition_count" in codes
    assert "invalid_reviewed_source_files" in codes
    assert "invalid_parse_errors" in codes
    assert "whole_paper_semantic_exhaustiveness_claim_ready_overclaim" in codes
    assert "independent_semantic_review_ready_overclaim" in codes
    assert "alphaevolve_parity_claim_ready_overclaim" in codes


def test_tex_proposition_inventory_rejects_missing_pinned_source(tmp_path):
    boundary = alphaevolve_tex_proposition_inventory_boundary_record(tmp_path)

    validation = validate_alphaevolve_tex_proposition_inventory_boundary(
        boundary,
        root=tmp_path,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert boundary["source_prose_ready"] is False
    assert boundary["proposition_inventory_ready"] is False
    assert "source_prose_incomplete" in codes
    assert "proposition_inventory_incomplete" in codes


def test_render_tex_proposition_inventory_summary_reports_shape():
    summary = render_alphaevolve_tex_proposition_inventory_boundary_summary(
        alphaevolve_tex_proposition_inventory_boundary_record()
    )

    assert "AlphaEvolve TeX proposition inventory boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| reviewed_sentence_count | 206 |" in summary
    assert "| proposition_count | 673 |" in summary
    assert "| remaining_sentence_count | 196 |" in summary
    assert "| validation_status | ok |" in summary
