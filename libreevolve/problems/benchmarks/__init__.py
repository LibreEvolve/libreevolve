"""Benchmark registry metadata."""

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

__all__ = [
    "APPENDIX_A_MATRIX_REGISTRY_SCHEMA",
    "APPENDIX_A_MATRIX_TARGET_SUITE",
    "EXPECTED_TARGET_COUNT",
    "EXAMPLE_BENCHMARK_SCOPE_SCHEMA",
    "example_benchmark_scope_records",
    "matrix_target_by_id",
    "matrix_target_records",
    "render_appendix_a_matrix_registry_summary",
    "render_example_benchmark_scope_summary",
    "validate_appendix_a_matrix_registry",
    "validate_example_benchmark_scope",
]
