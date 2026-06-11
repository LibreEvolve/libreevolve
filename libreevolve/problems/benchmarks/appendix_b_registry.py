from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REGISTRY_PATH = Path(__file__).with_name("alphaevolve_appendix_b.json")
REGISTRY_SCHEMA = "libreevolve.alphaevolve_appendix_b_registry.v1"
EXPECTED_FAMILY_IDS = (
    "autocorrelation_bounds_k3",
    "autocorrelation_bounds_k4",
    "autocorrelation_bounds_k5",
    "uncertainty_inequality",
    "erdos_minimum_overlap",
    "sums_differences_finite_sets",
    "regular_hexagon_packing",
    "max_min_distance_point_sets",
    "heilbronn_triangle",
    "heilbronn_convex_region",
    "kissing_number_d11",
    "circle_packing_unit_square",
    "circle_packing_perimeter4_rectangle",
)
EXPECTED_AUTOCORRELATION_LABELS = {
    "autocorrelation_bounds_k3": {
        "source_section_id": "B.1",
        "paper_heading": "First autocorrelation inequality",
        "constant_id": "C1",
        "display_label": "B.1. First autocorrelation inequality (C1)",
        "internal_label_policy": "internal_id_only_not_paper_label",
    },
    "autocorrelation_bounds_k4": {
        "source_section_id": "B.2",
        "paper_heading": "Second autocorrelation inequality",
        "constant_id": "C2",
        "display_label": "B.2. Second autocorrelation inequality (C2)",
        "internal_label_policy": "internal_id_only_not_paper_label",
    },
    "autocorrelation_bounds_k5": {
        "source_section_id": "B.3",
        "paper_heading": "Third autocorrelation inequality",
        "constant_id": "C3",
        "display_label": "B.3. Third autocorrelation inequality (C3)",
        "internal_label_policy": "internal_id_only_not_paper_label",
    },
}
EXPECTED_AUTOCORRELATION_STEP_EVIDENCE = {
    "autocorrelation_bounds_k3": {
        "source_section_id": "B.1",
        "constant_id": "C1",
        "domain": "[-1/4, 1/4]",
        "interval_count": 600,
        "interval_spacing": "equally_spaced",
        "function_sign_policy": "non_negative",
        "bound_direction": "upper_bound",
        "previous_bound": 1.5098,
        "previous_bound_source": "[70]",
        "reported_bound": 1.5053,
        "reported_bound_relation": "C1 <= 1.5053",
        "construction_payload_status": "not_recorded_locally",
    },
    "autocorrelation_bounds_k4": {
        "source_section_id": "B.2",
        "constant_id": "C2",
        "domain": "[-1/4, 1/4]",
        "interval_count": 50,
        "interval_spacing": "equally_spaced",
        "function_sign_policy": "non_negative",
        "bound_direction": "lower_bound",
        "previous_bound": 0.88922,
        "previous_bound_source": "[70]",
        "reported_bound": 0.8962,
        "reported_bound_relation": "0.8962 <= C2",
        "construction_payload_status": "not_recorded_locally",
    },
    "autocorrelation_bounds_k5": {
        "source_section_id": "B.3",
        "constant_id": "C3",
        "domain": "[-1/4, 1/4]",
        "interval_count": 400,
        "interval_spacing": "equally_spaced",
        "function_sign_policy": "signed_real",
        "bound_direction": "upper_bound",
        "previous_bound": 1.45810,
        "previous_bound_source": "[104, page 75]",
        "reported_bound": 1.4557,
        "reported_bound_relation": "C3 <= 1.4557",
        "construction_payload_status": "not_recorded_locally",
    },
}
EXPECTED_B8_METRIC_CONVENTIONS = (
    {
        "result_id": "b8_16_points_2d",
        "source_section_id": "B.8",
        "source_figure": "Figure 12 left",
        "point_count": 16,
        "dimension": 2,
        "metric_name": "maximum_distance_over_minimum_distance",
        "reported_value_convention": "squared_max_min_ratio",
        "raw_reported_value": 12.889266112,
        "derived_ratio_transform": "sqrt(raw_reported_value)",
        "derived_ratio": 3.590162407468,
        "prior_best_value": 12.890,
        "prior_best_convention": "squared_max_min_ratio",
        "prior_best_source": "[29]",
        "comparison_unit_policy": "compare_squared_values_before_square_root_display",
        "coordinate_artifact_status": "not_recorded_locally",
    },
    {
        "result_id": "b8_14_points_3d",
        "source_section_id": "B.8",
        "source_figure": "Figure 12 right",
        "point_count": 14,
        "dimension": 3,
        "metric_name": "maximum_distance_over_minimum_distance",
        "reported_value_convention": "squared_max_min_ratio",
        "raw_reported_value": 4.165849767,
        "derived_ratio_transform": "sqrt(raw_reported_value)",
        "derived_ratio": 2.041041343775,
        "prior_best_value": 4.168,
        "prior_best_convention": "squared_max_min_ratio",
        "prior_best_source": "[29]",
        "comparison_unit_policy": "compare_squared_values_before_square_root_display",
        "coordinate_artifact_status": "not_recorded_locally",
    },
)
EXPECTED_B8_WITNESS_REQUIRED_FIELDS = (
    "result_id",
    "point_count",
    "dimension",
    "coordinate_artifact_path",
    "coordinate_artifact_sha256",
    "coordinate_payload_schema",
    "distance_certificate_path",
    "distance_certificate_sha256",
    "minimum_pairwise_distance",
    "maximum_pairwise_distance",
    "recomputed_squared_ratio",
    "figure_panel_id",
)
EXPECTED_B8_WITNESS_IDS = ("b8_16_points_2d", "b8_14_points_3d")
EXPECTED_B5_SOURCE_FORMULATION = {
    "source_section_id": "B.5",
    "constant_id": "C5",
    "source_problem_name": "Erdos minimum overlap problem",
    "function_pair_domain": "[-1, 1]",
    "function_pair_range": "[0, 1]",
    "function_pair_non_negative": True,
    "complement_constraint": "f + g = 1 on [-1, 1]",
    "integral_constraint": "integral f = 1",
    "zero_extension": "extend f and g by zero outside [-1, 1]",
    "objective_domain": "x in [-2, 2]",
    "objective_expression": "sup_x integral_{-1}^1 f(t) g(x + t) dt",
    "bound_direction": "lower_bound_for_all_admissible_f_g",
    "known_lower_bound": 0.379005,
    "known_upper_bound": 0.380927,
    "lower_bound_source": "[107]",
    "equivalence_source": "[40]",
    "reduced_step_function_domain": "[0, 2]",
    "reduced_step_function_range": "[0, 1]",
    "reduced_integral_constraint": "integral_0^2 h(x) dx = 1",
    "reduced_objective_expression": "max_k integral h(x) * (1 - h(x + k)) dx",
    "reduced_objective_direction": "infimum",
    "mapping_to_step_function_evidence": "figure10_minimum_overlap_step_function",
    "construction_payload_status": "not_recorded_locally",
}
EXPECTED_B5_STEP_FUNCTION_REQUIRED_FIELDS = (
    "result_id",
    "step_function_artifact_path",
    "step_function_artifact_sha256",
    "step_function_payload_schema",
    "integral_normalization_certificate_path",
    "integral_normalization_certificate_sha256",
    "shift_objective_certificate_path",
    "shift_objective_certificate_sha256",
    "recomputed_upper_bound",
    "figure_panel_artifact_path",
    "figure_panel_artifact_sha256",
)
EXPECTED_B5_STEP_FUNCTION_BOUNDARY = {
    "status": "not_recorded_locally",
    "result_id": "figure10_minimum_overlap_step_function",
    "source_section_id": "B.5",
    "source_figure": "Figure 10",
    "constant_id": "C5",
    "step_function_domain": "[0, 2]",
    "step_function_range": "[0, 1]",
    "integral_constraint": "integral_0^2 h(x) dx = 1",
    "objective_expression": "max_k integral h(x) * (1 - h(x + k)) dx",
    "objective_direction": "minimize",
    "prior_lower_bound": 0.379005,
    "prior_upper_bound": 0.380927,
    "prior_lower_bound_source": "[107]",
    "prior_upper_bound_source": "[40]",
    "reported_upper_bound": 0.380924,
    "reported_bound_relation": "C5 <= 0.380924",
    "required_payload_fields": list(EXPECTED_B5_STEP_FUNCTION_REQUIRED_FIELDS),
    "claim_boundary": "The registry records the paper's B.5 source/result summary but does not claim a local Figure 10 step-function payload, integral certificate, shift-objective certificate, or recomputed upper bound.",
}
EXPECTED_B6_THEOREM_CONDITION = {
    "source_section_id": "B.6",
    "constant_id": "C6",
    "source_problem_name": "Sums and differences of finite sets",
    "set_pair_symbols": ["A", "B"],
    "set_pair_type": "arbitrarily_large_finite_integer_sets",
    "sumset_definition": "A + B = {a + b : a in A, b in B}",
    "difference_set_definition": "A - B = {a - b : a in A, b in B}",
    "small_sumset_condition": "|A + B| << |A|",
    "large_difference_condition": "|A - B| >> |A + B|^C6",
    "ll_notation": "X << Y means X <= C Y for a constant C independent of A and B for sufficiently large sets",
    "gg_notation": "X >> Y means X >= C' Y for a positive constant C' independent of A and B for sufficiently large sets",
    "known_lower_bound": 1.14465,
    "known_upper_bound": 1.333333333333,
    "known_upper_bound_fraction": "4/3",
    "upper_bound_source": "[39, Corollary 3]",
    "lower_bound_source": "[39, Theorem 1]",
    "finite_set_theorem_source": "[39, Theorem 1]",
    "finite_set_theorem_id": "b6_gyarmati_finite_set_theorem",
    "witness_set_symbol": "U",
    "witness_set_type": "finite_set_of_non_negative_integers",
    "witness_must_contain_zero": True,
    "admissibility_condition": "|U - U| <= 2 max(U) + 1",
    "lower_bound_formula": "C6 >= 1 + log(|U - U| / |U + U|) / log(2 max(U) + 1)",
}
EXPECTED_B6_WITNESS_REQUIRED_FIELDS = (
    "result_id",
    "witness_label",
    "set_size",
    "integer_set_artifact_path",
    "integer_set_artifact_sha256",
    "finite_set_payload_schema",
    "contains_zero_certificate_path",
    "non_negative_certificate_path",
    "admissibility_certificate_path",
    "admissibility_certificate_sha256",
    "sumset_cardinality",
    "difference_set_cardinality",
    "max_element",
    "recomputed_lower_bound",
    "reported_bound_relation",
)
EXPECTED_B6_WITNESS_ROWS = (
    {
        "result_id": "b6_u1_size_2003",
        "witness_label": "U1",
        "set_size": 2003,
        "reported_lower_bound": 1.1479,
        "reported_bound_relation": "1.1479 <= C6",
    },
    {
        "result_id": "b6_u2_size_54265",
        "witness_label": "U2",
        "set_size": 54265,
        "reported_lower_bound": 1.1584,
        "reported_bound_relation": "1.1584 <= C6",
    },
)
EXPECTED_B6_WITNESS_IDS = tuple(row["result_id"] for row in EXPECTED_B6_WITNESS_ROWS)
EXPECTED_B7_PACKING_REQUIRED_FIELDS = (
    "result_id",
    "hexagon_count",
    "inner_side_length",
    "outer_side_length",
    "placement_artifact_path",
    "placement_artifact_sha256",
    "placement_payload_schema",
    "containment_certificate_path",
    "containment_certificate_sha256",
    "non_overlap_certificate_path",
    "non_overlap_certificate_sha256",
    "recomputed_outer_side_length",
    "figure_panel_id",
)
EXPECTED_B7_PACKING_SUMMARY = {
    "status": "not_recorded_locally",
    "source_section_id": "B.7",
    "source_problem_name": "Packing unit regular hexagons inside a regular hexagon",
    "inner_shape": "regular_hexagon",
    "inner_side_length": 1.0,
    "outer_shape": "regular_hexagon",
    "objective": "minimize_outer_regular_hexagon_side_length",
    "source_figure": "Figure 11",
    "prior_best_source": "[29]",
    "required_witness_fields": list(EXPECTED_B7_PACKING_REQUIRED_FIELDS),
}
EXPECTED_B7_PACKING_ROWS = (
    {
        "result_id": "b7_11_unit_hexagons",
        "hexagon_count": 11,
        "source_figure_panel": "Figure 11 left",
        "prior_outer_side_length": 3.943,
        "reported_outer_side_length": 3.931,
        "reported_improvement_direction": "smaller_outer_side_length",
    },
    {
        "result_id": "b7_12_unit_hexagons",
        "hexagon_count": 12,
        "source_figure_panel": "Figure 11 right",
        "prior_outer_side_length": 4.0,
        "reported_outer_side_length": 3.942,
        "reported_improvement_direction": "smaller_outer_side_length",
    },
)
EXPECTED_B7_PACKING_IDS = tuple(row["result_id"] for row in EXPECTED_B7_PACKING_ROWS)
EXPECTED_B9_HEILBRONN_REQUIRED_FIELDS = (
    "result_id",
    "point_count",
    "domain_type",
    "domain_area",
    "point_coordinate_artifact_path",
    "point_coordinate_artifact_sha256",
    "domain_artifact_path",
    "domain_artifact_sha256",
    "domain_membership_certificate_path",
    "domain_membership_certificate_sha256",
    "unit_area_certificate_path",
    "unit_area_certificate_sha256",
    "all_triples_area_certificate_path",
    "all_triples_area_certificate_sha256",
    "recomputed_minimum_area",
    "figure_panel_id",
)
EXPECTED_B10_HEILBRONN_REQUIRED_FIELDS = (
    "result_id",
    "point_count",
    "domain_type",
    "domain_area",
    "point_coordinate_artifact_path",
    "point_coordinate_artifact_sha256",
    "domain_artifact_path",
    "domain_artifact_sha256",
    "domain_membership_certificate_path",
    "domain_membership_certificate_sha256",
    "convexity_certificate_path",
    "convexity_certificate_sha256",
    "unit_area_certificate_path",
    "unit_area_certificate_sha256",
    "all_triples_area_certificate_path",
    "all_triples_area_certificate_sha256",
    "recomputed_minimum_area",
    "figure_panel_id",
)
EXPECTED_HEILBRONN_SUMMARIES = {
    "heilbronn_triangle": {
        "status": "not_recorded_locally",
        "source_section_id": "B.9",
        "source_problem_name": "The Heilbronn problem for triangles",
        "domain_type": "triangle",
        "domain_area": 1.0,
        "objective": "maximize_minimum_area_of_triangles_formed_by_points",
        "source_figure": "Figure 13",
        "required_witness_fields": list(EXPECTED_B9_HEILBRONN_REQUIRED_FIELDS),
    },
    "heilbronn_convex_region": {
        "status": "not_recorded_locally",
        "source_section_id": "B.10",
        "source_problem_name": "The Heilbronn problem for convex regions",
        "domain_type": "convex_region",
        "domain_area": 1.0,
        "objective": "maximize_minimum_area_of_triangles_formed_by_points",
        "source_figure": "Figure 13",
        "required_witness_fields": list(EXPECTED_B10_HEILBRONN_REQUIRED_FIELDS),
    },
}
EXPECTED_HEILBRONN_ROWS = {
    "heilbronn_triangle": (
        {
            "result_id": "b9_triangle_n11",
            "point_count": 11,
            "source_figure_panel": "Figure 13 left",
            "prior_minimum_area": 0.036,
            "reported_minimum_area": 0.0365,
            "reported_value_relation": "minimum_area > 0.0365",
            "comparison_policy": "strictly_greater_than_reported_threshold",
            "prior_best_source": "[29]",
        },
    ),
    "heilbronn_convex_region": (
        {
            "result_id": "b10_convex_region_n13",
            "point_count": 13,
            "source_figure_panel": "Figure 13 middle",
            "prior_minimum_area": 0.0306,
            "reported_minimum_area": 0.0309,
            "reported_value_relation": "minimum_area >= 0.0309",
            "comparison_policy": "at_least_reported_value",
            "prior_best_source": "[29]",
        },
        {
            "result_id": "b10_convex_region_n14",
            "point_count": 14,
            "source_figure_panel": "Figure 13 right",
            "prior_minimum_area": 0.0277,
            "reported_minimum_area": 0.0278,
            "reported_value_relation": "minimum_area >= 0.0278",
            "comparison_policy": "at_least_reported_value",
            "prior_best_source": "[29]",
        },
    ),
}
EXPECTED_HEILBRONN_IDS = {
    family_id: tuple(row["result_id"] for row in rows)
    for family_id, rows in EXPECTED_HEILBRONN_ROWS.items()
}
EXPECTED_B11_KISSING_REQUIRED_FIELDS = (
    "result_id",
    "dimension",
    "vector_count",
    "vector_artifact_path",
    "vector_artifact_sha256",
    "vector_payload_schema",
    "integral_coordinate_certificate_path",
    "integral_coordinate_certificate_sha256",
    "nonzero_certificate_path",
    "nonzero_certificate_sha256",
    "max_norm_certificate_path",
    "max_norm_certificate_sha256",
    "min_pairwise_distance_certificate_path",
    "min_pairwise_distance_certificate_sha256",
    "lemma_applicability_certificate_path",
    "lemma_applicability_certificate_sha256",
    "transformed_center_certificate_path",
    "transformed_center_certificate_sha256",
    "recomputed_lower_bound",
)
EXPECTED_B11_KISSING_SUMMARY = {
    "status": "not_recorded_locally",
    "source_section_id": "B.11",
    "source_problem_name": "Kissing number in dimension 11",
    "dimension": 11,
    "prior_lower_bound": 592,
    "prior_lower_bound_source": "[31]",
    "reported_lower_bound": 593,
    "reported_bound_relation": "kissing_number_11 >= 593",
    "witness_vector_count": 593,
    "witness_vector_dimension": 11,
    "witness_coordinate_domain": "integral_coordinates",
    "witness_nonzero_condition": "0 not in C",
    "witness_norm_distance_condition": "max_norm_smaller_than_minimum_pairwise_distance",
    "lemma_id": "B.11 Lemma 1",
    "lemma_input_condition": "C subset R^d, 0 not in C, min_pairwise_distance >= max_norm",
    "lemma_transformation": "unit_sphere_centers = {2 x / ||x|| : x in C}",
    "lemma_output": "valid_kissing_configuration_in_dimension_d",
    "required_witness_fields": list(EXPECTED_B11_KISSING_REQUIRED_FIELDS),
}
EXPECTED_B11_KISSING_ROWS = (
    {
        "result_id": "b11_kissing_d11_593",
        "dimension": 11,
        "vector_count": 593,
        "reported_lower_bound": 593,
        "reported_bound_relation": "kissing_number_11 >= 593",
    },
)
EXPECTED_B11_KISSING_IDS = tuple(row["result_id"] for row in EXPECTED_B11_KISSING_ROWS)
EXPECTED_B12_SUM_OF_RADII_REQUIRED_FIELDS = (
    "result_id",
    "circle_count",
    "container_type",
    "container_artifact_path",
    "container_artifact_sha256",
    "circle_placement_artifact_path",
    "circle_placement_artifact_sha256",
    "circle_payload_schema",
    "containment_certificate_path",
    "containment_certificate_sha256",
    "non_overlap_certificate_path",
    "non_overlap_certificate_sha256",
    "recomputed_sum_of_radii",
    "figure_panel_id",
)
EXPECTED_B13_SUM_OF_RADII_REQUIRED_FIELDS = (
    "result_id",
    "circle_count",
    "container_type",
    "container_artifact_path",
    "container_artifact_sha256",
    "rectangle_dimensions",
    "rectangle_perimeter_certificate_path",
    "rectangle_perimeter_certificate_sha256",
    "circle_placement_artifact_path",
    "circle_placement_artifact_sha256",
    "circle_payload_schema",
    "containment_certificate_path",
    "containment_certificate_sha256",
    "non_overlap_certificate_path",
    "non_overlap_certificate_sha256",
    "recomputed_sum_of_radii",
    "figure_panel_id",
)
EXPECTED_SUM_OF_RADII_SUMMARIES = {
    "circle_packing_unit_square": {
        "status": "not_recorded_locally",
        "source_section_id": "B.12",
        "source_problem_name": "Packing circles inside a unit square to maximize sum of radii",
        "container_type": "unit_square",
        "container_constraint": "unit square",
        "objective": "maximize_sum_of_radii",
        "source_figure": "Figure 14",
        "prior_best_source": "[29]",
        "fixture_boundary": "The checked-in circle_packing fixture is a fixed-26 smoke validator and is not an AlphaEvolve B.12 result artifact.",
        "required_witness_fields": list(EXPECTED_B12_SUM_OF_RADII_REQUIRED_FIELDS),
    },
    "circle_packing_perimeter4_rectangle": {
        "status": "not_recorded_locally",
        "source_section_id": "B.13",
        "source_problem_name": "Packing circles inside a rectangle of perimeter 4 to maximize sum of radii",
        "container_type": "perimeter4_rectangle",
        "container_constraint": "rectangle perimeter = 4",
        "objective": "maximize_sum_of_radii",
        "source_figure": "Figure 14",
        "prior_best_source": "[29]",
        "required_witness_fields": list(EXPECTED_B13_SUM_OF_RADII_REQUIRED_FIELDS),
    },
}
EXPECTED_SUM_OF_RADII_ROWS = {
    "circle_packing_unit_square": (
        {
            "result_id": "b12_unit_square_n26",
            "circle_count": 26,
            "source_figure_panel": "Figure 14 left",
            "prior_sum_of_radii": 2.634,
            "reported_sum_of_radii": 2.635,
            "caption_sum_of_radii_relation": "sum_of_radii >= 2.635",
            "reported_improvement_direction": "larger_sum_of_radii",
        },
        {
            "result_id": "b12_unit_square_n32",
            "circle_count": 32,
            "source_figure_panel": "Figure 14 middle",
            "prior_sum_of_radii": 2.936,
            "reported_sum_of_radii": 2.937,
            "caption_sum_of_radii_relation": "sum_of_radii >= 2.937",
            "reported_improvement_direction": "larger_sum_of_radii",
        },
    ),
    "circle_packing_perimeter4_rectangle": (
        {
            "result_id": "b13_perimeter4_rectangle_n21",
            "circle_count": 21,
            "source_figure_panel": "Figure 14 right",
            "prior_sum_of_radii": 2.364,
            "reported_sum_of_radii": 2.3658,
            "caption_sum_of_radii_relation": "sum_of_radii >= 2.365",
            "reported_improvement_direction": "larger_sum_of_radii",
        },
    ),
}
EXPECTED_SUM_OF_RADII_IDS = {
    family_id: tuple(row["result_id"] for row in rows)
    for family_id, rows in EXPECTED_SUM_OF_RADII_ROWS.items()
}
STATUSES = frozenset({"implemented", "implemented_smoke", "planned", "background_only", "out_of_scope"})
DIRECTIONS = frozenset({"maximize", "minimize", "satisfy", "prove"})
_ID_RE = re.compile(r"[a-z][a-z0-9_]{1,79}")


@dataclass(frozen=True)
class AppendixBRegistryIssue:
    code: str
    message: str
    family_id: str | None = None


@dataclass(frozen=True)
class AppendixBRegistryReport:
    ok: bool
    family_count: int
    implemented_count: int
    planned_count: int
    unsupported_count: int
    issues: list[AppendixBRegistryIssue]


def validate_appendix_b_registry(
    path: str | Path = REGISTRY_PATH,
    *,
    repo_root: str | Path | None = None,
) -> AppendixBRegistryReport:
    registry_path = Path(path)
    root = Path(repo_root) if repo_root is not None else registry_path.parents[3]
    issues: list[AppendixBRegistryIssue] = []
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return AppendixBRegistryReport(False, 0, 0, 0, 0, [
            AppendixBRegistryIssue("read_error", f"failed to read registry: {exc}")
        ])
    except json.JSONDecodeError as exc:
        return AppendixBRegistryReport(False, 0, 0, 0, 0, [
            AppendixBRegistryIssue("invalid_json", f"invalid registry JSON: {exc.msg}")
        ])
    if not isinstance(data, dict):
        return AppendixBRegistryReport(False, 0, 0, 0, 0, [
            AppendixBRegistryIssue("invalid_shape", "registry must be a JSON object")
        ])
    if data.get("schema") != REGISTRY_SCHEMA:
        issues.append(AppendixBRegistryIssue("invalid_schema", "unsupported registry schema"))
    if data.get("source_paper_id") != "2506.13131":
        issues.append(AppendixBRegistryIssue("invalid_source", "source_paper_id must be 2506.13131"))
    families = data.get("families")
    if not isinstance(families, list):
        return AppendixBRegistryReport(False, 0, 0, 0, 0, issues + [
            AppendixBRegistryIssue("invalid_families", "families must be a list")
        ])

    seen: set[str] = set()
    status_counts = {"implemented": 0, "implemented_smoke": 0, "planned": 0, "background_only": 0, "out_of_scope": 0}
    for index, family in enumerate(families):
        family_id = _family_id(family, index)
        if not isinstance(family, dict):
            issues.append(AppendixBRegistryIssue("invalid_family", "family must be an object", family_id))
            continue
        _validate_family(family, family_id, root, issues)
        if family_id in seen:
            issues.append(AppendixBRegistryIssue("duplicate_family", "duplicate family id", family_id))
        seen.add(family_id)
        status = family.get("status")
        if isinstance(status, str) and status in status_counts:
            status_counts[status] += 1
    missing = set(EXPECTED_FAMILY_IDS) - seen
    extra = seen - set(EXPECTED_FAMILY_IDS)
    for family_id in sorted(missing):
        issues.append(AppendixBRegistryIssue("missing_family", "missing Appendix B family", family_id))
    for family_id in sorted(extra):
        issues.append(AppendixBRegistryIssue("extra_family", "unknown Appendix B family", family_id))
    return AppendixBRegistryReport(
        ok=not issues,
        family_count=len(families),
        implemented_count=status_counts["implemented"] + status_counts["implemented_smoke"],
        planned_count=status_counts["planned"],
        unsupported_count=status_counts["background_only"] + status_counts["out_of_scope"],
        issues=issues,
    )


def _validate_family(
    family: dict[str, Any],
    family_id: str,
    repo_root: Path,
    issues: list[AppendixBRegistryIssue],
) -> None:
    if _ID_RE.fullmatch(family_id) is None:
        issues.append(AppendixBRegistryIssue("invalid_family_id", "family id must be snake_case", family_id))
    _require_text(family, "name", family_id, issues)
    _validate_autocorrelation_paper_label(family, family_id, issues)
    _validate_autocorrelation_step_evidence(family, family_id, issues)
    _validate_b8_metric_conventions(family, family_id, issues)
    _validate_b8_witness_boundary(family, family_id, issues)
    _validate_b5_source_formulation(family, family_id, issues)
    _validate_b5_step_function_boundary(family, family_id, issues)
    _validate_b6_theorem_condition(family, family_id, issues)
    _validate_b6_witness_boundary(family, family_id, issues)
    _validate_b7_packing_boundary(family, family_id, issues)
    _validate_heilbronn_boundary(family, family_id, issues)
    _validate_b11_kissing_boundary(family, family_id, issues)
    _validate_sum_of_radii_boundary(family, family_id, issues)
    status = family.get("status")
    if status not in STATUSES:
        issues.append(AppendixBRegistryIssue("invalid_status", "invalid implementation status", family_id))
    objective = family.get("objective")
    if not isinstance(objective, dict):
        issues.append(AppendixBRegistryIssue("invalid_objective", "objective must be an object", family_id))
    else:
        _require_text(objective, "metric", family_id, issues)
        if objective.get("direction") not in DIRECTIONS:
            issues.append(AppendixBRegistryIssue("invalid_direction", "invalid objective direction", family_id))
    target = family.get("target_baseline")
    if not isinstance(target, dict) or not isinstance(target.get("status"), str) or not target["status"]:
        issues.append(AppendixBRegistryIssue("invalid_target_baseline", "target_baseline.status is required", family_id))
    artifact_schema = family.get("artifact_schema")
    if not isinstance(artifact_schema, dict):
        issues.append(AppendixBRegistryIssue("invalid_artifact_schema", "artifact_schema must be an object", family_id))
    else:
        _require_text(artifact_schema, "construction", family_id, issues)
        _require_text(artifact_schema, "certificate", family_id, issues)
        _validate_b5_artifact_schema(artifact_schema, family_id, issues)
    _require_text(family, "certification", family_id, issues)
    _require_text(family, "rationale", family_id, issues)
    citations = family.get("paper_citations")
    if not isinstance(citations, list) or "2506.13131" not in citations:
        issues.append(AppendixBRegistryIssue("missing_alphaevolve_citation", "paper_citations must include 2506.13131", family_id))
    fixture = family.get("fixture")
    if status in {"implemented", "implemented_smoke"}:
        if not isinstance(fixture, str) or not fixture:
            issues.append(AppendixBRegistryIssue("missing_fixture", "implemented family requires fixture", family_id))
        elif not _fixture_exists(repo_root, fixture):
            issues.append(AppendixBRegistryIssue("missing_fixture_path", f"fixture does not exist: {fixture}", family_id))
    elif fixture is not None:
        issues.append(AppendixBRegistryIssue("unexpected_fixture", "non-implemented family must not advertise a fixture", family_id))


def _validate_autocorrelation_paper_label(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    expected = EXPECTED_AUTOCORRELATION_LABELS.get(family_id)
    if expected is None:
        return
    label = family.get("paper_label")
    if not isinstance(label, dict):
        issues.append(AppendixBRegistryIssue("missing_paper_label", "B.1-B.3 autocorrelation rows require paper_label metadata", family_id))
        return
    if label.get("internal_family_id") != family_id:
        issues.append(AppendixBRegistryIssue("invalid_paper_label_internal_id", "paper_label.internal_family_id must match the registry id", family_id))
    for field, expected_value in expected.items():
        if label.get(field) != expected_value:
            issues.append(AppendixBRegistryIssue(f"invalid_paper_label_{field}", f"paper_label.{field} must match the AlphaEvolve Appendix B heading metadata", family_id))
    display_label = label.get("display_label")
    if family.get("name") != display_label:
        issues.append(AppendixBRegistryIssue("paper_label_name_mismatch", "family name must use the paper-facing B.1-B.3 display label", family_id))
    if isinstance(family.get("name"), str) and re.search(r"\bk\s*=", family["name"]):
        issues.append(AppendixBRegistryIssue("paper_label_uses_internal_k_label", "family name must not expose internal k-number labels as paper terminology", family_id))


def _validate_autocorrelation_step_evidence(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    expected = EXPECTED_AUTOCORRELATION_STEP_EVIDENCE.get(family_id)
    if expected is None:
        return
    evidence = family.get("step_function_evidence")
    if not isinstance(evidence, dict):
        issues.append(AppendixBRegistryIssue("missing_step_function_evidence", "B.1-B.3 autocorrelation rows require step_function_evidence metadata", family_id))
        return
    for field, expected_value in expected.items():
        actual = evidence.get(field)
        if isinstance(expected_value, float):
            if isinstance(actual, bool) or not isinstance(actual, (int, float)) or float(actual) != expected_value:
                issues.append(AppendixBRegistryIssue(f"invalid_step_function_{field}", f"step_function_evidence.{field} must match the AlphaEvolve Appendix B value", family_id))
        elif actual != expected_value:
            issues.append(AppendixBRegistryIssue(f"invalid_step_function_{field}", f"step_function_evidence.{field} must match the AlphaEvolve Appendix B value", family_id))
    label = family.get("paper_label")
    if isinstance(label, dict):
        if evidence.get("source_section_id") != label.get("source_section_id"):
            issues.append(AppendixBRegistryIssue("step_function_label_section_mismatch", "step_function_evidence source section must match paper_label", family_id))
        if evidence.get("constant_id") != label.get("constant_id"):
            issues.append(AppendixBRegistryIssue("step_function_label_constant_mismatch", "step_function_evidence constant id must match paper_label", family_id))


def _validate_b8_metric_conventions(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    if family_id != "max_min_distance_point_sets":
        return
    conventions = family.get("metric_convention_evidence")
    if not isinstance(conventions, list):
        issues.append(AppendixBRegistryIssue("missing_b8_metric_convention_evidence", "B.8 requires metric_convention_evidence rows", family_id))
        return
    if len(conventions) != len(EXPECTED_B8_METRIC_CONVENTIONS):
        issues.append(AppendixBRegistryIssue("invalid_b8_metric_convention_count", "B.8 must include exactly the 2D and 3D metric convention rows", family_id))
    by_id = {
        row.get("result_id"): row
        for row in conventions
        if isinstance(row, dict)
    }
    for expected in EXPECTED_B8_METRIC_CONVENTIONS:
        result_id = expected["result_id"]
        row = by_id.get(result_id)
        if not isinstance(row, dict):
            issues.append(AppendixBRegistryIssue("missing_b8_metric_convention_row", "missing B.8 metric convention row", family_id))
            continue
        for field, expected_value in expected.items():
            actual = row.get(field)
            if isinstance(expected_value, float):
                if isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isclose(float(actual), expected_value, rel_tol=0.0, abs_tol=1e-12):
                    issues.append(AppendixBRegistryIssue(f"invalid_b8_{field}", f"B.8 {field} must match the AlphaEvolve metric convention evidence", family_id))
            elif actual != expected_value:
                issues.append(AppendixBRegistryIssue(f"invalid_b8_{field}", f"B.8 {field} must match the AlphaEvolve metric convention evidence", family_id))
        raw = row.get("raw_reported_value")
        derived = row.get("derived_ratio")
        if (
            isinstance(raw, (int, float))
            and not isinstance(raw, bool)
            and isinstance(derived, (int, float))
            and not isinstance(derived, bool)
            and not math.isclose(math.sqrt(float(raw)), float(derived), rel_tol=0.0, abs_tol=1e-12)
        ):
            issues.append(AppendixBRegistryIssue("invalid_b8_derived_ratio_math", "B.8 derived_ratio must equal sqrt(raw_reported_value)", family_id))
        prior = row.get("prior_best_value")
        if (
            isinstance(raw, (int, float))
            and not isinstance(raw, bool)
            and isinstance(prior, (int, float))
            and not isinstance(prior, bool)
            and float(raw) >= float(prior)
        ):
            issues.append(AppendixBRegistryIssue("invalid_b8_improvement_direction", "B.8 raw reported squared value must improve on the prior squared value", family_id))


def _validate_b8_witness_boundary(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    if family_id != "max_min_distance_point_sets":
        return
    boundary = family.get("witness_certificate_boundary")
    if not isinstance(boundary, dict):
        issues.append(AppendixBRegistryIssue("missing_b8_witness_boundary", "B.8 requires witness_certificate_boundary", family_id))
        return
    if boundary.get("status") != "not_recorded_locally":
        issues.append(AppendixBRegistryIssue("invalid_b8_witness_boundary_status", "B.8 witness boundary must remain not_recorded_locally until coordinate and certificate artifacts exist", family_id))
    required = boundary.get("required_witness_fields")
    if required != list(EXPECTED_B8_WITNESS_REQUIRED_FIELDS):
        issues.append(AppendixBRegistryIssue("invalid_b8_witness_required_fields", "B.8 witness boundary must enumerate required future coordinate and distance-certificate fields", family_id))
    missing = boundary.get("missing_witnesses")
    if not isinstance(missing, list):
        issues.append(AppendixBRegistryIssue("invalid_b8_missing_witnesses", "B.8 missing_witnesses must be a list", family_id))
        return
    if len(missing) != len(EXPECTED_B8_WITNESS_IDS):
        issues.append(AppendixBRegistryIssue("invalid_b8_missing_witness_count", "B.8 must track both missing point-set witnesses", family_id))
    seen: set[str] = set()
    for witness in missing:
        if not isinstance(witness, dict):
            issues.append(AppendixBRegistryIssue("invalid_b8_missing_witness", "B.8 missing witness rows must be objects", family_id))
            continue
        result_id = witness.get("result_id")
        if result_id not in EXPECTED_B8_WITNESS_IDS:
            issues.append(AppendixBRegistryIssue("invalid_b8_missing_witness_id", "B.8 missing witness result_id must match a convention row", family_id))
        elif isinstance(result_id, str):
            if result_id in seen:
                issues.append(AppendixBRegistryIssue("duplicate_b8_missing_witness_id", "B.8 missing witness ids must be unique", family_id))
            seen.add(result_id)
        for field in ("coordinate_artifact_status", "distance_certificate_status", "recomputed_ratio_status"):
            if witness.get(field) != "not_recorded_locally":
                issues.append(AppendixBRegistryIssue(f"invalid_b8_{field}", f"B.8 {field} must be not_recorded_locally in the absence boundary", family_id))
        claim_boundary = witness.get("claim_boundary")
        if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary:
            issues.append(AppendixBRegistryIssue("missing_b8_witness_claim_boundary", "B.8 missing witness rows must state that local coordinate/certificate evidence is not claimed", family_id))
    for result_id in EXPECTED_B8_WITNESS_IDS:
        if result_id not in seen:
            issues.append(AppendixBRegistryIssue("missing_b8_witness_id", "B.8 witness boundary must include each convention result id", family_id))


def _validate_b5_source_formulation(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    if family_id != "erdos_minimum_overlap":
        return
    evidence = family.get("source_formulation_evidence")
    if not isinstance(evidence, dict):
        issues.append(AppendixBRegistryIssue("missing_b5_source_formulation", "B.5 requires source_formulation_evidence", family_id))
        return
    for field, expected_value in EXPECTED_B5_SOURCE_FORMULATION.items():
        actual = evidence.get(field)
        if isinstance(expected_value, float):
            if isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isclose(float(actual), expected_value, rel_tol=0.0, abs_tol=1e-12):
                issues.append(AppendixBRegistryIssue(f"invalid_b5_{field}", f"B.5 {field} must match the AlphaEvolve source formulation evidence", family_id))
        elif actual != expected_value:
            issues.append(AppendixBRegistryIssue(f"invalid_b5_{field}", f"B.5 {field} must match the AlphaEvolve source formulation evidence", family_id))
    lower = evidence.get("known_lower_bound")
    upper = evidence.get("known_upper_bound")
    if (
        isinstance(lower, (int, float))
        and not isinstance(lower, bool)
        and isinstance(upper, (int, float))
        and not isinstance(upper, bool)
        and float(lower) >= float(upper)
    ):
        issues.append(AppendixBRegistryIssue("invalid_b5_bound_order", "B.5 lower bound must be below the upper bound", family_id))


def _validate_b5_step_function_boundary(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    if family_id != "erdos_minimum_overlap":
        return
    boundary = family.get("step_function_result_boundary")
    if not isinstance(boundary, dict):
        issues.append(AppendixBRegistryIssue("missing_b5_step_function_boundary", "B.5 requires step_function_result_boundary", family_id))
        return
    for field, expected_value in EXPECTED_B5_STEP_FUNCTION_BOUNDARY.items():
        if field in {"status", "required_payload_fields", "claim_boundary"}:
            continue
        actual = boundary.get(field)
        if isinstance(expected_value, float):
            if isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isclose(float(actual), expected_value, rel_tol=0.0, abs_tol=1e-12):
                issues.append(AppendixBRegistryIssue(f"invalid_b5_step_function_{field}", f"B.5 step_function_result_boundary.{field} must match the AlphaEvolve result summary", family_id))
        elif actual != expected_value:
            issues.append(AppendixBRegistryIssue(f"invalid_b5_step_function_{field}", f"B.5 step_function_result_boundary.{field} must match the AlphaEvolve result summary", family_id))
    if boundary.get("status") != "not_recorded_locally":
        issues.append(AppendixBRegistryIssue("invalid_b5_step_function_status", "B.5 Figure 10 payload boundary must remain not_recorded_locally until local artifacts exist", family_id))
    if boundary.get("required_payload_fields") != list(EXPECTED_B5_STEP_FUNCTION_REQUIRED_FIELDS):
        issues.append(AppendixBRegistryIssue("invalid_b5_step_function_required_payload_fields", "B.5 boundary must enumerate required future step-function payload and certificate fields", family_id))
    source = family.get("source_formulation_evidence")
    if isinstance(source, dict) and source.get("mapping_to_step_function_evidence") != boundary.get("result_id"):
        issues.append(AppendixBRegistryIssue("b5_step_function_source_mapping_mismatch", "B.5 source formulation must map to the same Figure 10 result boundary", family_id))
    claim_boundary = boundary.get("claim_boundary")
    if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary:
        issues.append(AppendixBRegistryIssue("missing_b5_step_function_claim_boundary", "B.5 boundary must state that local Figure 10 payload/certificate evidence is not claimed", family_id))
    lower = boundary.get("prior_lower_bound")
    prior_upper = boundary.get("prior_upper_bound")
    reported = boundary.get("reported_upper_bound")
    if (
        isinstance(lower, (int, float))
        and not isinstance(lower, bool)
        and isinstance(prior_upper, (int, float))
        and not isinstance(prior_upper, bool)
        and isinstance(reported, (int, float))
        and not isinstance(reported, bool)
        and not (float(lower) < float(reported) < float(prior_upper))
    ):
        issues.append(AppendixBRegistryIssue("invalid_b5_step_function_bound_order", "B.5 reported upper bound must lie between the prior lower and prior upper bound", family_id))


def _validate_b5_artifact_schema(
    artifact_schema: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    if family_id != "erdos_minimum_overlap":
        return
    if artifact_schema.get("construction") != "normalized_step_function":
        issues.append(AppendixBRegistryIssue("invalid_b5_artifact_construction", "B.5 construction schema must be normalized_step_function", family_id))
    if artifact_schema.get("certificate") != "integral_and_shift_overlap_certificate":
        issues.append(AppendixBRegistryIssue("invalid_b5_artifact_certificate", "B.5 certificate schema must cover integral and shift-overlap verification", family_id))


def _validate_b6_theorem_condition(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    if family_id != "sums_differences_finite_sets":
        return
    evidence = family.get("theorem_condition_evidence")
    if not isinstance(evidence, dict):
        issues.append(AppendixBRegistryIssue("missing_b6_theorem_condition", "B.6 requires theorem_condition_evidence", family_id))
        return
    for field, expected_value in EXPECTED_B6_THEOREM_CONDITION.items():
        actual = evidence.get(field)
        if isinstance(expected_value, float):
            if isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isclose(float(actual), expected_value, rel_tol=0.0, abs_tol=1e-12):
                issues.append(AppendixBRegistryIssue(f"invalid_b6_theorem_{field}", f"B.6 theorem_condition_evidence.{field} must match the AlphaEvolve source theorem", family_id))
        elif actual != expected_value:
            issues.append(AppendixBRegistryIssue(f"invalid_b6_theorem_{field}", f"B.6 theorem_condition_evidence.{field} must match the AlphaEvolve source theorem", family_id))
    lower = evidence.get("known_lower_bound")
    upper = evidence.get("known_upper_bound")
    if (
        isinstance(lower, (int, float))
        and not isinstance(lower, bool)
        and isinstance(upper, (int, float))
        and not isinstance(upper, bool)
        and float(lower) >= float(upper)
    ):
        issues.append(AppendixBRegistryIssue("invalid_b6_theorem_bound_order", "B.6 known lower bound must be below the known upper bound", family_id))


def _validate_b6_witness_boundary(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    if family_id != "sums_differences_finite_sets":
        return
    boundary = family.get("finite_set_witness_boundary")
    if not isinstance(boundary, dict):
        issues.append(AppendixBRegistryIssue("missing_b6_witness_boundary", "B.6 requires finite_set_witness_boundary", family_id))
        return
    if boundary.get("status") != "not_recorded_locally":
        issues.append(AppendixBRegistryIssue("invalid_b6_witness_boundary_status", "B.6 finite-set witness boundary must remain not_recorded_locally until local set and certificate artifacts exist", family_id))
    if boundary.get("source_section_id") != "B.6":
        issues.append(AppendixBRegistryIssue("invalid_b6_witness_source_section_id", "B.6 witness boundary must retain the source section", family_id))
    if boundary.get("constant_id") != "C6":
        issues.append(AppendixBRegistryIssue("invalid_b6_witness_constant_id", "B.6 witness boundary must retain the constant id", family_id))
    theorem = family.get("theorem_condition_evidence")
    expected_theorem_id = EXPECTED_B6_THEOREM_CONDITION["finite_set_theorem_id"]
    if boundary.get("theorem_condition_evidence") != expected_theorem_id:
        issues.append(AppendixBRegistryIssue("invalid_b6_witness_theorem_condition_evidence", "B.6 witness boundary must link to the Gyarmati finite-set theorem id", family_id))
    if isinstance(theorem, dict) and theorem.get("finite_set_theorem_id") != boundary.get("theorem_condition_evidence"):
        issues.append(AppendixBRegistryIssue("b6_witness_theorem_mapping_mismatch", "B.6 theorem evidence and witness boundary must name the same theorem id", family_id))
    if boundary.get("required_witness_fields") != list(EXPECTED_B6_WITNESS_REQUIRED_FIELDS):
        issues.append(AppendixBRegistryIssue("invalid_b6_witness_required_fields", "B.6 boundary must enumerate required future finite-set payload and certificate fields", family_id))
    missing = boundary.get("missing_witnesses")
    if not isinstance(missing, list):
        issues.append(AppendixBRegistryIssue("invalid_b6_missing_witnesses", "B.6 missing_witnesses must be a list", family_id))
        return
    if len(missing) != len(EXPECTED_B6_WITNESS_ROWS):
        issues.append(AppendixBRegistryIssue("invalid_b6_missing_witness_count", "B.6 must track both U1 and U2 witnesses", family_id))
    by_id = {
        witness.get("result_id"): witness
        for witness in missing
        if isinstance(witness, dict)
    }
    seen: set[str] = set()
    prior_lower = EXPECTED_B6_THEOREM_CONDITION["known_lower_bound"]
    known_upper = EXPECTED_B6_THEOREM_CONDITION["known_upper_bound"]
    reported_bounds: list[float] = []
    for expected in EXPECTED_B6_WITNESS_ROWS:
        result_id = expected["result_id"]
        witness = by_id.get(result_id)
        if not isinstance(witness, dict):
            issues.append(AppendixBRegistryIssue("missing_b6_witness_id", "B.6 witness boundary must include U1 and U2 result ids", family_id))
            continue
        if result_id in seen:
            issues.append(AppendixBRegistryIssue("duplicate_b6_witness_id", "B.6 witness ids must be unique", family_id))
        seen.add(result_id)
        for field, expected_value in expected.items():
            actual = witness.get(field)
            if isinstance(expected_value, float):
                if isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isclose(float(actual), expected_value, rel_tol=0.0, abs_tol=1e-12):
                    issues.append(AppendixBRegistryIssue(f"invalid_b6_witness_{field}", f"B.6 witness {field} must match the AlphaEvolve result summary", family_id))
            elif actual != expected_value:
                issues.append(AppendixBRegistryIssue(f"invalid_b6_witness_{field}", f"B.6 witness {field} must match the AlphaEvolve result summary", family_id))
        for field in (
            "integer_set_artifact_status",
            "admissibility_certificate_status",
            "sum_difference_certificate_status",
            "recomputed_lower_bound_status",
        ):
            if witness.get(field) != "not_recorded_locally":
                issues.append(AppendixBRegistryIssue(f"invalid_b6_{field}", f"B.6 {field} must be not_recorded_locally in the absence boundary", family_id))
        claim_boundary = witness.get("claim_boundary")
        if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary:
            issues.append(AppendixBRegistryIssue("missing_b6_witness_claim_boundary", "B.6 missing witness rows must state that local finite-set/certificate evidence is not claimed", family_id))
        reported = witness.get("reported_lower_bound")
        if isinstance(reported, (int, float)) and not isinstance(reported, bool):
            reported_value = float(reported)
            reported_bounds.append(reported_value)
            if not (float(prior_lower) < reported_value < float(known_upper)):
                issues.append(AppendixBRegistryIssue("invalid_b6_witness_bound_order", "B.6 reported witness lower bounds must improve the prior lower bound and stay below the known upper bound", family_id))
    for witness in missing:
        if not isinstance(witness, dict):
            issues.append(AppendixBRegistryIssue("invalid_b6_missing_witness", "B.6 missing witness rows must be objects", family_id))
            continue
        result_id = witness.get("result_id")
        if result_id not in EXPECTED_B6_WITNESS_IDS:
            issues.append(AppendixBRegistryIssue("invalid_b6_missing_witness_id", "B.6 missing witness result_id must match U1 or U2", family_id))
    if len(reported_bounds) == len(EXPECTED_B6_WITNESS_ROWS) and reported_bounds != sorted(reported_bounds):
        issues.append(AppendixBRegistryIssue("invalid_b6_witness_bound_progression", "B.6 U2 reported lower bound must improve on U1", family_id))


def _validate_b7_packing_boundary(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    if family_id != "regular_hexagon_packing":
        return
    boundary = family.get("packing_result_boundary")
    if not isinstance(boundary, dict):
        issues.append(AppendixBRegistryIssue("missing_b7_packing_boundary", "B.7 requires packing_result_boundary", family_id))
        return
    for field, expected_value in EXPECTED_B7_PACKING_SUMMARY.items():
        actual = boundary.get(field)
        if isinstance(expected_value, float):
            if isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isclose(float(actual), expected_value, rel_tol=0.0, abs_tol=1e-12):
                issues.append(AppendixBRegistryIssue(f"invalid_b7_packing_{field}", f"B.7 packing_result_boundary.{field} must match the AlphaEvolve source summary", family_id))
        elif actual != expected_value:
            issues.append(AppendixBRegistryIssue(f"invalid_b7_packing_{field}", f"B.7 packing_result_boundary.{field} must match the AlphaEvolve source summary", family_id))
    if boundary.get("status") != "not_recorded_locally":
        issues.append(AppendixBRegistryIssue("invalid_b7_packing_boundary_status", "B.7 packing boundary must remain not_recorded_locally until placement and certificate artifacts exist", family_id))
    if boundary.get("required_witness_fields") != list(EXPECTED_B7_PACKING_REQUIRED_FIELDS):
        issues.append(AppendixBRegistryIssue("invalid_b7_packing_required_fields", "B.7 boundary must enumerate required future placement and geometry-certificate fields", family_id))
    missing = boundary.get("missing_witnesses")
    if not isinstance(missing, list):
        issues.append(AppendixBRegistryIssue("invalid_b7_missing_witnesses", "B.7 missing_witnesses must be a list", family_id))
        return
    if len(missing) != len(EXPECTED_B7_PACKING_ROWS):
        issues.append(AppendixBRegistryIssue("invalid_b7_missing_witness_count", "B.7 must track both n=11 and n=12 packing witnesses", family_id))
    by_id = {
        witness.get("result_id"): witness
        for witness in missing
        if isinstance(witness, dict)
    }
    seen: set[str] = set()
    for expected in EXPECTED_B7_PACKING_ROWS:
        result_id = expected["result_id"]
        witness = by_id.get(result_id)
        if not isinstance(witness, dict):
            issues.append(AppendixBRegistryIssue("missing_b7_witness_id", "B.7 packing boundary must include both result ids", family_id))
            continue
        if result_id in seen:
            issues.append(AppendixBRegistryIssue("duplicate_b7_witness_id", "B.7 packing witness ids must be unique", family_id))
        seen.add(result_id)
        for field, expected_value in expected.items():
            actual = witness.get(field)
            if isinstance(expected_value, float):
                if isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isclose(float(actual), expected_value, rel_tol=0.0, abs_tol=1e-12):
                    issues.append(AppendixBRegistryIssue(f"invalid_b7_witness_{field}", f"B.7 witness {field} must match the AlphaEvolve result summary", family_id))
            elif actual != expected_value:
                issues.append(AppendixBRegistryIssue(f"invalid_b7_witness_{field}", f"B.7 witness {field} must match the AlphaEvolve result summary", family_id))
        for field in (
            "placement_artifact_status",
            "containment_certificate_status",
            "non_overlap_certificate_status",
            "recomputed_outer_side_length_status",
        ):
            if witness.get(field) != "not_recorded_locally":
                issues.append(AppendixBRegistryIssue(f"invalid_b7_{field}", f"B.7 {field} must be not_recorded_locally in the absence boundary", family_id))
        claim_boundary = witness.get("claim_boundary")
        if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary:
            issues.append(AppendixBRegistryIssue("missing_b7_witness_claim_boundary", "B.7 missing witness rows must state that local placement/certificate evidence is not claimed", family_id))
        prior = witness.get("prior_outer_side_length")
        reported = witness.get("reported_outer_side_length")
        if (
            isinstance(prior, (int, float))
            and not isinstance(prior, bool)
            and isinstance(reported, (int, float))
            and not isinstance(reported, bool)
            and float(reported) >= float(prior)
        ):
            issues.append(AppendixBRegistryIssue("invalid_b7_improvement_direction", "B.7 reported outer side length must improve by being smaller than the prior side length", family_id))
    for witness in missing:
        if not isinstance(witness, dict):
            issues.append(AppendixBRegistryIssue("invalid_b7_missing_witness", "B.7 missing witness rows must be objects", family_id))
            continue
        result_id = witness.get("result_id")
        if result_id not in EXPECTED_B7_PACKING_IDS:
            issues.append(AppendixBRegistryIssue("invalid_b7_missing_witness_id", "B.7 missing witness result_id must match n=11 or n=12", family_id))


def _validate_heilbronn_boundary(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    expected_summary = EXPECTED_HEILBRONN_SUMMARIES.get(family_id)
    if expected_summary is None:
        return
    boundary = family.get("heilbronn_result_boundary")
    if not isinstance(boundary, dict):
        issues.append(AppendixBRegistryIssue("missing_heilbronn_boundary", "B.9-B.10 require heilbronn_result_boundary", family_id))
        return
    for field, expected_value in expected_summary.items():
        actual = boundary.get(field)
        if isinstance(expected_value, float):
            if isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isclose(float(actual), expected_value, rel_tol=0.0, abs_tol=1e-12):
                issues.append(AppendixBRegistryIssue(f"invalid_heilbronn_{field}", f"Heilbronn boundary {field} must match the AlphaEvolve source summary", family_id))
        elif actual != expected_value:
            issues.append(AppendixBRegistryIssue(f"invalid_heilbronn_{field}", f"Heilbronn boundary {field} must match the AlphaEvolve source summary", family_id))
    if boundary.get("status") != "not_recorded_locally":
        issues.append(AppendixBRegistryIssue("invalid_heilbronn_boundary_status", "Heilbronn boundary must remain not_recorded_locally until point/domain/certificate artifacts exist", family_id))
    if boundary.get("required_witness_fields") != expected_summary["required_witness_fields"]:
        issues.append(AppendixBRegistryIssue("invalid_heilbronn_required_fields", "Heilbronn boundary must enumerate required future point, domain, and area-certificate fields", family_id))
    missing = boundary.get("missing_witnesses")
    if not isinstance(missing, list):
        issues.append(AppendixBRegistryIssue("invalid_heilbronn_missing_witnesses", "Heilbronn missing_witnesses must be a list", family_id))
        return
    expected_rows = EXPECTED_HEILBRONN_ROWS[family_id]
    expected_ids = EXPECTED_HEILBRONN_IDS[family_id]
    if len(missing) != len(expected_rows):
        issues.append(AppendixBRegistryIssue("invalid_heilbronn_missing_witness_count", "Heilbronn boundary must track the expected Figure 13 witness rows", family_id))
    by_id = {
        witness.get("result_id"): witness
        for witness in missing
        if isinstance(witness, dict)
    }
    seen: set[str] = set()
    for expected in expected_rows:
        result_id = expected["result_id"]
        witness = by_id.get(result_id)
        if not isinstance(witness, dict):
            issues.append(AppendixBRegistryIssue("missing_heilbronn_witness_id", "Heilbronn boundary must include each expected result id", family_id))
            continue
        if result_id in seen:
            issues.append(AppendixBRegistryIssue("duplicate_heilbronn_witness_id", "Heilbronn witness ids must be unique", family_id))
        seen.add(result_id)
        for field, expected_value in expected.items():
            actual = witness.get(field)
            if isinstance(expected_value, float):
                if isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isclose(float(actual), expected_value, rel_tol=0.0, abs_tol=1e-12):
                    issues.append(AppendixBRegistryIssue(f"invalid_heilbronn_witness_{field}", f"Heilbronn witness {field} must match the AlphaEvolve result summary", family_id))
            elif actual != expected_value:
                issues.append(AppendixBRegistryIssue(f"invalid_heilbronn_witness_{field}", f"Heilbronn witness {field} must match the AlphaEvolve result summary", family_id))
        required_status_fields = [
            "point_coordinate_artifact_status",
            "domain_artifact_status",
            "domain_membership_certificate_status",
            "unit_area_certificate_status",
            "all_triples_area_certificate_status",
            "recomputed_minimum_area_status",
        ]
        if family_id == "heilbronn_convex_region":
            required_status_fields.append("convexity_certificate_status")
        for field in required_status_fields:
            if witness.get(field) != "not_recorded_locally":
                issues.append(AppendixBRegistryIssue(f"invalid_heilbronn_{field}", f"Heilbronn {field} must be not_recorded_locally in the absence boundary", family_id))
        claim_boundary = witness.get("claim_boundary")
        if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary:
            issues.append(AppendixBRegistryIssue("missing_heilbronn_witness_claim_boundary", "Heilbronn missing witness rows must state that local coordinate/domain/certificate evidence is not claimed", family_id))
        prior = witness.get("prior_minimum_area")
        reported = witness.get("reported_minimum_area")
        if (
            isinstance(prior, (int, float))
            and not isinstance(prior, bool)
            and isinstance(reported, (int, float))
            and not isinstance(reported, bool)
            and float(reported) <= float(prior)
        ):
            issues.append(AppendixBRegistryIssue("invalid_heilbronn_improvement_direction", "Heilbronn reported minimum area must improve by exceeding the prior minimum area", family_id))
    for witness in missing:
        if not isinstance(witness, dict):
            issues.append(AppendixBRegistryIssue("invalid_heilbronn_missing_witness", "Heilbronn missing witness rows must be objects", family_id))
            continue
        result_id = witness.get("result_id")
        if result_id not in expected_ids:
            issues.append(AppendixBRegistryIssue("invalid_heilbronn_missing_witness_id", "Heilbronn missing witness result_id must match the expected Figure 13 rows", family_id))


def _validate_b11_kissing_boundary(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    if family_id != "kissing_number_d11":
        return
    boundary = family.get("kissing_result_boundary")
    if not isinstance(boundary, dict):
        issues.append(AppendixBRegistryIssue("missing_b11_kissing_boundary", "B.11 requires kissing_result_boundary", family_id))
        return
    for field, expected_value in EXPECTED_B11_KISSING_SUMMARY.items():
        actual = boundary.get(field)
        if actual != expected_value:
            issues.append(AppendixBRegistryIssue(f"invalid_b11_kissing_{field}", f"B.11 kissing_result_boundary.{field} must match the AlphaEvolve source summary", family_id))
    if boundary.get("status") != "not_recorded_locally":
        issues.append(AppendixBRegistryIssue("invalid_b11_kissing_boundary_status", "B.11 kissing boundary must remain not_recorded_locally until vector and certificate artifacts exist", family_id))
    if boundary.get("required_witness_fields") != list(EXPECTED_B11_KISSING_REQUIRED_FIELDS):
        issues.append(AppendixBRegistryIssue("invalid_b11_kissing_required_fields", "B.11 boundary must enumerate required future vector, norm/distance, and lemma-certificate fields", family_id))
    prior = boundary.get("prior_lower_bound")
    reported = boundary.get("reported_lower_bound")
    if (
        isinstance(prior, int)
        and not isinstance(prior, bool)
        and isinstance(reported, int)
        and not isinstance(reported, bool)
        and reported <= prior
    ):
        issues.append(AppendixBRegistryIssue("invalid_b11_kissing_improvement_direction", "B.11 reported lower bound must improve on the prior lower bound", family_id))
    missing = boundary.get("missing_witnesses")
    if not isinstance(missing, list):
        issues.append(AppendixBRegistryIssue("invalid_b11_kissing_missing_witnesses", "B.11 missing_witnesses must be a list", family_id))
        return
    if len(missing) != len(EXPECTED_B11_KISSING_ROWS):
        issues.append(AppendixBRegistryIssue("invalid_b11_kissing_missing_witness_count", "B.11 must track the 593-vector witness", family_id))
    by_id = {
        witness.get("result_id"): witness
        for witness in missing
        if isinstance(witness, dict)
    }
    seen: set[str] = set()
    for expected in EXPECTED_B11_KISSING_ROWS:
        result_id = expected["result_id"]
        witness = by_id.get(result_id)
        if not isinstance(witness, dict):
            issues.append(AppendixBRegistryIssue("missing_b11_kissing_witness_id", "B.11 boundary must include the 593-vector result id", family_id))
            continue
        if result_id in seen:
            issues.append(AppendixBRegistryIssue("duplicate_b11_kissing_witness_id", "B.11 witness ids must be unique", family_id))
        seen.add(result_id)
        for field, expected_value in expected.items():
            if witness.get(field) != expected_value:
                issues.append(AppendixBRegistryIssue(f"invalid_b11_kissing_witness_{field}", f"B.11 witness {field} must match the AlphaEvolve result summary", family_id))
        for field in (
            "vector_artifact_status",
            "integral_coordinate_certificate_status",
            "nonzero_certificate_status",
            "norm_distance_certificate_status",
            "lemma_applicability_certificate_status",
            "transformed_center_certificate_status",
            "recomputed_lower_bound_status",
        ):
            if witness.get(field) != "not_recorded_locally":
                issues.append(AppendixBRegistryIssue(f"invalid_b11_kissing_{field}", f"B.11 {field} must be not_recorded_locally in the absence boundary", family_id))
        claim_boundary = witness.get("claim_boundary")
        if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary:
            issues.append(AppendixBRegistryIssue("missing_b11_kissing_claim_boundary", "B.11 missing witness row must state that local vector/certificate evidence is not claimed", family_id))
    for witness in missing:
        if not isinstance(witness, dict):
            issues.append(AppendixBRegistryIssue("invalid_b11_kissing_missing_witness", "B.11 missing witness rows must be objects", family_id))
            continue
        result_id = witness.get("result_id")
        if result_id not in EXPECTED_B11_KISSING_IDS:
            issues.append(AppendixBRegistryIssue("invalid_b11_kissing_missing_witness_id", "B.11 missing witness result_id must match the 593-vector row", family_id))


def _validate_sum_of_radii_boundary(
    family: dict[str, Any],
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    expected_summary = EXPECTED_SUM_OF_RADII_SUMMARIES.get(family_id)
    if expected_summary is None:
        return
    boundary = family.get("sum_of_radii_result_boundary")
    if not isinstance(boundary, dict):
        issues.append(AppendixBRegistryIssue("missing_sum_of_radii_boundary", "B.12-B.13 require sum_of_radii_result_boundary", family_id))
        return
    for field, expected_value in expected_summary.items():
        actual = boundary.get(field)
        if actual != expected_value:
            issues.append(AppendixBRegistryIssue(f"invalid_sum_of_radii_{field}", f"sum_of_radii_result_boundary.{field} must match the AlphaEvolve source summary", family_id))
    if boundary.get("status") != "not_recorded_locally":
        issues.append(AppendixBRegistryIssue("invalid_sum_of_radii_boundary_status", "sum-of-radii boundary must remain not_recorded_locally until placement and certificate artifacts exist", family_id))
    if boundary.get("required_witness_fields") != expected_summary["required_witness_fields"]:
        issues.append(AppendixBRegistryIssue("invalid_sum_of_radii_required_fields", "sum-of-radii boundary must enumerate required future placement, container, and certificate fields", family_id))
    if family_id == "circle_packing_unit_square" and "smoke validator" not in str(boundary.get("fixture_boundary", "")):
        issues.append(AppendixBRegistryIssue("missing_sum_of_radii_fixture_boundary", "B.12 must distinguish the checked-in smoke fixture from AlphaEvolve result artifacts", family_id))
    missing = boundary.get("missing_witnesses")
    if not isinstance(missing, list):
        issues.append(AppendixBRegistryIssue("invalid_sum_of_radii_missing_witnesses", "sum-of-radii missing_witnesses must be a list", family_id))
        return
    expected_rows = EXPECTED_SUM_OF_RADII_ROWS[family_id]
    expected_ids = EXPECTED_SUM_OF_RADII_IDS[family_id]
    if len(missing) != len(expected_rows):
        issues.append(AppendixBRegistryIssue("invalid_sum_of_radii_missing_witness_count", "sum-of-radii boundary must track the expected Figure 14 witness rows", family_id))
    by_id = {
        witness.get("result_id"): witness
        for witness in missing
        if isinstance(witness, dict)
    }
    seen: set[str] = set()
    for expected in expected_rows:
        result_id = expected["result_id"]
        witness = by_id.get(result_id)
        if not isinstance(witness, dict):
            issues.append(AppendixBRegistryIssue("missing_sum_of_radii_witness_id", "sum-of-radii boundary must include each expected result id", family_id))
            continue
        if result_id in seen:
            issues.append(AppendixBRegistryIssue("duplicate_sum_of_radii_witness_id", "sum-of-radii witness ids must be unique", family_id))
        seen.add(result_id)
        for field, expected_value in expected.items():
            actual = witness.get(field)
            if isinstance(expected_value, float):
                if isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isclose(float(actual), expected_value, rel_tol=0.0, abs_tol=1e-12):
                    issues.append(AppendixBRegistryIssue(f"invalid_sum_of_radii_witness_{field}", f"sum-of-radii witness {field} must match the AlphaEvolve result summary", family_id))
            elif actual != expected_value:
                issues.append(AppendixBRegistryIssue(f"invalid_sum_of_radii_witness_{field}", f"sum-of-radii witness {field} must match the AlphaEvolve result summary", family_id))
        required_status_fields = [
            "circle_placement_artifact_status",
            "containment_certificate_status",
            "non_overlap_certificate_status",
            "recomputed_sum_of_radii_status",
        ]
        if family_id == "circle_packing_perimeter4_rectangle":
            required_status_fields.append("rectangle_perimeter_certificate_status")
        for field in required_status_fields:
            if witness.get(field) != "not_recorded_locally":
                issues.append(AppendixBRegistryIssue(f"invalid_sum_of_radii_{field}", f"sum-of-radii {field} must be not_recorded_locally in the absence boundary", family_id))
        claim_boundary = witness.get("claim_boundary")
        if not isinstance(claim_boundary, str) or "does not claim" not in claim_boundary:
            issues.append(AppendixBRegistryIssue("missing_sum_of_radii_claim_boundary", "sum-of-radii missing witness rows must state that local placement/certificate evidence is not claimed", family_id))
        prior = witness.get("prior_sum_of_radii")
        reported = witness.get("reported_sum_of_radii")
        if (
            isinstance(prior, (int, float))
            and not isinstance(prior, bool)
            and isinstance(reported, (int, float))
            and not isinstance(reported, bool)
            and float(reported) <= float(prior)
        ):
            issues.append(AppendixBRegistryIssue("invalid_sum_of_radii_improvement_direction", "reported sum of radii must improve by exceeding the prior value", family_id))
    for witness in missing:
        if not isinstance(witness, dict):
            issues.append(AppendixBRegistryIssue("invalid_sum_of_radii_missing_witness", "sum-of-radii missing witness rows must be objects", family_id))
            continue
        result_id = witness.get("result_id")
        if result_id not in expected_ids:
            issues.append(AppendixBRegistryIssue("invalid_sum_of_radii_missing_witness_id", "sum-of-radii missing witness result_id must match the expected Figure 14 rows", family_id))


def _family_id(family: object, index: int) -> str:
    if isinstance(family, dict) and isinstance(family.get("id"), str):
        return family["id"]
    return f"family_{index}"


def _require_text(
    value: dict[str, Any],
    field: str,
    family_id: str,
    issues: list[AppendixBRegistryIssue],
) -> None:
    raw = value.get(field)
    if not isinstance(raw, str) or not raw.strip():
        issues.append(AppendixBRegistryIssue(f"missing_{field}", f"{field} is required", family_id))


def _fixture_exists(repo_root: Path, fixture: str) -> bool:
    if fixture.startswith("/") or "\\" in fixture or ".." in Path(fixture).parts:
        return False
    path = repo_root / fixture
    return (
        path.is_dir()
        and (path / "metrics.yaml").is_file()
        and (path / "validate.py").is_file()
        and (path / "task_description.txt").is_file()
    )
