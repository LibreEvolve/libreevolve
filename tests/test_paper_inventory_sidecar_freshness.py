import json
from pathlib import Path

from libreevolve.problems.benchmarks.alphaevolve_tex_proposition_inventory_boundary import (
    alphaevolve_tex_proposition_inventory_boundary_record,
)
from libreevolve.problems.benchmarks.alphaevolve_tex_prose_inventory_boundary import (
    alphaevolve_tex_prose_inventory_boundary_record,
)
from libreevolve.problems.benchmarks.implementation_evidence_map_boundary import (
    implementation_evidence_map_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_source_span_coverage_boundary import (
    roadmap_source_span_coverage_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_source_span_disposition_boundary import (
    roadmap_source_span_disposition_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_source_span_exhaustiveness_boundary import (
    roadmap_source_span_exhaustiveness_boundary_record,
)


def test_paper_inventory_sidecars_match_authoritative_records(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(root)
    records = {
        "papers/alphaevolve_tex_prose_inventory_boundary.json":
        alphaevolve_tex_prose_inventory_boundary_record(root),
        "papers/alphaevolve_tex_proposition_inventory_boundary.json":
        alphaevolve_tex_proposition_inventory_boundary_record(root),
        "papers/implementation_evidence_map_boundary.json":
        implementation_evidence_map_boundary_record(),
        "papers/roadmap_source_span_coverage_boundary.json":
        roadmap_source_span_coverage_boundary_record(root),
        "papers/roadmap_source_span_disposition_boundary.json":
        roadmap_source_span_disposition_boundary_record(root),
        "papers/roadmap_source_span_exhaustiveness_boundary.json":
        roadmap_source_span_exhaustiveness_boundary_record(root),
    }

    for relative_path, expected in records.items():
        actual = json.loads((root / relative_path).read_text(encoding="utf-8"))
        assert actual == expected, f"stale generated sidecar: {relative_path}"
