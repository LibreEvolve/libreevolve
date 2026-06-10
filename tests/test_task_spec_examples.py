import json
from pathlib import Path

from libreevolve.core.database import validate_task_specification_bundle


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = ROOT / "docs" / "examples"


def test_task_specification_examples_validate():
    paths = sorted(EXAMPLE_DIR.glob("task_specification.*.json"))
    assert paths
    for path in paths:
        bundle = json.loads(path.read_text(encoding="utf-8"))
        validation = validate_task_specification_bundle(bundle)
        assert validation["ok"] is True, path
        assert bundle["validation"]["ok"] is True
        assert bundle["validation"]["issues"] == []
        assert bundle["status"] == "partial_alphaevolve_task_specification"
        assert "example_is_documentation_fixture_not_runtime_manifest" in (
            bundle["unsupported_or_incomplete"]
        )
        assert "startup_task_spec_needs_runtime_score_path_causal_attribution" in (
            bundle["unsupported_or_incomplete"]
        )
