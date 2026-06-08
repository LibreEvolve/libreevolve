import json

from libreevolve.problems.benchmarks.paper_artifact_roles import (
    PAPER_ARTIFACT_ROLE_SCHEMA,
    alphaevolve_paper_artifact_role_records,
    render_paper_artifact_role_summary,
    validate_paper_artifact_roles,
)


def test_validate_paper_artifact_roles_accepts_alphaevolve_contribution_records():
    recordset = alphaevolve_paper_artifact_role_records()

    validation = validate_paper_artifact_roles(recordset)

    assert validation.ok is True
    assert validation.artifact_count == 2
    assert validation.role_count == 2
    assert validation.issues == []


def test_validate_paper_artifact_roles_loads_json_file(tmp_path):
    path = tmp_path / "artifact_roles.json"
    path.write_text(json.dumps(alphaevolve_paper_artifact_role_records()), encoding="utf-8")

    validation = validate_paper_artifact_roles(path)

    assert validation.ok is True


def test_validate_paper_artifact_roles_rejects_missing_and_wrong_contributors():
    recordset = alphaevolve_paper_artifact_role_records()
    recordset["artifacts"] = recordset["artifacts"][:1]
    recordset["artifacts"][0]["contributors"] = ["N.V.", "E.D."]

    validation = validate_paper_artifact_roles(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_contributors" in codes
    assert "missing_artifact" in codes


def test_validate_paper_artifact_roles_rejects_unknown_and_duplicate_artifacts():
    recordset = alphaevolve_paper_artifact_role_records()
    duplicate = dict(recordset["artifacts"][0])
    unknown = {
        "artifact_id": "appendix_tables",
        "artifact_type": "table_set",
        "role": "creator",
        "contributors": ["N.V."],
        "source_phrase": "created the tables",
    }
    recordset["artifacts"].extend([duplicate, unknown])

    validation = validate_paper_artifact_roles(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "duplicate_artifact" in codes
    assert "unknown_artifact" in codes


def test_validate_paper_artifact_roles_rejects_source_metadata_drift():
    recordset = alphaevolve_paper_artifact_role_records()
    recordset["schema"] = "wrong"
    recordset["source_pdf_page"] = 22
    recordset["artifacts"][1]["source_phrase"] = "assembled a notebook"

    validation = validate_paper_artifact_roles(recordset)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_schema" in codes
    assert "invalid_source_pdf_page" in codes
    assert "missing_source_phrase" in codes


def test_render_paper_artifact_role_summary_reports_shape():
    summary = render_paper_artifact_role_summary(alphaevolve_paper_artifact_role_records())

    assert "AlphaEvolve paper artifact roles" in summary
    assert "| schema_status | ok |" in summary
    assert "| artifact_count | 2 |" in summary
    assert "| role_count | 2 |" in summary
    assert "| source_pdf_page | 23 |" in summary
