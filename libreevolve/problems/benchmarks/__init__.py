"""Benchmark registry metadata."""

from libreevolve.problems.benchmarks.ablation_results import (
    ABLATION_ARTIFACT_INVENTORY_SCHEMA,
    ABLATION_RESULT_SCHEMA,
    ablation_result_artifact_inventory,
    render_ablation_result_summary,
    validate_ablation_result_report,
)
from libreevolve.problems.benchmarks.appendix_a_matrix_registry import (
    EXPECTED_TARGET_COUNT,
    REGISTRY_SCHEMA as APPENDIX_A_MATRIX_REGISTRY_SCHEMA,
    TARGET_SUITE as APPENDIX_A_MATRIX_TARGET_SUITE,
    matrix_target_by_id,
    matrix_target_records,
    render_appendix_a_matrix_registry_summary,
    validate_appendix_a_matrix_registry,
)
from libreevolve.problems.benchmarks.example_scope import (
    EXAMPLE_BENCHMARK_SCOPE_SCHEMA,
    example_benchmark_scope_records,
    render_example_benchmark_scope_summary,
    validate_example_benchmark_scope,
)
from libreevolve.problems.benchmarks.matrix_results import (
    MATRIX_ARTIFACT_INVENTORY_SCHEMA,
    MATRIX_RESULT_SCHEMA,
    matrix_result_artifact_inventory,
    render_matrix_result_summary,
    validate_matrix_result_report,
    write_strassen_2x2_publication_bundle,
)
from libreevolve.problems.benchmarks.result_certification import (
    CERTIFICATION_ARTIFACT_INVENTORY_SCHEMA,
    PAPER_CERTIFICATION_SCHEMA,
    certification_artifact_inventory,
    render_certification_summary,
    validate_paper_result_certification,
)
from libreevolve.problems.benchmarks.systems_results import (
    SYSTEMS_ARTIFACT_INVENTORY_SCHEMA,
    SYSTEMS_RESULT_SCHEMA,
    render_systems_result_summary,
    systems_result_artifact_inventory,
    validate_systems_result_report,
)

__all__ = [
    "ABLATION_ARTIFACT_INVENTORY_SCHEMA",
    "ABLATION_RESULT_SCHEMA",
    "APPENDIX_A_MATRIX_REGISTRY_SCHEMA",
    "APPENDIX_A_MATRIX_TARGET_SUITE",
    "CERTIFICATION_ARTIFACT_INVENTORY_SCHEMA",
    "EXPECTED_TARGET_COUNT",
    "EXAMPLE_BENCHMARK_SCOPE_SCHEMA",
    "MATRIX_ARTIFACT_INVENTORY_SCHEMA",
    "MATRIX_RESULT_SCHEMA",
    "PAPER_CERTIFICATION_SCHEMA",
    "SYSTEMS_ARTIFACT_INVENTORY_SCHEMA",
    "SYSTEMS_RESULT_SCHEMA",
    "ablation_result_artifact_inventory",
    "certification_artifact_inventory",
    "example_benchmark_scope_records",
    "matrix_result_artifact_inventory",
    "matrix_target_by_id",
    "matrix_target_records",
    "render_ablation_result_summary",
    "render_appendix_a_matrix_registry_summary",
    "render_certification_summary",
    "render_example_benchmark_scope_summary",
    "render_matrix_result_summary",
    "render_systems_result_summary",
    "systems_result_artifact_inventory",
    "validate_ablation_result_report",
    "validate_appendix_a_matrix_registry",
    "validate_example_benchmark_scope",
    "validate_matrix_result_report",
    "validate_paper_result_certification",
    "validate_systems_result_report",
    "write_strassen_2x2_publication_bundle",
]
