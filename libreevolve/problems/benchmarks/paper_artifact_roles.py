from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PAPER_ARTIFACT_ROLE_SCHEMA = "libreevolve.alphaevolve_paper_artifact_roles.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION = "Acknowledgments and Author information"
EXPECTED_SOURCE_PAGE = 23
EXPECTED_ROLE_RECORDS = {
    "paper_figures": {
        "artifact_type": "figure_set",
        "role": "creator",
        "contributors": ("N.V.", "E.D.", "M.E.", "S.C.", "A.N.", "A.Z.W."),
        "required_source_phrase": "created the figures",
    },
    "accompanying_google_colab": {
        "artifact_type": "companion_notebook",
        "role": "assembler",
        "contributors": ("F.J.R.R.", "A.M.", "A.Z.W."),
        "required_source_phrase": "assembled the accompanying Google Colab",
    },
}
_ARTIFACT_ID_RE = re.compile(r"[a-z][a-z0-9_]{2,95}")


@dataclass(frozen=True)
class PaperArtifactRoleIssue:
    code: str
    message: str
    artifact_id: str | None = None


@dataclass(frozen=True)
class PaperArtifactRoleValidation:
    ok: bool
    artifact_count: int
    role_count: int
    issues: list[PaperArtifactRoleIssue]


def alphaevolve_paper_artifact_role_records() -> dict[str, Any]:
    return {
        "schema": PAPER_ARTIFACT_ROLE_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section": EXPECTED_SOURCE_SECTION,
        "source_pdf_page": EXPECTED_SOURCE_PAGE,
        "source_text_ref": (
            "AlphaEvolve PDF page 23 contribution sentences for figure creation "
            "and companion Google Colab assembly."
        ),
        "artifacts": [
            {
                "artifact_id": artifact_id,
                "artifact_type": expected["artifact_type"],
                "role": expected["role"],
                "contributors": list(expected["contributors"]),
                "source_phrase": expected["required_source_phrase"],
            }
            for artifact_id, expected in EXPECTED_ROLE_RECORDS.items()
        ],
    }


def validate_paper_artifact_roles(recordset: object | str | Path) -> PaperArtifactRoleValidation:
    data, read_issues = _load_recordset(recordset)
    if read_issues:
        return PaperArtifactRoleValidation(False, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[PaperArtifactRoleIssue] = []
    if data.get("schema") != PAPER_ARTIFACT_ROLE_SCHEMA:
        issues.append(PaperArtifactRoleIssue("invalid_schema", "unsupported paper artifact-role schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(PaperArtifactRoleIssue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section") != EXPECTED_SOURCE_SECTION:
        issues.append(PaperArtifactRoleIssue("invalid_source_section", "source_section must match the PDF contribution section"))
    if data.get("source_pdf_page") != EXPECTED_SOURCE_PAGE:
        issues.append(PaperArtifactRoleIssue("invalid_source_pdf_page", "source_pdf_page must identify page 23"))
    if not isinstance(data.get("source_text_ref"), str) or not data["source_text_ref"].strip():
        issues.append(PaperArtifactRoleIssue("missing_source_text_ref", "source_text_ref is required"))
    artifact_count, role_count = _validate_artifacts(data.get("artifacts"), issues)
    return PaperArtifactRoleValidation(
        ok=not issues,
        artifact_count=artifact_count,
        role_count=role_count,
        issues=issues,
    )


def render_paper_artifact_role_summary(recordset: dict[str, Any]) -> str:
    validation = validate_paper_artifact_roles(recordset)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve paper artifact roles",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| artifact_count | {validation.artifact_count} |",
        f"| role_count | {validation.role_count} |",
        f"| source_pdf_page | {recordset.get('source_pdf_page', '<unknown>')} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(
            f"- {issue.code}: {issue.message}"
            + (f" ({issue.artifact_id})" if issue.artifact_id else "")
            for issue in validation.issues
        )
    return "\n".join(lines)


def _load_recordset(recordset: object | str | Path) -> tuple[dict[str, Any] | None, list[PaperArtifactRoleIssue]]:
    if isinstance(recordset, dict):
        return dict(recordset), []
    if isinstance(recordset, (str, Path)):
        path = Path(recordset)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [PaperArtifactRoleIssue("read_error", f"failed to read paper artifact-role recordset: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [PaperArtifactRoleIssue("invalid_json", f"invalid paper artifact-role JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [PaperArtifactRoleIssue("invalid_shape", "paper artifact-role recordset must be a JSON object")]


def _validate_artifacts(value: object, issues: list[PaperArtifactRoleIssue]) -> tuple[int, int]:
    if not isinstance(value, list):
        issues.append(PaperArtifactRoleIssue("invalid_artifacts", "artifacts must be a list"))
        return 0, 0
    seen: set[str] = set()
    role_count = 0
    for artifact in value:
        if not isinstance(artifact, dict):
            issues.append(PaperArtifactRoleIssue("invalid_artifact", "artifact entries must be objects"))
            continue
        artifact_id = artifact.get("artifact_id")
        safe_id = artifact_id if isinstance(artifact_id, str) else None
        if safe_id is None or _ARTIFACT_ID_RE.fullmatch(safe_id) is None:
            issues.append(PaperArtifactRoleIssue("invalid_artifact_id", "artifact_id must be a safe snake_case id"))
            continue
        if safe_id in seen:
            issues.append(PaperArtifactRoleIssue("duplicate_artifact", "duplicate artifact_id", safe_id))
        seen.add(safe_id)
        expected = EXPECTED_ROLE_RECORDS.get(safe_id)
        if expected is None:
            issues.append(PaperArtifactRoleIssue("unknown_artifact", "artifact_id is not a required AlphaEvolve role record", safe_id))
            continue
        _validate_artifact_fields(artifact, safe_id, expected, issues)
        role_count += 1
    for artifact_id in EXPECTED_ROLE_RECORDS:
        if artifact_id not in seen:
            issues.append(PaperArtifactRoleIssue("missing_artifact", "required AlphaEvolve artifact-role record is missing", artifact_id))
    return len(value), role_count


def _validate_artifact_fields(
    artifact: dict[str, Any],
    artifact_id: str,
    expected: dict[str, Any],
    issues: list[PaperArtifactRoleIssue],
) -> None:
    if artifact.get("artifact_type") != expected["artifact_type"]:
        issues.append(PaperArtifactRoleIssue("invalid_artifact_type", "artifact_type does not match the paper role record", artifact_id))
    if artifact.get("role") != expected["role"]:
        issues.append(PaperArtifactRoleIssue("invalid_role", "role does not match the paper contribution wording", artifact_id))
    contributors = artifact.get("contributors")
    if not isinstance(contributors, list) or tuple(contributors) != expected["contributors"]:
        issues.append(PaperArtifactRoleIssue("invalid_contributors", "contributors must preserve the exact paper initials and order", artifact_id))
    source_phrase = artifact.get("source_phrase")
    required_phrase = expected["required_source_phrase"]
    if not isinstance(source_phrase, str) or required_phrase not in source_phrase:
        issues.append(PaperArtifactRoleIssue("missing_source_phrase", "source_phrase must preserve the paper contribution phrase", artifact_id))
