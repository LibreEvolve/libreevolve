from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEVELOPMENT_PROVIDER_EXAMPLE_BOUNDARY_SCHEMA = (
    "libreevolve.development_provider_example_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "development_provider_examples_static_inventory_with_paired_show_commands"
)
DEVELOPMENT_DOC_PATH = "docs/development.md"
README_PATH = "README.md"
DOCS_INDEX_PATH = "docs/README.md"
BACKENDS_PATH = "docs/backends.md"
STATUS_PATH = "docs/status.md"
PAPERS_README_PATH = "papers/README.md"
README_PROVIDER_MATRIX_PATH = "papers/readme_provider_example_matrix_boundary.json"
PROVIDER_AUTH_PATH = "papers/readme_provider_auth_boundary.json"
GEMINI_PROVIDER_PARITY_PATH = "papers/gemini_provider_parity_boundary.json"
README_TODO_PATH = "docs/todo/readme.md"

EXPECTED_PROVIDER_EXAMPLES = (
    {
        "example_id": "development_openai_hello_world",
        "provider": "openai",
        "problem": "hello_world",
        "command_marker": (
            'py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world '
            '--max-generations 10 --backends "openai:<openai-model-id>" '
            '--run-name development_hello_world --overwrite'
        ),
        "placeholder": "<openai-model-id>",
        "expected_run_dir": "runs/development_hello_world",
        "show_marker": "py -3.12 -m libreevolve show runs/development_hello_world",
    },
    {
        "example_id": "development_anthropic_circle_packing",
        "provider": "anthropic",
        "problem": "circle_packing",
        "command_marker": (
            'py -3.12 -m libreevolve run libreevolve/problems/examples/circle_packing '
            '--max-generations 10 --backends "anthropic:<anthropic-model-id>" '
            '--run-name development_circle_packing --overwrite'
        ),
        "placeholder": "<anthropic-model-id>",
        "expected_run_dir": "runs/development_circle_packing",
        "show_marker": "py -3.12 -m libreevolve show runs/development_circle_packing",
    },
)
EXPECTED_GUIDANCE_MARKERS = (
    ("development_placeholder_guidance", DEVELOPMENT_DOC_PATH, "Replace placeholder backend model ids with currently available provider/account\nmodel ids before running."),
    ("readme_provider_model_guidance", README_PATH, "available in\nyour account or local Ollama install"),
    ("readme_provider_failure_scope", README_PATH, "credentials, model IDs, local Ollama state, or account access"),
    ("docs_index_development_route", DOCS_INDEX_PATH, "[Development](./development.md)"),
    ("docs_index_backend_route", DOCS_INDEX_PATH, "[Backends](./backends.md)"),
    ("backend_builtin_provider_lane", BACKENDS_PATH, "Built-in SDK adapters"),
    ("backend_gemini_absence", BACKENDS_PATH, "Google/Gemini is not a built-in registry provider yet"),
    ("status_builtin_provider_boundary", STATUS_PATH, "Built-in provider adapters are OpenAI, Anthropic, and Ollama"),
    ("papers_readme_provider_matrix", PAPERS_README_PATH, "papers/readme_provider_example_matrix_boundary.json"),
    ("papers_readme_provider_auth", PAPERS_README_PATH, "papers/readme_provider_auth_boundary.json"),
    ("papers_readme_gemini_provider_parity", PAPERS_README_PATH, "papers/gemini_provider_parity_boundary.json"),
    ("papers_readme_provider_smoke_gap", PAPERS_README_PATH, "credential-safe provider smoke matrix"),
    ("active_todo_owner", README_TODO_PATH, "Add development-guide provider example smoke evidence."),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "development_provider_command_markers",
    "development_provider_placeholder_guidance",
    "development_provider_show_pairing",
    "readme_provider_model_guidance",
    "readme_provider_failure_scope",
    "docs_index_development_route",
    "backend_provider_lane_and_gemini_boundary",
    "status_provider_boundary",
    "readme_provider_matrix_sidecar_anchor",
    "provider_auth_sidecar_anchor",
    "gemini_provider_parity_sidecar_anchor",
    "active_todo_owner_anchor",
    "live_openai_model_availability_probe",
    "live_anthropic_model_availability_probe",
    "credential_safe_development_provider_smoke",
    "account_specific_model_id_provenance",
    "ci_development_provider_matrix",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "live_openai_model_availability_probe": "not_recorded_locally",
    "live_anthropic_model_availability_probe": "not_recorded_locally",
    "credential_safe_development_provider_smoke": "not_recorded_locally",
    "account_specific_model_id_provenance": "not_recorded_locally",
    "ci_development_provider_matrix": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class DevelopmentProviderExampleBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class DevelopmentProviderExampleBoundaryValidation:
    ok: bool
    boundary_status: str | None
    provider_example_count: int
    missing_command_count: int
    unpaired_show_count: int
    guidance_marker_count: int
    missing_guidance_marker_count: int
    missing_evidence_count: int
    issues: list[DevelopmentProviderExampleBoundaryIssue]


def development_provider_example_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the development-guide provider-example static inventory."""

    root_path = Path(root)
    development_text = _read_text(root_path / DEVELOPMENT_DOC_PATH)
    texts = {
        path: _read_text(root_path / path)
        for path in (
            DEVELOPMENT_DOC_PATH,
            README_PATH,
            DOCS_INDEX_PATH,
            BACKENDS_PATH,
            STATUS_PATH,
            PAPERS_README_PATH,
            README_TODO_PATH,
        )
    }
    provider_records = [
        _provider_record(development_text, spec)
        for spec in EXPECTED_PROVIDER_EXAMPLES
    ]
    missing_command_records = [
        record
        for record in provider_records
        if record["command_marker_status"] != "command_marker_present"
    ]
    unpaired_show_records = [
        record
        for record in provider_records
        if record["show_marker_status"] != "show_marker_present"
    ]
    guidance_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_GUIDANCE_MARKERS
    ]
    missing_guidance_records = [
        record for record in guidance_records if record["marker_status"] != "marker_present"
    ]
    return {
        "schema": DEVELOPMENT_PROVIDER_EXAMPLE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "development_doc_path": DEVELOPMENT_DOC_PATH,
        "provider_example_count": len(provider_records),
        "missing_command_count": len(missing_command_records),
        "missing_command_records": missing_command_records,
        "unpaired_show_count": len(unpaired_show_records),
        "unpaired_show_records": unpaired_show_records,
        "provider_example_records": provider_records,
        "guidance_marker_count": len(guidance_records),
        "missing_guidance_marker_count": len(missing_guidance_records),
        "missing_guidance_marker_records": missing_guidance_records,
        "guidance_marker_records": guidance_records,
        "development_provider_example_status": (
            "development_provider_examples_static_inventory_with_paired_show_commands"
            if not missing_command_records and not unpaired_show_records and not missing_guidance_records
            else "development_provider_examples_static_inventory_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the docs/development.md OpenAI hello_world "
            "and Anthropic circle_packing provider command markers, placeholder "
            "model-id guidance, paired show commands for both provider examples, "
            "explicit development run-name/overwrite markers, README provider "
            "model/failure guidance, docs-index routes, backend provider-lane "
            "and Gemini absence markers, status/paper sidecar anchors, and active "
            "TODO ownership. It does not claim live OpenAI or Anthropic model "
            "availability, credential-safe development provider smoke, account-"
            "specific model-id provenance, a CI development provider matrix, or "
            "owner review signoff."
        ),
    }


def validate_development_provider_example_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> DevelopmentProviderExampleBoundaryValidation:
    data, read_issues = _load_boundary(
        development_provider_example_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return DevelopmentProviderExampleBoundaryValidation(False, None, 0, 0, 0, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = development_provider_example_boundary_record(root)
    issues: list[DevelopmentProviderExampleBoundaryIssue] = []
    if data.get("schema") != DEVELOPMENT_PROVIDER_EXAMPLE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported development provider example boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "development provider examples must not claim live provider smoke"))
    for key in (
        "development_doc_path",
        "provider_example_count",
        "missing_command_count",
        "missing_command_records",
        "unpaired_show_count",
        "unpaired_show_records",
        "provider_example_records",
        "guidance_marker_count",
        "missing_guidance_marker_count",
        "missing_guidance_marker_records",
        "guidance_marker_records",
        "development_provider_example_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current development provider inputs"))
    if data.get("provider_example_count") != 2:
        issues.append(_issue("invalid_provider_example_count", "development guide should record two provider-backed examples"))
    if data.get("missing_command_count") != 0:
        issues.append(_issue("missing_development_provider_command", "development provider command markers are incomplete"))
    if data.get("unpaired_show_count") != 0:
        issues.append(_issue("invalid_unpaired_show_count", "development provider examples should have paired show commands"))
    if data.get("missing_guidance_marker_count") != 0:
        issues.append(_issue("missing_development_provider_guidance_marker", "development provider evidence anchors are incomplete"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "docs/development.md OpenAI hello_world" not in boundary_text
        or "paired show commands for both provider examples" not in boundary_text
        or "does not claim live OpenAI or Anthropic model availability" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate static development commands from live provider smoke"))
    return DevelopmentProviderExampleBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        provider_example_count=data.get("provider_example_count") if isinstance(data.get("provider_example_count"), int) else 0,
        missing_command_count=data.get("missing_command_count") if isinstance(data.get("missing_command_count"), int) else 0,
        unpaired_show_count=data.get("unpaired_show_count") if isinstance(data.get("unpaired_show_count"), int) else 0,
        guidance_marker_count=data.get("guidance_marker_count") if isinstance(data.get("guidance_marker_count"), int) else 0,
        missing_guidance_marker_count=data.get("missing_guidance_marker_count") if isinstance(data.get("missing_guidance_marker_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_development_provider_example_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_development_provider_example_boundary(boundary)
    lines = [
        "Development provider example boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| provider_example_count | {validation.provider_example_count} |",
        f"| missing_command_count | {validation.missing_command_count} |",
        f"| unpaired_show_count | {validation.unpaired_show_count} |",
        f"| guidance_marker_count | {validation.guidance_marker_count} |",
        f"| missing_guidance_marker_count | {validation.missing_guidance_marker_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _provider_record(text: str, spec: dict[str, str]) -> dict[str, Any]:
    return {
        "example_id": spec["example_id"],
        "provider": spec["provider"],
        "problem": spec["problem"],
        "placeholder": spec["placeholder"],
        "expected_run_dir": spec["expected_run_dir"],
        "command_marker": spec["command_marker"],
        "command_marker_status": (
            "command_marker_present" if spec["command_marker"] in text else "command_marker_missing"
        ),
        "show_marker": spec["show_marker"],
        "show_marker_status": (
            "show_marker_present" if spec["show_marker"] in text else "show_marker_missing"
        ),
    }


def _marker_record(record_id: str, path: str, text: str, marker: str) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "path": path,
        "required_marker": marker,
        "marker_status": "marker_present" if marker in text else "marker_missing",
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[DevelopmentProviderExampleBoundaryIssue]]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")]
    else:
        try:
            data = json.loads(Path(boundary).read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")]
    if isinstance(data, dict):
        return data, []
    return None, [_issue("invalid_shape", "development provider example boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[DevelopmentProviderExampleBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_required_evidence_field", f"missing required evidence fields: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_required_evidence_field", f"unknown required evidence fields: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[DevelopmentProviderExampleBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_missing_evidence_key", f"missing_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_missing_evidence_key", f"missing_evidence has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _issue(code: str, message: str) -> DevelopmentProviderExampleBoundaryIssue:
    return DevelopmentProviderExampleBoundaryIssue(code, message)
