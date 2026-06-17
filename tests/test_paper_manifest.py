import csv
import hashlib
import json
import stat
import subprocess
from io import BytesIO
from types import SimpleNamespace
from pathlib import Path

from pypdf import PdfWriter

import libreevolve.tools.paper_manifest as paper_manifest
from libreevolve.problems.benchmarks.paper_source_versions import (
    alphaevolve_source_pdf_version_manifest_record,
    alphaevolve_source_pdf_version_record,
)
from libreevolve.problems.benchmarks.paper_source_rights import (
    alphaevolve_source_pdf_rights_manifest_record,
)
from libreevolve.problems.benchmarks.paper_source_identity import (
    paper_source_identity_manifest_record,
)
from libreevolve.problems.benchmarks.companion_sources import (
    alphaevolve_companion_source_manifest_record,
)
from libreevolve.problems.benchmarks.paper_artifact_roles import (
    alphaevolve_paper_artifact_linkage_record,
    alphaevolve_paper_artifact_role_records,
)
from libreevolve.problems.benchmarks.follow_on_sources import (
    alphaevolve_follow_on_repository_rights_manifest_record,
    alphaevolve_follow_on_runtime_absence_manifest_record,
    alphaevolve_follow_on_source_manifest_record,
    alphaevolve_follow_on_tao_blog_manifest_record,
)
from libreevolve.problems.benchmarks.theoretical_cs_sources import (
    alphaevolve_theoretical_cs_source_manifest_record,
)
from libreevolve.problems.benchmarks.official_deepmind_blog import (
    alphaevolve_official_blog_manifest_record,
)
from libreevolve.problems.benchmarks.appendix_a_matrix_registry import (
    appendix_a_matrix_baseline_citation_boundary_from_builtin_citations,
    appendix_a_matrix_curation_record,
    appendix_a_matrix_excluded_target_curation_boundary_record,
    appendix_a_matrix_local_resource_frontier_record,
    appendix_a_matrix_resource_frontier_record,
    appendix_a_matrix_row_note_artifact_boundary_from_records,
    appendix_a_matrix_subset_scope_artifact_boundary_from_records,
)
from libreevolve.problems.benchmarks.matrix_exhibits import (
    matrix_rank_table_artifact_boundary_from_builtin_exhibit,
)
from libreevolve.problems.benchmarks.matrix_results import (
    matrix_headline_historicity_runtime_boundary_from_builtin_evidence,
)
from libreevolve.tools.paper_manifest import main, rehydrate_paper_cache, validate_paper_manifest

PARTIAL_FIXTURE_STATUS = (
    "Partially implemented: `libreevolve/core/loop.py` fixture status; no full paper behavior."
)


def _write_manifest(root, rows):
    papers = root / "papers"
    papers.mkdir(exist_ok=True)
    (root / "README.md").write_text(
        f"LibreEvolve is informed by a local cache of {len(rows)} papers.\n",
        encoding="utf-8",
    )
    (papers / "README.md").write_text(
        f"This directory is the paper-cache index. On the working machine it contains {len(rows)} papers.\n",
        encoding="utf-8",
    )
    (papers / "download_manifest.json").write_text(
        json.dumps(rows, indent=2),
        encoding="utf-8",
    )
    with (papers / "download_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "title", "url", "file", "ok", "bytes", "sha256", "message"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_math_outcome_boundary_sidecars(root):
    sidecars = {
        paper_manifest.MATH_OUTCOME_BOUNDARY_FILE: paper_manifest.alphaevolve_math_outcome_boundary(),
        paper_manifest.MATH_STARTING_CONSTRUCTION_BOUNDARY_FILE: paper_manifest.alphaevolve_math_starting_construction_boundary(),
        paper_manifest.MATH_HEURISTIC_HANDOFF_BOUNDARY_FILE: paper_manifest.alphaevolve_math_heuristic_handoff_boundary(),
        paper_manifest.MATH_HEURISTIC_STAGE_SEQUENCE_BOUNDARY_FILE: paper_manifest.alphaevolve_math_heuristic_stage_sequence_boundary(),
    }
    for relative_path, boundary in sidecars.items():
        (root / relative_path).write_text(
            json.dumps(boundary, indent=2),
            encoding="utf-8",
        )


def _write_status_table(root, row_ids):
    rows = "\n".join(
        f"| {row_id} | Paper {index} | Primary specification target | "
        f"{PARTIAL_FIXTURE_STATUS} |"
        for index, row_id in enumerate(row_ids, start=1)
    )
    (root / "papers" / "README.md").write_text(
        "This directory is the paper-cache index. On the working machine it contains "
        f"{len(row_ids)} papers.\n\n"
        "## Implementation status\n\n"
        "| ID | Title | Role | Current LibreEvolve status |\n"
        "|---|---|---|---|\n"
        f"{rows}\n",
        encoding="utf-8",
    )


def _write_status_fixture_artifact(root):
    artifact_path = root / "libreevolve" / "core" / "loop.py"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text("# loop fixture\n", encoding="utf-8")


def _append_todo_coverage_table(root, rows):
    table_rows = "\n".join(
        f"| {row_id} | {active_cell} | {completed_cell} |"
        for row_id, active_cell, completed_cell in rows
    )
    path = root / "papers" / "README.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text(
        existing.rstrip()
        + "\n\n"
        + "## TODO coverage cross-references\n\n"
        + "| ID | Active gap evidence | Completed/grouped evidence |\n"
        + "|---|---|---|\n"
        + f"{table_rows}\n",
        encoding="utf-8",
    )


def _write_active_todo_ledgers(root, row_id, *, paths=None):
    paths = set(paths or paper_manifest.ACTIVE_TODO_LEDGER_PATHS)
    for relative_path in paper_manifest.ACTIVE_TODO_LEDGER_PATHS:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if relative_path in paths:
            path.write_text(
                f"- [ ] Track source-specific gap for `{row_id}`.\n"
                "  - Current gap: temporary test ledger entry for `libreevolve/core/loop.py`.\n"
                "  - Required result: keep the temporary fixture source-specific.\n",
                encoding="utf-8",
            )
        else:
            path.write_text("- [ ] Track unrelated source.\n", encoding="utf-8")


def _active_todo_cell(*paths):
    return "; ".join(f"`{path}`" for path in paths)


def _write_completed_todo_ledger(root, path="docs/todo/Completed/code.md", row_id="2506.13131"):
    completed_path = root / path
    completed_path.parent.mkdir(parents=True, exist_ok=True)
    completed_path.write_text(
        f"- [x] Completed fixture evidence for `{row_id}` in `libreevolve/core/loop.py`.\n",
        encoding="utf-8",
    )
    return f"`{path}`"


def _valid_pdf_bytes(extra=b""):
    buffer = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(buffer)
    return buffer.getvalue() + extra


def _row(
    root,
    *,
    row_id="2506.13131",
    title="AlphaEvolve",
    url="https://arxiv.org/pdf/2506.13131.pdf",
    file="papers/2506.13131__AlphaEvolve.pdf",
    message="downloaded",
    ok=True,
    content=None,
    sha256=None,
    bytes_value=None,
):
    content = _valid_pdf_bytes() if content is None else content
    paper_path = root / file
    paper_path.parent.mkdir(exist_ok=True)
    paper_path.write_bytes(content)
    return {
        "id": row_id,
        "title": title,
        "url": url,
        "file": file,
        "ok": ok,
        "bytes": len(content) if bytes_value is None else bytes_value,
        "sha256": hashlib.sha256(content).hexdigest() if sha256 is None else sha256,
        "message": message,
    }


def _follow_on_row():
    record = alphaevolve_follow_on_source_manifest_record()["sources"][0]["source_record"]
    cache = record["paper"]["local_cache"]
    return {
        "id": record["paper"]["arxiv_id"],
        "title": "Mathematical_exploration_and_discovery_at_scale",
        "url": record["paper"]["floating_pdf_url"],
        "file": cache["file"],
        "ok": True,
        "bytes": cache["bytes"],
        "sha256": cache["sha256"],
        "message": "downloaded",
    }


def test_validate_paper_manifest_accepts_matching_local_pdf(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    assert report.ok is True
    assert report.row_count == 1
    assert report.local_present_count == 1
    assert report.availability[0].local_status == "present"
    assert report.availability[0].download_ok is True
    assert report.issues == []


def test_validate_paper_manifest_accepts_matching_source_version_manifest(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row, _follow_on_row()])
    (tmp_path / "papers" / "source_versions.json").write_text(
        json.dumps(alphaevolve_source_pdf_version_manifest_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_source_version_manifest_row_drift(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded", "sha256": "0" * 64})
    _write_manifest(tmp_path, [row])
    (tmp_path / "papers" / "source_versions.json").write_text(
        json.dumps(alphaevolve_source_pdf_version_manifest_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "alphaevolve_source_pdf_version_manifest_sha256_mismatch" in codes


def test_validate_paper_manifest_accepts_arxiv_abstract_snapshot(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    source_root = Path(__file__).resolve().parents[1]
    (tmp_path / "papers" / "arxiv_abstract_2506.13131v1.html").write_bytes(
        (source_root / "papers" / "arxiv_abstract_2506.13131v1.html").read_bytes()
    )
    sidecar = tmp_path / paper_manifest.ARXIV_ABSTRACT_SNAPSHOT_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.alphaevolve_arxiv_abstract_snapshot_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_arxiv_abstract_snapshot_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    (tmp_path / "papers" / "arxiv_abstract_2506.13131v1.html").write_text(
        "not the abstract page",
        encoding="utf-8",
    )
    record = paper_manifest.alphaevolve_arxiv_abstract_snapshot_record()
    record["html_snapshot"]["bytes"] = 1
    record["normalized_metadata"]["subject_codes"] = ["cs.AI"]
    record["missing_evidence"]["automated_live_refresh_ci_gate"] = "recorded"
    sidecar = tmp_path / paper_manifest.ARXIV_ABSTRACT_SNAPSHOT_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_arxiv_abstract_snapshot_invalid_html_snapshot_bytes" in codes
    assert "alphaevolve_arxiv_abstract_snapshot_invalid_html_artifact_sha256" in codes
    assert "alphaevolve_arxiv_abstract_snapshot_invalid_metadata_subject_codes" in codes
    assert (
        "alphaevolve_arxiv_abstract_snapshot_invalid_missing_evidence_automated_live_refresh_ci_gate"
        in codes
    )


def test_validate_paper_manifest_requires_arxiv_abstract_snapshot_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_arxiv_abstract_snapshot_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_current_version_boundary(
    tmp_path,
):
    source_root = Path(__file__).resolve().parents[1]
    alphaevolve_pdf_bytes = (source_root / "papers" / "2506.13131__AlphaEvolve.pdf").read_bytes()
    row = _row(tmp_path, content=alphaevolve_pdf_bytes)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_CURRENT_VERSION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.alphaevolve_current_version_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_current_version_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.alphaevolve_current_version_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "current_version_refresh_gate_ready"
    record["current_abs_snapshot"]["resolved_current_version"] = 2
    record["floating_pdf_snapshot"]["floating_pdf_matches_cached_pdf"] = False
    record["missing_evidence"]["automated_current_version_refresh_gate"] = "recorded"
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_CURRENT_VERSION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_current_version_boundary_claim_ready_overclaim" in codes
    assert "alphaevolve_current_version_boundary_invalid_boundary_status" in codes
    assert (
        "alphaevolve_current_version_boundary_invalid_current_abs_resolved_current_version"
        in codes
    )
    assert (
        "alphaevolve_current_version_boundary_invalid_floating_pdf_floating_pdf_matches_cached_pdf"
        in codes
    )
    assert "alphaevolve_current_version_boundary_invalid_floating_pdf_artifact_sha256" in codes
    assert (
        "alphaevolve_current_version_boundary_invalid_missing_evidence_automated_current_version_refresh_gate"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_current_version_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_current_version_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_cached_pdf_header_consistency_boundary(
    tmp_path,
):
    source_root = Path(__file__).resolve().parents[1]
    alphaevolve_pdf_bytes = (source_root / "papers" / "2506.13131__AlphaEvolve.pdf").read_bytes()
    row = _row(tmp_path, content=alphaevolve_pdf_bytes)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_CACHED_PDF_HEADER_CONSISTENCY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.alphaevolve_cached_pdf_header_consistency_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_cached_pdf_header_consistency_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.alphaevolve_cached_pdf_header_consistency_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "cached_pdf_header_refresh_gate_ready"
    record["first_page_extraction"]["required_markers"]["has_arxiv_header"] = False
    record["missing_evidence"]["automated_cached_pdf_header_refresh_gate"] = "recorded"
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_CACHED_PDF_HEADER_CONSISTENCY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_cached_pdf_header_consistency_boundary_claim_ready_overclaim" in codes
    assert "alphaevolve_cached_pdf_header_consistency_boundary_invalid_boundary_status" in codes
    assert (
        "alphaevolve_cached_pdf_header_consistency_boundary_invalid_pdf_artifact_file_sha256"
        in codes
    )
    assert (
        "alphaevolve_cached_pdf_header_consistency_boundary_invalid_first_page_extraction_required_markers"
        in codes
    )
    assert (
        "alphaevolve_cached_pdf_header_consistency_boundary_invalid_missing_evidence_automated_cached_pdf_header_refresh_gate"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_cached_pdf_header_consistency_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_cached_pdf_header_consistency_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_metadata_extraction_script_boundary(
    tmp_path,
):
    source_root = Path(__file__).resolve().parents[1]
    alphaevolve_pdf_bytes = (source_root / "papers" / "2506.13131__AlphaEvolve.pdf").read_bytes()
    row = _row(tmp_path, content=alphaevolve_pdf_bytes)
    _write_manifest(tmp_path, [row])
    (tmp_path / "libreevolve" / "tools").mkdir(parents=True)
    (tmp_path / "libreevolve" / "tools" / "alphaevolve_source_metadata.py").write_bytes(
        (source_root / "libreevolve" / "tools" / "alphaevolve_source_metadata.py").read_bytes()
    )
    for relative_path in (
        "papers/arxiv_abstract_2506.13131v1.html",
        "papers/alphaevolve_datacite_full_response_boundary.json",
        "papers/alphaevolve_license_page.html",
        "papers/alphaevolve_tex_source_archive.tar.gz",
    ):
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((source_root / relative_path).read_bytes())
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_METADATA_EXTRACTION_SCRIPT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.alphaevolve_metadata_extraction_script_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_metadata_extraction_script_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.alphaevolve_metadata_extraction_script_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "metadata_refresh_gate_ready"
    record["script_artifact"]["sha256"] = "0" * 64
    record["missing_evidence"]["automated_live_refresh_ci_gate"] = "recorded"
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_METADATA_EXTRACTION_SCRIPT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_metadata_extraction_script_boundary_claim_ready_overclaim" in codes
    assert "alphaevolve_metadata_extraction_script_boundary_invalid_boundary_status" in codes
    assert "alphaevolve_metadata_extraction_script_boundary_invalid_script_artifact_sha256" in codes
    assert (
        "alphaevolve_metadata_extraction_script_boundary_invalid_missing_evidence_automated_live_refresh_ci_gate"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_metadata_extraction_script_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_metadata_extraction_script_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_source_refresh_gate_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    source_root = Path(__file__).resolve().parents[1]
    script_target = tmp_path / "libreevolve" / "tools" / "alphaevolve_source_refresh_gate.py"
    workflow_target = tmp_path / ".github" / "workflows" / "tests.yml"
    script_target.parent.mkdir(parents=True)
    workflow_target.parent.mkdir(parents=True)
    script_target.write_bytes(
        (source_root / "libreevolve" / "tools" / "alphaevolve_source_refresh_gate.py").read_bytes()
    )
    workflow_target.write_text(
        (source_root / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_SOURCE_REFRESH_GATE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.alphaevolve_source_refresh_gate_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_source_refresh_gate_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.alphaevolve_source_refresh_gate_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "source_refresh_gate_publication_ready"
    record["script_artifact"]["sha256"] = "0" * 64
    record["workflow_artifact"]["schedule_cron"] = "0 0 * * *"
    record["workflow_artifact"]["report_artifact_name"] = "wrong-report"
    record["archived_outcome_artifact"]["run_mode"] = "provided_snapshots"
    record["missing_evidence"]["scheduled_ci_refresh_run_history"] = "recorded"
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_SOURCE_REFRESH_GATE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_source_refresh_gate_boundary_claim_ready_overclaim" in codes
    assert "alphaevolve_source_refresh_gate_boundary_invalid_boundary_status" in codes
    assert "alphaevolve_source_refresh_gate_boundary_invalid_script_artifact_sha256" in codes
    assert "alphaevolve_source_refresh_gate_boundary_invalid_workflow_artifact_schedule_cron" in codes
    assert "alphaevolve_source_refresh_gate_boundary_invalid_workflow_artifact_report_artifact_name" in codes
    assert "alphaevolve_source_refresh_gate_boundary_invalid_archived_outcome_artifact_run_mode" in codes
    assert (
        "alphaevolve_source_refresh_gate_boundary_invalid_missing_evidence_scheduled_ci_refresh_run_history"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_source_refresh_gate_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_source_refresh_gate_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_source_refresh_run_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    source_root = Path(__file__).resolve().parents[1]
    script_target = tmp_path / "libreevolve" / "tools" / "alphaevolve_source_refresh_gate.py"
    script_target.parent.mkdir(parents=True)
    script_target.write_bytes(
        (source_root / "libreevolve" / "tools" / "alphaevolve_source_refresh_gate.py").read_bytes()
    )
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_SOURCE_REFRESH_RUN_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.alphaevolve_source_refresh_run_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_source_refresh_run_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.alphaevolve_source_refresh_run_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "source_refresh_run_publication_ready"
    record["run_report"]["checks"][0]["observed"]["sha256"] = "0" * 64
    record["missing_evidence"]["scheduled_ci_refresh_run_history"] = "recorded"
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_SOURCE_REFRESH_RUN_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_source_refresh_run_boundary_claim_ready_overclaim" in codes
    assert "alphaevolve_source_refresh_run_boundary_invalid_boundary_status" in codes
    assert "alphaevolve_source_refresh_run_boundary_invalid_run_report_sha256" in codes
    assert (
        "alphaevolve_source_refresh_run_boundary_invalid_versioned_abstract_observed_sha256"
        in codes
    )
    assert (
        "alphaevolve_source_refresh_run_boundary_invalid_missing_evidence_scheduled_ci_refresh_run_history"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_source_refresh_run_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_source_refresh_run_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_source_refresh_promotion_boundary(
    tmp_path,
):
    source_root = Path(__file__).resolve().parents[1]
    alphaevolve_pdf_bytes = (source_root / "papers" / "2506.13131__AlphaEvolve.pdf").read_bytes()
    row = _row(tmp_path, content=alphaevolve_pdf_bytes)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.alphaevolve_source_refresh_promotion_boundary_record()
    linked_paths = {
        record["central_refresh_gate"]["path"],
        record["central_refresh_gate"]["workflow_path"],
        record["central_refresh_gate"]["archived_manual_run_path"],
    }
    for source in record["source_sidecar_map"]:
        linked_paths.update(source["sidecars"])
    for relative_path in linked_paths:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((source_root / relative_path).read_bytes())
    for relative_path in (
        "libreevolve/tools/alphaevolve_source_refresh_gate.py",
        "papers/arxiv_abstract_2506.13131v1.html",
        "papers/alphaevolve_license_page.html",
        "papers/alphaevolve_tex_source_archive.tar.gz",
    ):
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((source_root / relative_path).read_bytes())
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_SOURCE_REFRESH_PROMOTION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_source_refresh_promotion_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.alphaevolve_source_refresh_promotion_boundary_record()
    record["claim_ready"] = True
    record["promotion_policy"] = "all_sidecars_individually_refresh_ready"
    record["source_sidecar_map"][0]["promotion_status"] = "refresh_ready"
    record["missing_evidence"]["scheduled_ci_refresh_run_history"] = "recorded"
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_SOURCE_REFRESH_PROMOTION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_source_refresh_promotion_boundary_claim_ready_overclaim" in codes
    assert "alphaevolve_source_refresh_promotion_boundary_invalid_promotion_policy" in codes
    assert "alphaevolve_source_refresh_promotion_boundary_invalid_promotion_status" in codes
    assert (
        "alphaevolve_source_refresh_promotion_boundary_invalid_missing_evidence_scheduled_ci_refresh_run_history"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_source_refresh_promotion_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_source_refresh_promotion_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_raw_http_headers_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_RAW_HTTP_HEADERS_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.alphaevolve_raw_http_headers_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_raw_http_headers_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.alphaevolve_raw_http_headers_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "raw_http_headers_refresh_gate_ready"
    record["header_snapshots"]["floating_pdf"]["raw_header_lines"] = []
    record["missing_evidence"]["automated_header_refresh_gate"] = "recorded"
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_RAW_HTTP_HEADERS_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_raw_http_headers_boundary_claim_ready_overclaim" in codes
    assert "alphaevolve_raw_http_headers_boundary_invalid_boundary_status" in codes
    assert "alphaevolve_raw_http_headers_boundary_invalid_floating_pdf_raw_header_lines" in codes
    assert (
        "alphaevolve_raw_http_headers_boundary_invalid_missing_evidence_automated_header_refresh_gate"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_raw_http_headers_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_raw_http_headers_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_datacite_doi_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_DATACITE_DOI_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.alphaevolve_datacite_doi_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_datacite_doi_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.alphaevolve_datacite_doi_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "full_source_refresh_gate_ready"
    record["datacite_api_snapshot"]["creator_count"] = 17
    record["missing_evidence"]["datacite_refresh_gate"] = "recorded"
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_DATACITE_DOI_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_datacite_doi_boundary_claim_ready_overclaim" in codes
    assert "alphaevolve_datacite_doi_boundary_invalid_boundary_status" in codes
    assert "alphaevolve_datacite_doi_boundary_invalid_snapshot_creator_count" in codes
    assert (
        "alphaevolve_datacite_doi_boundary_invalid_missing_evidence_datacite_refresh_gate"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_datacite_doi_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_datacite_doi_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_datacite_full_response_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_DATACITE_FULL_RESPONSE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.alphaevolve_datacite_full_response_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_datacite_full_response_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.alphaevolve_datacite_full_response_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "datacite_refresh_gate_ready"
    record["raw_response_body"] = "{}"
    record["missing_evidence"]["automated_datacite_refresh_gate"] = "recorded"
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_DATACITE_FULL_RESPONSE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_datacite_full_response_boundary_claim_ready_overclaim" in codes
    assert "alphaevolve_datacite_full_response_boundary_invalid_boundary_status" in codes
    assert "alphaevolve_datacite_full_response_boundary_invalid_raw_response_body_sha256" in codes
    assert (
        "alphaevolve_datacite_full_response_boundary_invalid_missing_evidence_automated_datacite_refresh_gate"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_datacite_full_response_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_datacite_full_response_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_doi_landing_resolution_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_DOI_LANDING_RESOLUTION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.alphaevolve_doi_landing_resolution_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_doi_landing_resolution_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.alphaevolve_doi_landing_resolution_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "doi_resolution_refresh_gate_ready"
    record["doi_redirect"]["location"] = "https://example.invalid/"
    record["missing_evidence"]["automated_doi_resolution_refresh_gate"] = "recorded"
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_DOI_LANDING_RESOLUTION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_doi_landing_resolution_boundary_claim_ready_overclaim" in codes
    assert "alphaevolve_doi_landing_resolution_boundary_invalid_boundary_status" in codes
    assert "alphaevolve_doi_landing_resolution_boundary_invalid_doi_redirect_location" in codes
    assert (
        "alphaevolve_doi_landing_resolution_boundary_invalid_missing_evidence_automated_doi_resolution_refresh_gate"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_doi_landing_resolution_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_doi_landing_resolution_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_tex_source_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_TEX_SOURCE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.alphaevolve_tex_source_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_tex_source_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.alphaevolve_tex_source_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "full_tex_source_archive_refresh_gate_ready"
    record["tex_eprint_snapshot"]["response_sha256"] = "0" * 64
    record["missing_evidence"]["tex_source_refresh_gate"] = "recorded"
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_TEX_SOURCE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_tex_source_boundary_claim_ready_overclaim" in codes
    assert "alphaevolve_tex_source_boundary_invalid_boundary_status" in codes
    assert "alphaevolve_tex_source_boundary_invalid_snapshot_response_sha256" in codes
    assert (
        "alphaevolve_tex_source_boundary_invalid_missing_evidence_tex_source_refresh_gate"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_tex_source_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_tex_source_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_tex_archive_retention_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    papers_dir = tmp_path / "papers"
    source_root = Path(__file__).resolve().parents[1]
    (papers_dir / "alphaevolve_tex_source_archive.tar.gz").write_bytes(
        (source_root / "papers" / "alphaevolve_tex_source_archive.tar.gz").read_bytes()
    )
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_TEX_ARCHIVE_RETENTION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.alphaevolve_tex_archive_retention_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_tex_archive_retention_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    papers_dir = tmp_path / "papers"
    (papers_dir / "alphaevolve_tex_source_archive.tar.gz").write_bytes(b"not a tarball")
    record = paper_manifest.alphaevolve_tex_archive_retention_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "tex_archive_refresh_gate_ready"
    record["archive_member_inventory"]["member_count"] = 1
    record["missing_evidence"]["tex_source_refresh_gate"] = "recorded"
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_TEX_ARCHIVE_RETENTION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_tex_archive_retention_boundary_claim_ready_overclaim" in codes
    assert "alphaevolve_tex_archive_retention_boundary_invalid_boundary_status" in codes
    assert "alphaevolve_tex_archive_retention_boundary_invalid_archive_member_inventory_member_count" in codes
    assert "alphaevolve_tex_archive_retention_boundary_invalid_archive_artifact_sha256" in codes
    assert (
        "alphaevolve_tex_archive_retention_boundary_invalid_missing_evidence_tex_source_refresh_gate"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_tex_archive_retention_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_tex_archive_retention_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_license_page_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_LICENSE_PAGE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.alphaevolve_license_page_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_license_page_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.alphaevolve_license_page_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "license_page_full_refresh_gate_ready"
    record["license_page_snapshot"]["response_bytes"] = 1
    record["missing_evidence"]["license_page_refresh_gate"] = "recorded"
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_LICENSE_PAGE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_license_page_boundary_claim_ready_overclaim" in codes
    assert "alphaevolve_license_page_boundary_invalid_boundary_status" in codes
    assert "alphaevolve_license_page_boundary_invalid_snapshot_response_bytes" in codes
    assert (
        "alphaevolve_license_page_boundary_invalid_missing_evidence_license_page_refresh_gate"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_license_page_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_license_page_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_license_page_html_retention_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    papers_dir = tmp_path / "papers"
    source_root = Path(__file__).resolve().parents[1]
    (papers_dir / "alphaevolve_license_page.html").write_bytes(
        (source_root / "papers" / "alphaevolve_license_page.html").read_bytes()
    )
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_LICENSE_PAGE_HTML_RETENTION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.alphaevolve_license_page_html_retention_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_license_page_html_retention_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    papers_dir = tmp_path / "papers"
    (papers_dir / "alphaevolve_license_page.html").write_text("not the license page", encoding="utf-8")
    record = paper_manifest.alphaevolve_license_page_html_retention_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "license_page_refresh_gate_ready"
    record["html_content_markers"]["has_license_title"] = False
    record["missing_evidence"]["license_page_refresh_gate"] = "recorded"
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_LICENSE_PAGE_HTML_RETENTION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_license_page_html_retention_boundary_claim_ready_overclaim" in codes
    assert "alphaevolve_license_page_html_retention_boundary_invalid_boundary_status" in codes
    assert "alphaevolve_license_page_html_retention_boundary_invalid_html_artifact_sha256" in codes
    assert "alphaevolve_license_page_html_retention_boundary_invalid_html_content_marker_has_license_title" in codes
    assert (
        "alphaevolve_license_page_html_retention_boundary_invalid_missing_evidence_license_page_refresh_gate"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_license_page_html_retention_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_license_page_html_retention_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_matching_source_identity_manifest(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row, _follow_on_row()])
    (tmp_path / "papers" / "row_identity.json").write_text(
        json.dumps(paper_source_identity_manifest_record([row, _follow_on_row()]), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_source_identity_manifest_row_drift(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    identity_record = paper_source_identity_manifest_record([row])
    identity_record["sources"][0]["file_source_id"] = "2506.99999"
    (tmp_path / "papers" / "row_identity.json").write_text(
        json.dumps(identity_record, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "paper_source_identity_file_source_id_mismatch" in codes
    assert "paper_source_identity_manifest_file_source_id_mismatch" in codes


def test_validate_paper_manifest_accepts_matching_source_rights_manifest(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    (tmp_path / "papers" / "source_rights.json").write_text(
        json.dumps(alphaevolve_source_pdf_rights_manifest_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_source_rights_manifest_policy_drift(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    rights_record = alphaevolve_source_pdf_rights_manifest_record()
    rights_record["sources"][0]["paper_derived_artifact_policy"][
        "reproduction_policy"
    ] = "free_reuse"
    rights_record["sources"][0]["paper_derived_artifact_policy"][
        "publication_ready_without_rights_review"
    ] = True
    (tmp_path / "papers" / "source_rights.json").write_text(
        json.dumps(rights_record, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "alphaevolve_source_pdf_rights_manifest_invalid_reproduction_policy" in codes
    assert (
        "alphaevolve_source_pdf_rights_manifest_invalid_publication_ready_without_rights_review"
        in codes
    )


def test_validate_paper_manifest_accepts_matching_companion_source_manifest(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    (tmp_path / "papers" / "companion_sources.json").write_text(
        json.dumps(alphaevolve_companion_source_manifest_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_companion_source_manifest_drift(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    companion_record = alphaevolve_companion_source_manifest_record()
    companion_record["sources"][0]["source_record"]["notebook"]["sha256"] = "0" * 64
    (tmp_path / "papers" / "companion_sources.json").write_text(
        json.dumps(companion_record, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "alphaevolve_companion_source_manifest_invalid_notebook_sha256" in codes


def test_validate_paper_manifest_accepts_committed_paper_artifact_role_sidecars(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    roles = alphaevolve_paper_artifact_role_records()
    (tmp_path / paper_manifest.PAPER_ARTIFACT_ROLES_FILE).write_text(
        json.dumps(roles, indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.PAPER_ARTIFACT_LINKAGE_FILE).write_text(
        json.dumps(alphaevolve_paper_artifact_linkage_record(roles), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_paper_artifact_role_sidecar_drift(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    roles = alphaevolve_paper_artifact_role_records()
    roles["artifacts"][0]["contributors"] = ["N.V."]
    (tmp_path / paper_manifest.PAPER_ARTIFACT_ROLES_FILE).write_text(
        json.dumps(roles, indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.PAPER_ARTIFACT_LINKAGE_FILE).write_text(
        json.dumps(alphaevolve_paper_artifact_linkage_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "alphaevolve_paper_artifact_roles_invalid_contributors" in codes


def test_validate_paper_manifest_rejects_paper_artifact_linkage_sidecar_drift(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    roles = alphaevolve_paper_artifact_role_records()
    linkage = alphaevolve_paper_artifact_linkage_record(roles)
    linkage["artifact_linkages"][0]["artifact_availability"] = "linked"
    (tmp_path / paper_manifest.PAPER_ARTIFACT_ROLES_FILE).write_text(
        json.dumps(roles, indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.PAPER_ARTIFACT_LINKAGE_FILE).write_text(
        json.dumps(linkage, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "alphaevolve_paper_artifact_linkage_missing_linked_artifacts" in codes


def test_validate_paper_manifest_requires_paper_artifact_role_sidecars_at_repo_root(
    tmp_path,
    monkeypatch,
):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "alphaevolve_paper_artifact_roles_manifest_missing" in codes
    assert "alphaevolve_paper_artifact_linkage_manifest_missing" in codes


def test_validate_paper_manifest_accepts_matching_follow_on_source_manifest(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row, _follow_on_row()])
    (tmp_path / "papers" / "follow_on_sources.json").write_text(
        json.dumps(alphaevolve_follow_on_source_manifest_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_follow_on_source_manifest_drift(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row, _follow_on_row()])
    follow_on_record = alphaevolve_follow_on_source_manifest_record()
    follow_on_record["sources"][0]["source_record"]["repository"]["commit"] = "0" * 40
    (tmp_path / "papers" / "follow_on_sources.json").write_text(
        json.dumps(follow_on_record, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "alphaevolve_follow_on_source_manifest_repository_commit_drift" in codes


def test_validate_paper_manifest_accepts_matching_follow_on_repository_rights_manifest(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    (tmp_path / "papers" / "follow_on_repository_rights.json").write_text(
        json.dumps(alphaevolve_follow_on_repository_rights_manifest_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_follow_on_repository_rights_manifest_drift(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    rights_record = alphaevolve_follow_on_repository_rights_manifest_record()
    rights_record["sources"][0]["repository_rights_record"]["rights"]["software_license"] = "MIT"
    (tmp_path / "papers" / "follow_on_repository_rights.json").write_text(
        json.dumps(rights_record, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "alphaevolve_follow_on_repository_rights_manifest_invalid_repository_rights_software_license" in codes


def test_validate_paper_manifest_accepts_matching_follow_on_runtime_absence_manifest(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    (tmp_path / "papers" / "follow_on_runtime_absence.json").write_text(
        json.dumps(alphaevolve_follow_on_runtime_absence_manifest_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_follow_on_runtime_absence_manifest_drift(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    runtime_record = alphaevolve_follow_on_runtime_absence_manifest_record()
    runtime_record["sources"][0]["runtime_absence_record"]["runtime_boundary"][
        "alphaevolve_runtime_available"
    ] = True
    (tmp_path / "papers" / "follow_on_runtime_absence.json").write_text(
        json.dumps(runtime_record, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "alphaevolve_follow_on_runtime_absence_manifest_runtime_absence_runtime_available_overclaim" in codes


def test_validate_paper_manifest_accepts_matching_follow_on_tao_blog_manifest(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    (tmp_path / "papers" / "follow_on_tao_blog.json").write_text(
        json.dumps(alphaevolve_follow_on_tao_blog_manifest_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_follow_on_tao_blog_manifest_drift(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    blog_record = alphaevolve_follow_on_tao_blog_manifest_record()
    blog_record["sources"][0]["source_record"]["claim_boundary"][
        "blog_commentary_secondary"
    ] = False
    (tmp_path / "papers" / "follow_on_tao_blog.json").write_text(
        json.dumps(blog_record, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "alphaevolve_follow_on_tao_blog_manifest_invalid_tao_blog_claim_boundary_blog_commentary_secondary" in codes


def test_validate_paper_manifest_accepts_matching_theoretical_cs_source_manifest(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    (tmp_path / "papers" / "theoretical_cs_sources.json").write_text(
        json.dumps(alphaevolve_theoretical_cs_source_manifest_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_theoretical_cs_source_manifest_drift(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    theoretical_record = alphaevolve_theoretical_cs_source_manifest_record()
    theoretical_record["sources"][0]["source_record"]["claim_boundaries"][
        "not_formal_theorem_prover"
    ] = False
    (tmp_path / "papers" / "theoretical_cs_sources.json").write_text(
        json.dumps(theoretical_record, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "alphaevolve_theoretical_cs_source_manifest_invalid_claim_boundaries_not_formal_theorem_prover" in codes


def test_validate_paper_manifest_accepts_matching_official_blog_manifest(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    (tmp_path / "papers" / "official_deepmind_blog.json").write_text(
        json.dumps(alphaevolve_official_blog_manifest_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_official_blog_manifest_drift(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    blog_record = alphaevolve_official_blog_manifest_record()
    blog_record["sources"][0]["source_record"]["claim_boundary"][
        "not_whitepaper_specification"
    ] = False
    (tmp_path / "papers" / "official_deepmind_blog.json").write_text(
        json.dumps(blog_record, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "alphaevolve_official_blog_manifest_invalid_claim_boundary_not_whitepaper_specification" in codes


def test_validate_paper_manifest_reports_invalid_appendix_b_registry(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks"
    registry.mkdir(parents=True)
    (registry / "alphaevolve_appendix_b.json").write_text(
        json.dumps({"schema": "wrong", "families": []}),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    issue_codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "appendix_b_invalid_schema" in issue_codes
    assert "appendix_b_missing_family" in issue_codes


def test_validate_paper_manifest_reports_invalid_ablation_registry(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks"
    registry.mkdir(parents=True)
    (registry / "alphaevolve_ablations.json").write_text(
        json.dumps({"schema": "wrong", "variants": [], "report_contract": {}}),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    issue_codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "ablation_invalid_schema" in issue_codes
    assert "ablation_missing_variant" in issue_codes


def test_validate_paper_manifest_accepts_figure8_ablation_artifact_sidecar(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.FIGURE8_ABLATION_ARTIFACTS_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.figure8_artifact_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_figure8_ablation_artifact_sidecar_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.figure8_artifact_boundary_record()
    record["source_figure"] = "Figure 7"
    record["source_figure_ids"] = ["Figure 7"]
    sidecar = tmp_path / paper_manifest.FIGURE8_ABLATION_ARTIFACTS_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "figure8_ablation_artifact_invalid_source_figure" in codes
    assert "figure8_ablation_artifact_invalid_source_figure_ids" in codes


def test_validate_paper_manifest_requires_figure8_ablation_artifact_sidecar_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "figure8_ablation_artifact_manifest_missing" in codes


def test_validate_paper_manifest_accepts_benchmark_fixture_readiness_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.BENCHMARK_FIXTURE_READINESS_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.benchmark_fixture_readiness_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_benchmark_fixture_readiness_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.benchmark_fixture_readiness_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "paper_claim_ready"
    record["missing_evidence"]["repeated_seed_protocol"] = "recorded"
    sidecar = tmp_path / paper_manifest.BENCHMARK_FIXTURE_READINESS_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "benchmark_fixture_readiness_boundary_claim_ready_overclaim" in codes
    assert "benchmark_fixture_readiness_boundary_invalid_boundary_status" in codes
    assert (
        "benchmark_fixture_readiness_boundary_invalid_missing_evidence_repeated_seed_protocol"
        in codes
    )


def test_validate_paper_manifest_requires_benchmark_fixture_readiness_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "benchmark_fixture_readiness_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_systems_result_readiness_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.SYSTEMS_RESULT_READINESS_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.systems_result_readiness_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_systems_result_readiness_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.systems_result_readiness_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "real_systems_fixtures_ready"
    record["source_section_ids"] = ["3.2"]
    record["missing_evidence"]["deployment_measurement_artifacts"] = "recorded"
    sidecar = tmp_path / paper_manifest.SYSTEMS_RESULT_READINESS_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "systems_result_readiness_boundary_claim_ready_overclaim" in codes
    assert "systems_result_readiness_boundary_invalid_boundary_status" in codes
    assert "systems_result_readiness_boundary_invalid_source_section_ids" in codes
    assert (
        "systems_result_readiness_boundary_invalid_missing_evidence_deployment_measurement_artifacts"
        in codes
    )


def test_validate_paper_manifest_requires_systems_result_readiness_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "systems_result_readiness_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_problem_formulation_provenance_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PROBLEM_FORMULATION_PROVENANCE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.problem_formulation_provenance_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_problem_formulation_provenance_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.problem_formulation_provenance_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "expert_guided_formulation_ready"
    record["source_section_ids"] = ["2.1"]
    record["missing_evidence"]["alphaevolve_expert_guided_formulation_parity"] = "recorded"
    sidecar = tmp_path / paper_manifest.PROBLEM_FORMULATION_PROVENANCE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "problem_formulation_provenance_boundary_claim_ready_overclaim" in codes
    assert "problem_formulation_provenance_boundary_invalid_boundary_status" in codes
    assert "problem_formulation_provenance_boundary_invalid_source_section_ids" in codes
    assert (
        "problem_formulation_provenance_boundary_invalid_missing_evidence_alphaevolve_expert_guided_formulation_parity"
        in codes
    )


def test_validate_paper_manifest_requires_problem_formulation_provenance_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "problem_formulation_provenance_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_programmatic_representation_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PROGRAMMATIC_REPRESENTATION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.programmatic_representation_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_programmatic_representation_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.programmatic_representation_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "ai_coscientist_bridge_ready"
    record["missing_evidence"]["natural_language_to_programmatic_bridge_status"] = (
        "recorded"
    )
    sidecar = tmp_path / paper_manifest.PROGRAMMATIC_REPRESENTATION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "programmatic_representation_boundary_claim_ready_overclaim" in codes
    assert "programmatic_representation_boundary_invalid_boundary_status" in codes
    assert (
        "programmatic_representation_boundary_invalid_missing_evidence_natural_language_to_programmatic_bridge_status"
        in codes
    )


def test_validate_paper_manifest_requires_programmatic_representation_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "programmatic_representation_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_qualitative_feedback_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.QUALITATIVE_FEEDBACK_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.qualitative_feedback_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_qualitative_feedback_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.qualitative_feedback_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "executed_qualitative_feedback_calibration_ready"
    record["source_section_ids"] = ["2.3"]
    record["missing_evidence"]["executed_calibration_task_suite"] = "recorded"
    sidecar = tmp_path / paper_manifest.QUALITATIVE_FEEDBACK_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "qualitative_feedback_boundary_claim_ready_overclaim" in codes
    assert "qualitative_feedback_boundary_invalid_boundary_status" in codes
    assert "qualitative_feedback_boundary_invalid_source_section_ids" in codes
    assert (
        "qualitative_feedback_boundary_invalid_missing_evidence_executed_calibration_task_suite"
        in codes
    )


def test_validate_paper_manifest_requires_qualitative_feedback_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "qualitative_feedback_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_feedback_calibration_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.FEEDBACK_CALIBRATION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.feedback_calibration_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_feedback_calibration_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.feedback_calibration_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "executed_feedback_calibration_ready"
    record["source_section_ids"] = ["2.3"]
    record["missing_evidence"]["runtime_calibration_runner"] = "recorded"
    sidecar = tmp_path / paper_manifest.FEEDBACK_CALIBRATION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "feedback_calibration_boundary_claim_ready_overclaim" in codes
    assert "feedback_calibration_boundary_invalid_boundary_status" in codes
    assert "feedback_calibration_boundary_invalid_source_section_ids" in codes
    assert (
        "feedback_calibration_boundary_invalid_missing_evidence_runtime_calibration_runner"
        in codes
    )


def test_validate_paper_manifest_requires_feedback_calibration_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "feedback_calibration_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_llm_role_scheduler_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.LLM_ROLE_SCHEDULER_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.llm_role_scheduler_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_llm_role_scheduler_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.llm_role_scheduler_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "calibrated_alphaevolve_role_scheduler_ready"
    record["missing_evidence"]["calibrated_role_reward_policy"] = "recorded"
    sidecar = tmp_path / paper_manifest.LLM_ROLE_SCHEDULER_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "llm_role_scheduler_boundary_claim_ready_overclaim" in codes
    assert "llm_role_scheduler_boundary_invalid_boundary_status" in codes
    assert (
        "llm_role_scheduler_boundary_invalid_missing_evidence_calibrated_role_reward_policy"
        in codes
    )


def test_validate_paper_manifest_requires_llm_role_scheduler_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "llm_role_scheduler_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_llm_budget_policy_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.LLM_BUDGET_POLICY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.llm_budget_policy_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_llm_budget_policy_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.llm_budget_policy_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "async_pending_work_budget_accounting_ready"
    record["missing_evidence"]["queued_running_pending_work_budget_state"] = "recorded"
    sidecar = tmp_path / paper_manifest.LLM_BUDGET_POLICY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "llm_budget_policy_boundary_claim_ready_overclaim" in codes
    assert "llm_budget_policy_boundary_invalid_boundary_status" in codes
    assert (
        "llm_budget_policy_boundary_invalid_missing_evidence_queued_running_pending_work_budget_state"
        in codes
    )


def test_validate_paper_manifest_requires_llm_budget_policy_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "llm_budget_policy_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_llm_stochastic_reproducibility_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.LLM_STOCHASTIC_REPRODUCIBILITY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.llm_stochastic_reproducibility_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_llm_stochastic_reproducibility_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.llm_stochastic_reproducibility_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "deterministic_provider_replay_ready"
    record["missing_evidence"]["repeated_identical_call_fixtures"] = "recorded"
    sidecar = tmp_path / paper_manifest.LLM_STOCHASTIC_REPRODUCIBILITY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "llm_stochastic_reproducibility_boundary_claim_ready_overclaim" in codes
    assert "llm_stochastic_reproducibility_boundary_invalid_boundary_status" in codes
    assert (
        "llm_stochastic_reproducibility_boundary_invalid_missing_evidence_repeated_identical_call_fixtures"
        in codes
    )


def test_validate_paper_manifest_requires_llm_stochastic_reproducibility_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "llm_stochastic_reproducibility_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_fast_strong_model_mix_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.FAST_STRONG_MODEL_MIX_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.fast_strong_model_mix_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_fast_strong_model_mix_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.fast_strong_model_mix_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "alphaevolve_fast_strong_model_mix_ready"
    record["source_section_ids"] = ["2.4"]
    record["missing_evidence"]["experiment_level_selection_traces"] = "recorded"
    sidecar = tmp_path / paper_manifest.FAST_STRONG_MODEL_MIX_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "fast_strong_model_mix_boundary_claim_ready_overclaim" in codes
    assert "fast_strong_model_mix_boundary_invalid_boundary_status" in codes
    assert "fast_strong_model_mix_boundary_invalid_source_section_ids" in codes
    assert (
        "fast_strong_model_mix_boundary_invalid_missing_evidence_experiment_level_selection_traces"
        in codes
    )


def test_validate_paper_manifest_requires_fast_strong_model_mix_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "fast_strong_model_mix_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_provider_cancellation_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PROVIDER_CANCELLATION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.provider_cancellation_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_provider_cancellation_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.provider_cancellation_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "live_hard_provider_cancellation_ready"
    record["missing_evidence"]["live_provider_sdk_cancellation"] = "recorded"
    sidecar = tmp_path / paper_manifest.PROVIDER_CANCELLATION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "provider_cancellation_boundary_claim_ready_overclaim" in codes
    assert "provider_cancellation_boundary_invalid_boundary_status" in codes
    assert (
        "provider_cancellation_boundary_invalid_missing_evidence_live_provider_sdk_cancellation"
        in codes
    )


def test_validate_paper_manifest_requires_provider_cancellation_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "provider_cancellation_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_provider_pricing_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PROVIDER_PRICING_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.provider_pricing_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_provider_pricing_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.provider_pricing_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "live_provider_pricing_ready"
    record["missing_evidence"]["live_provider_pricing"] = "recorded"
    sidecar = tmp_path / paper_manifest.PROVIDER_PRICING_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "provider_pricing_boundary_claim_ready_overclaim" in codes
    assert "provider_pricing_boundary_invalid_boundary_status" in codes
    assert (
        "provider_pricing_boundary_invalid_missing_evidence_live_provider_pricing"
        in codes
    )


def test_validate_paper_manifest_requires_provider_pricing_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "provider_pricing_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_provider_diagnostics_replay_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PROVIDER_DIAGNOSTICS_REPLAY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.provider_diagnostics_replay_boundary_record(), indent=2
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_provider_diagnostics_replay_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.provider_diagnostics_replay_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "raw_provider_replay_ready"
    record["missing_evidence"]["raw_provider_payload_sidecars"] = "recorded"
    sidecar = tmp_path / paper_manifest.PROVIDER_DIAGNOSTICS_REPLAY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "provider_diagnostics_replay_boundary_claim_ready_overclaim" in codes
    assert "provider_diagnostics_replay_boundary_invalid_boundary_status" in codes
    assert (
        "provider_diagnostics_replay_boundary_invalid_missing_evidence_raw_provider_payload_sidecars"
        in codes
    )


def test_validate_paper_manifest_requires_provider_diagnostics_replay_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "provider_diagnostics_replay_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_critique_reviewer_pool_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.CRITIQUE_REVIEWER_POOL_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.critique_reviewer_pool_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_critique_reviewer_pool_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.critique_reviewer_pool_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "calibrated_async_reviewer_pool_ready"
    record["missing_evidence"]["calibrated_reviewer_score_report"] = "recorded"
    sidecar = tmp_path / paper_manifest.CRITIQUE_REVIEWER_POOL_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "critique_reviewer_pool_boundary_claim_ready_overclaim" in codes
    assert "critique_reviewer_pool_boundary_invalid_boundary_status" in codes
    assert (
        "critique_reviewer_pool_boundary_invalid_missing_evidence_calibrated_reviewer_score_report"
        in codes
    )


def test_validate_paper_manifest_requires_critique_reviewer_pool_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "critique_reviewer_pool_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_prompt_section_packing_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PROMPT_SECTION_PACKING_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.prompt_section_packing_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_prompt_section_packing_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.prompt_section_packing_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "all_role_provider_token_section_packing_ready"
    record["missing_evidence"]["all_role_provider_token_section_packing"] = "recorded"
    sidecar = tmp_path / paper_manifest.PROMPT_SECTION_PACKING_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "prompt_section_packing_boundary_claim_ready_overclaim" in codes
    assert "prompt_section_packing_boundary_invalid_boundary_status" in codes
    assert (
        "prompt_section_packing_boundary_invalid_missing_evidence_all_role_provider_token_section_packing"
        in codes
    )


def test_validate_paper_manifest_requires_prompt_section_packing_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "prompt_section_packing_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_stochastic_prompt_format_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.STOCHASTIC_PROMPT_FORMAT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.stochastic_prompt_format_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_stochastic_prompt_format_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.stochastic_prompt_format_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "separate_source_distribution_claim_ready"
    record["missing_evidence"]["separate_distribution_config_source_path"] = "recorded"
    sidecar = tmp_path / paper_manifest.STOCHASTIC_PROMPT_FORMAT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "stochastic_prompt_format_boundary_claim_ready_overclaim" in codes
    assert "stochastic_prompt_format_boundary_invalid_boundary_status" in codes
    assert (
        "stochastic_prompt_format_boundary_invalid_missing_evidence_separate_distribution_config_source_path"
        in codes
    )


def test_validate_paper_manifest_requires_stochastic_prompt_format_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "stochastic_prompt_format_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_documentation_truthfulness_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.DOCUMENTATION_TRUTHFULNESS_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.documentation_truthfulness_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_documentation_truthfulness_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.documentation_truthfulness_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "full_semantic_documentation_truth_proof_ready"
    record["missing_evidence"]["semantic_claim_verifier"] = "recorded"
    sidecar = tmp_path / paper_manifest.DOCUMENTATION_TRUTHFULNESS_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "documentation_truthfulness_boundary_claim_ready_overclaim" in codes
    assert "documentation_truthfulness_boundary_invalid_boundary_status" in codes
    assert (
        "documentation_truthfulness_boundary_invalid_missing_evidence_semantic_claim_verifier"
        in codes
    )


def test_validate_paper_manifest_requires_documentation_truthfulness_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "documentation_truthfulness_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_docs_status_ledger_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    (tmp_path / "docs" / "todo").mkdir(parents=True)
    (tmp_path / "papers").mkdir(exist_ok=True)
    (tmp_path / "README.md").write_text("[docs/status.md](docs/status.md)\n", encoding="utf-8")
    (tmp_path / "docs" / "README.md").write_text(
        "[Current Status](./status.md)\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "todo" / "readme.md").write_text(
        "Add `docs/status.md` ledger freshness and coverage evidence.\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "status.md").write_text(
        "# Current Implementation Status\n"
        "\n"
        "Implemented today:\n"
        "- Implemented local smoke support.\n"
        "\n"
        "Important limits:\n"
        "- Missing semantic freshness proof.\n",
        encoding="utf-8",
    )
    (tmp_path / "papers" / "README.md").write_text(
        "papers/status_claim_inventory.json\n",
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.DOCS_STATUS_LEDGER_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.docs_status_ledger_boundary_record(tmp_path),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_docs_status_ledger_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.docs_status_ledger_boundary_record(tmp_path)
    record["claim_ready"] = True
    record["boundary_status"] = "docs_status_semantic_freshness_verified"
    record["missing_evidence"]["owner_review_signoff"] = "recorded"
    sidecar = tmp_path / paper_manifest.DOCS_STATUS_LEDGER_BOUNDARY_FILE
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "docs_status_ledger_boundary_claim_ready_overclaim" in codes
    assert "docs_status_ledger_boundary_invalid_boundary_status" in codes
    assert (
        "docs_status_ledger_boundary_invalid_missing_evidence_owner_review_signoff"
        in codes
    )


def test_validate_paper_manifest_requires_docs_status_ledger_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "docs_status_ledger_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_development_provider_example_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    marker_files = {
        "docs/development.md": (
            'py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world '
            '--max-generations 10 --backends "openai:<openai-model-id>"\n'
            'py -3.12 -m libreevolve run libreevolve/problems/examples/circle_packing '
            '--max-generations 10 --backends "anthropic:<anthropic-model-id>"\n'
            "py -3.12 -m libreevolve show runs/hello_world\n"
            "Replace placeholder backend model ids with currently available provider/account\n"
            "model ids before running.\n"
        ),
        "README.md": (
            "available in\nyour account or local Ollama install\n"
            "credentials, model IDs, local Ollama state, or account access\n"
        ),
        "docs/README.md": (
            "[Development](./development.md)\n"
            "[Backends](./backends.md)\n"
        ),
        "docs/backends.md": (
            "Built-in SDK adapters\n"
            "Google/Gemini is not a built-in registry provider yet\n"
        ),
        "docs/status.md": "Built-in provider adapters are OpenAI, Anthropic, and Ollama\n",
        "papers/README.md": (
            "papers/readme_provider_example_matrix_boundary.json\n"
            "papers/readme_provider_auth_boundary.json\n"
            "papers/gemini_provider_parity_boundary.json\n"
            "credential-safe provider smoke matrix\n"
        ),
        "docs/todo/readme.md": "Add development-guide provider example smoke evidence.\n",
    }
    for relative_path, content in marker_files.items():
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    sidecar = tmp_path / paper_manifest.DEVELOPMENT_PROVIDER_EXAMPLE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.development_provider_example_boundary_record(tmp_path),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_development_provider_example_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.development_provider_example_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "development_provider_examples_live_smoke_ready"
    record["missing_evidence"]["ci_development_provider_matrix"] = "recorded"
    sidecar = tmp_path / paper_manifest.DEVELOPMENT_PROVIDER_EXAMPLE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "development_provider_example_boundary_claim_ready_overclaim" in codes
    assert "development_provider_example_boundary_invalid_boundary_status" in codes
    assert (
        "development_provider_example_boundary_invalid_missing_evidence_ci_development_provider_matrix"
        in codes
    )


def test_validate_paper_manifest_requires_development_provider_example_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "development_provider_example_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_development_workflow_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    marker_files = {
        "docs/development.md": (
            "py -3.12\n"
            'py -3.12 -m pip install -e ".[dev]"\n'
            "py -3.12 -m pre_commit install\n"
            "loads `.env` during run setup with `override=True`\n"
            'py -3.12 -m pytest tests/ -m "not integration" --tb=short\n'
            "py -3.12 -m pytest tests/integration/ -m integration\n"
            "py -3.12 -m pre_commit run --all-files\n"
            "git diff --check\n"
            "py -3.12 -m libreevolve.tools.paper_manifest --rehydrate\n"
            "py -3.12 -m libreevolve.tools.paper_manifest\n"
            "py -3.12 -m libreevolve.tools.paper_manifest --require-local-pdfs\n"
            "use `--json` when auditing\n"
            "[docs/release-checklist.md](release-checklist.md)\n"
            "path-scoped\n`push` / `pull_request` events\n"
            "The secret scan uses `.secrets.baseline`.\n"
            "## Repository conventions\n"
            "[Architecture](./architecture.md)\n"
            "[Problem Format](./problem-format.md)\n"
            "[Configuration](./configuration.md)\n"
            "[Plugins](./plugins.md)\n"
            "numpy scikit-learn anthropic openai ollama pyyaml click python-dotenv packaging pypdf\n"
            "pytest pytest-mock pre-commit detect-secrets\n"
        ),
        "pyproject.toml": (
            'requires-python = ">=3.11"\n'
            "[project.optional-dependencies]\n"
            'libreevolve = "libreevolve.cli:cli"\n'
        ),
        ".pre-commit-config.yaml": "detect-secrets\n.secrets.baseline\n",
        ".github/workflows/tests.yml": (
            '"docs/**"\n"papers/**"\n"tests/**"\n'
            "Run detect-secrets\n"
            'python -m pytest tests/ -m "not integration" --tb=short\n'
            "python -m libreevolve.tools.paper_manifest --root .\n"
            'Path("tests").glob("test_*boundary.py")\n'
            "Release Artifact Smoke\n"
            "ANTHROPIC_API_KEY is not configured; skipping integration tests.\n"
        ),
        "README.md": "operational details belong in `docs/`\n",
        "docs/README.md": "[Development](./development.md)\n",
        "docs/release-checklist.md": "## Required Local Evidence\n",
        "docs/run-artifacts.md": "release-smoke checklist exist\n",
        "papers/README.md": (
            "papers/release_checklist_documentation_boundary.json\n"
            "papers/ci_workflow_coverage_boundary.json\n"
        ),
        "tests/test_agents_docs.py": (
            "test_development_docs_track_detect_secrets_baseline_workflow\n"
            "test_tests_workflow_covers_docs_papers_and_todo_changes\n"
        ),
        "docs/todo/readme.md": (
            "Add development-guide workflow and convention drift evidence.\n"
        ),
    }
    for relative_path, content in marker_files.items():
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    sidecar = tmp_path / paper_manifest.DEVELOPMENT_WORKFLOW_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.development_workflow_boundary_record(tmp_path),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_development_workflow_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.development_workflow_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "development_workflow_semantic_drift_gate_ready"
    record["missing_evidence"]["owner_review_signoff"] = "recorded"
    sidecar = tmp_path / paper_manifest.DEVELOPMENT_WORKFLOW_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "development_workflow_boundary_claim_ready_overclaim" in codes
    assert "development_workflow_boundary_invalid_boundary_status" in codes
    assert (
        "development_workflow_boundary_invalid_missing_evidence_owner_review_signoff"
        in codes
    )


def test_validate_paper_manifest_requires_development_workflow_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "development_workflow_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_documentation_claim_inventory(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.DOCUMENTATION_CLAIM_INVENTORY_FILE
    sidecar.write_text("{}", encoding="utf-8")
    sidecar.write_text(
        json.dumps(paper_manifest.documentation_claim_inventory_record(tmp_path), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_documentation_claim_inventory_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.DOCUMENTATION_CLAIM_INVENTORY_FILE
    sidecar.write_text("{}", encoding="utf-8")
    record = paper_manifest.documentation_claim_inventory_record(tmp_path)
    record["claim_ready"] = True
    record["inventory_status"] = "complete_semantic_documentation_truth_ready"
    record["claims"][0]["evidence_refs"] = ["README.md"]
    record["missing_evidence"]["semantic_claim_verifier"] = "recorded"
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "documentation_claim_inventory_claim_ready_overclaim" in codes
    assert "documentation_claim_inventory_invalid_inventory_status" in codes
    assert (
        "documentation_claim_inventory_invalid_readme_current_status_scope_evidence_refs"
        in codes
    )
    assert (
        "documentation_claim_inventory_invalid_missing_evidence_semantic_claim_verifier"
        in codes
    )


def test_validate_paper_manifest_requires_documentation_claim_inventory_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "documentation_claim_inventory_manifest_missing" in codes


def test_validate_paper_manifest_accepts_implementation_evidence_map_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.IMPLEMENTATION_EVIDENCE_MAP_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.implementation_evidence_map_boundary_record(), indent=2
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_implementation_evidence_map_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.implementation_evidence_map_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "exhaustive_alphaevolve_implementation_audit_ready"
    record["requirements"][0]["module_refs"] = ["libreevolve/core/loop.py"]
    record["missing_evidence"]["exhaustive_requirement_inventory"] = "recorded"
    sidecar = tmp_path / paper_manifest.IMPLEMENTATION_EVIDENCE_MAP_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "implementation_evidence_map_boundary_claim_ready_overclaim" in codes
    assert "implementation_evidence_map_boundary_invalid_boundary_status" in codes
    assert (
        "implementation_evidence_map_boundary_invalid_alphaevolve_program_markers_module_refs"
        in codes
    )
    assert (
        "implementation_evidence_map_boundary_invalid_missing_evidence_exhaustive_requirement_inventory"
        in codes
    )


def test_validate_paper_manifest_requires_implementation_evidence_map_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "implementation_evidence_map_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_related_work_taxonomy_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.RELATED_WORK_TAXONOMY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.related_work_taxonomy_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_related_work_taxonomy_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.related_work_taxonomy_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "related_work_taxonomy_ready"
    record["source_section_ids"] = ["4"]
    record["missing_evidence"]["method_family_taxonomy"] = "recorded"
    sidecar = tmp_path / paper_manifest.RELATED_WORK_TAXONOMY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "related_work_taxonomy_boundary_claim_ready_overclaim" in codes
    assert "related_work_taxonomy_boundary_invalid_boundary_status" in codes
    assert "related_work_taxonomy_boundary_invalid_source_section_ids" in codes
    assert (
        "related_work_taxonomy_boundary_invalid_missing_evidence_method_family_taxonomy"
        in codes
    )


def test_validate_paper_manifest_requires_related_work_taxonomy_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "related_work_taxonomy_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_natural_language_preamble_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.NATURAL_LANGUAGE_PREAMBLE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.natural_language_preamble_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_natural_language_preamble_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.natural_language_preamble_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "complete_alphaevolve_rationale_handling"
    record["missing_evidence"]["semantic_rationale_quality_scoring"] = "recorded"
    sidecar = tmp_path / paper_manifest.NATURAL_LANGUAGE_PREAMBLE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "natural_language_preamble_boundary_claim_ready_overclaim" in codes
    assert "natural_language_preamble_boundary_invalid_boundary_status" in codes
    assert (
        "natural_language_preamble_boundary_invalid_missing_evidence_semantic_rationale_quality_scoring"
        in codes
    )


def test_validate_paper_manifest_requires_natural_language_preamble_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "natural_language_preamble_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_prompt_example_copy_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PROMPT_EXAMPLE_COPY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.prompt_example_copy_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_prompt_example_copy_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.prompt_example_copy_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "full_prompt_example_copy_guard_ready"
    record["missing_evidence"]["semantic_or_renamed_copy_detection"] = "recorded"
    sidecar = tmp_path / paper_manifest.PROMPT_EXAMPLE_COPY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "prompt_example_copy_boundary_claim_ready_overclaim" in codes
    assert "prompt_example_copy_boundary_invalid_boundary_status" in codes
    assert (
        "prompt_example_copy_boundary_invalid_missing_evidence_semantic_or_renamed_copy_detection"
        in codes
    )


def test_validate_paper_manifest_requires_prompt_example_copy_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "prompt_example_copy_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_mutation_consistency_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.MUTATION_CONSISTENCY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.mutation_consistency_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_mutation_consistency_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.mutation_consistency_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "semantic_multi_edit_consistency_proven"
    record["missing_evidence"]["required_companion_edit_inference"] = "recorded"
    sidecar = tmp_path / paper_manifest.MUTATION_CONSISTENCY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "mutation_consistency_boundary_claim_ready_overclaim" in codes
    assert "mutation_consistency_boundary_invalid_boundary_status" in codes
    assert (
        "mutation_consistency_boundary_invalid_missing_evidence_required_companion_edit_inference"
        in codes
    )


def test_validate_paper_manifest_requires_mutation_consistency_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "mutation_consistency_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_mutation_operator_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.MUTATION_OPERATOR_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.mutation_operator_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_mutation_operator_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.mutation_operator_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "operator_family_evidence_ready"
    record["source_section_ids"] = ["2.3"]
    record["missing_evidence"]["operator_family_scoring"] = "recorded"
    sidecar = tmp_path / paper_manifest.MUTATION_OPERATOR_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "mutation_operator_boundary_claim_ready_overclaim" in codes
    assert "mutation_operator_boundary_invalid_boundary_status" in codes
    assert "mutation_operator_boundary_invalid_source_section_ids" in codes
    assert (
        "mutation_operator_boundary_invalid_missing_evidence_operator_family_scoring"
        in codes
    )


def test_validate_paper_manifest_requires_mutation_operator_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "mutation_operator_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_adaptive_mutation_mode_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.ADAPTIVE_MUTATION_MODE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.adaptive_mutation_mode_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_adaptive_mutation_mode_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.adaptive_mutation_mode_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "adaptive_mutation_mode_selection_ready"
    record["missing_evidence"]["selection_reason_telemetry"] = "recorded"
    sidecar = tmp_path / paper_manifest.ADAPTIVE_MUTATION_MODE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "adaptive_mutation_mode_boundary_claim_ready_overclaim" in codes
    assert "adaptive_mutation_mode_boundary_invalid_boundary_status" in codes
    assert (
        "adaptive_mutation_mode_boundary_invalid_missing_evidence_selection_reason_telemetry"
        in codes
    )


def test_validate_paper_manifest_requires_adaptive_mutation_mode_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "adaptive_mutation_mode_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_initial_pool_divergence_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.INITIAL_POOL_DIVERGENCE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.initial_pool_divergence_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_initial_pool_divergence_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.initial_pool_divergence_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "functional_discovery_distance_ready"
    record["missing_evidence"]["syntax_and_function_joint_claim_gate"] = "recorded"
    sidecar = tmp_path / paper_manifest.INITIAL_POOL_DIVERGENCE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "initial_pool_divergence_boundary_claim_ready_overclaim" in codes
    assert "initial_pool_divergence_boundary_invalid_boundary_status" in codes
    assert (
        "initial_pool_divergence_boundary_invalid_missing_evidence_syntax_and_function_joint_claim_gate"
        in codes
    )


def test_validate_paper_manifest_requires_initial_pool_divergence_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "initial_pool_divergence_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_duplicate_work_policy_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.DUPLICATE_WORK_POLICY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.duplicate_work_policy_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_duplicate_work_policy_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.duplicate_work_policy_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "alphaevolve_grade_duplicate_work_memory_ready"
    record["missing_evidence"]["durable_evaluation_cache_storage"] = "recorded"
    sidecar = tmp_path / paper_manifest.DUPLICATE_WORK_POLICY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "duplicate_work_policy_boundary_claim_ready_overclaim" in codes
    assert "duplicate_work_policy_boundary_invalid_boundary_status" in codes
    assert (
        "duplicate_work_policy_boundary_invalid_missing_evidence_durable_evaluation_cache_storage"
        in codes
    )


def test_validate_paper_manifest_requires_duplicate_work_policy_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "duplicate_work_policy_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_map_elites_descriptor_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.MAP_ELITES_DESCRIPTOR_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.map_elites_descriptor_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_map_elites_descriptor_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.map_elites_descriptor_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "stable_behavior_descriptor_and_rebin_ready"
    record["missing_evidence"]["learned_descriptor_model"] = "recorded"
    sidecar = tmp_path / paper_manifest.MAP_ELITES_DESCRIPTOR_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "map_elites_descriptor_boundary_claim_ready_overclaim" in codes
    assert "map_elites_descriptor_boundary_invalid_boundary_status" in codes
    assert (
        "map_elites_descriptor_boundary_invalid_missing_evidence_learned_descriptor_model"
        in codes
    )


def test_validate_paper_manifest_requires_map_elites_descriptor_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "map_elites_descriptor_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_objective_archive_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.OBJECTIVE_ARCHIVE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.objective_archive_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_objective_archive_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.objective_archive_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "primary_pareto_archive_replacement_ready"
    record["missing_evidence"]["primary_pareto_archive_replacement"] = "recorded"
    sidecar = tmp_path / paper_manifest.OBJECTIVE_ARCHIVE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "objective_archive_boundary_claim_ready_overclaim" in codes
    assert "objective_archive_boundary_invalid_boundary_status" in codes
    assert (
        "objective_archive_boundary_invalid_missing_evidence_primary_pareto_archive_replacement"
        in codes
    )


def test_validate_paper_manifest_requires_objective_archive_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "objective_archive_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_archive_event_replay_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.ARCHIVE_EVENT_REPLAY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.archive_event_replay_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_archive_event_replay_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.archive_event_replay_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "ordered_archive_event_restore_engine_ready"
    record["missing_evidence"]["ordered_archive_event_restore_engine"] = "recorded"
    sidecar = tmp_path / paper_manifest.ARCHIVE_EVENT_REPLAY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "archive_event_replay_boundary_claim_ready_overclaim" in codes
    assert "archive_event_replay_boundary_invalid_boundary_status" in codes
    assert (
        "archive_event_replay_boundary_invalid_missing_evidence_ordered_archive_event_restore_engine"
        in codes
    )


def test_validate_paper_manifest_requires_archive_event_replay_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "archive_event_replay_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_controller_pending_work_resume_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.CONTROLLER_PENDING_WORK_RESUME_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.controller_pending_work_resume_boundary_record(), indent=2
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_controller_pending_work_resume_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.controller_pending_work_resume_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "pending_work_resume_ready"
    record["missing_evidence"]["controller_queue_checkpoint_schema"] = "recorded"
    sidecar = tmp_path / paper_manifest.CONTROLLER_PENDING_WORK_RESUME_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "controller_pending_work_resume_boundary_claim_ready_overclaim" in codes
    assert "controller_pending_work_resume_boundary_invalid_boundary_status" in codes
    assert (
        "controller_pending_work_resume_boundary_invalid_missing_evidence_controller_queue_checkpoint_schema"
        in codes
    )


def test_validate_paper_manifest_requires_controller_pending_work_resume_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "controller_pending_work_resume_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_lineage_replay_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.LINEAGE_REPLAY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.lineage_replay_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_lineage_replay_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.lineage_replay_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "end_to_end_lineage_replay_ready"
    record["missing_evidence"]["end_to_end_resumed_lineage_trace"] = "recorded"
    sidecar = tmp_path / paper_manifest.LINEAGE_REPLAY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "lineage_replay_boundary_claim_ready_overclaim" in codes
    assert "lineage_replay_boundary_invalid_boundary_status" in codes
    assert (
        "lineage_replay_boundary_invalid_missing_evidence_end_to_end_resumed_lineage_trace"
        in codes
    )


def test_validate_paper_manifest_requires_lineage_replay_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "lineage_replay_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_runtime_rng_replay_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.RUNTIME_RNG_REPLAY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.runtime_rng_replay_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_runtime_rng_replay_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.runtime_rng_replay_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "full_sampling_replay_ready"
    record["missing_evidence"]["end_to_end_sampling_continuity_trace"] = "recorded"
    sidecar = tmp_path / paper_manifest.RUNTIME_RNG_REPLAY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "runtime_rng_replay_boundary_claim_ready_overclaim" in codes
    assert "runtime_rng_replay_boundary_invalid_boundary_status" in codes
    assert (
        "runtime_rng_replay_boundary_invalid_missing_evidence_end_to_end_sampling_continuity_trace"
        in codes
    )


def test_validate_paper_manifest_requires_runtime_rng_replay_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "runtime_rng_replay_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_validator_execution_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.VALIDATOR_EXECUTION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.validator_execution_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_validator_execution_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.validator_execution_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "os_container_sandbox_ready"
    record["missing_evidence"]["os_container_sandbox_enforcement"] = "recorded"
    sidecar = tmp_path / paper_manifest.VALIDATOR_EXECUTION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "validator_execution_boundary_claim_ready_overclaim" in codes
    assert "validator_execution_boundary_invalid_boundary_status" in codes
    assert (
        "validator_execution_boundary_invalid_missing_evidence_os_container_sandbox_enforcement"
        in codes
    )


def test_validate_paper_manifest_requires_validator_execution_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "validator_execution_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_validator_artifact_promotion_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.VALIDATOR_ARTIFACT_PROMOTION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.validator_artifact_promotion_boundary_record(), indent=2
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_validator_artifact_promotion_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.validator_artifact_promotion_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "release_artifact_promotion_gate_ready"
    record["missing_evidence"]["release_artifact_promotion_gate"] = "recorded"
    sidecar = tmp_path / paper_manifest.VALIDATOR_ARTIFACT_PROMOTION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "validator_artifact_promotion_boundary_claim_ready_overclaim" in codes
    assert "validator_artifact_promotion_boundary_invalid_boundary_status" in codes
    assert (
        "validator_artifact_promotion_boundary_invalid_missing_evidence_release_artifact_promotion_gate"
        in codes
    )


def test_validate_paper_manifest_requires_validator_artifact_promotion_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "validator_artifact_promotion_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_metric_diverse_prompt_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.METRIC_DIVERSE_PROMPT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.metric_diverse_prompt_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_metric_diverse_prompt_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.metric_diverse_prompt_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "alphaevolve_section_2_4_benchmark_ready"
    record["source_section_ids"] = ["2.3"]
    record["missing_evidence"]["equal_budget_comparison_report"] = "recorded"
    sidecar = tmp_path / paper_manifest.METRIC_DIVERSE_PROMPT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "metric_diverse_prompt_boundary_claim_ready_overclaim" in codes
    assert "metric_diverse_prompt_boundary_invalid_boundary_status" in codes
    assert "metric_diverse_prompt_boundary_invalid_source_section_ids" in codes
    assert (
        "metric_diverse_prompt_boundary_invalid_missing_evidence_equal_budget_comparison_report"
        in codes
    )


def test_validate_paper_manifest_requires_metric_diverse_prompt_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "metric_diverse_prompt_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_proposal_score_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PROPOSAL_SCORE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.proposal_score_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_proposal_score_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.proposal_score_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "semantic_idea_memory_ready"
    record["missing_evidence"]["semantic_embedding_proposal_index"] = "recorded"
    sidecar = tmp_path / paper_manifest.PROPOSAL_SCORE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "proposal_score_boundary_claim_ready_overclaim" in codes
    assert "proposal_score_boundary_invalid_boundary_status" in codes
    assert (
        "proposal_score_boundary_invalid_missing_evidence_semantic_embedding_proposal_index"
        in codes
    )


def test_validate_paper_manifest_requires_proposal_score_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "proposal_score_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_proposal_diversity_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PROPOSAL_DIVERSITY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.proposal_diversity_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_proposal_diversity_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.proposal_diversity_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "semantic_proposal_diversity_ready"
    record["source_section_ids"] = ["2.3"]
    record["missing_evidence"]["near_duplicate_detection"] = "recorded"
    sidecar = tmp_path / paper_manifest.PROPOSAL_DIVERSITY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "proposal_diversity_boundary_claim_ready_overclaim" in codes
    assert "proposal_diversity_boundary_invalid_boundary_status" in codes
    assert "proposal_diversity_boundary_invalid_source_section_ids" in codes
    assert (
        "proposal_diversity_boundary_invalid_missing_evidence_near_duplicate_detection"
        in codes
    )


def test_validate_paper_manifest_requires_proposal_diversity_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "proposal_diversity_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_failure_memory_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.FAILURE_MEMORY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.failure_memory_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_failure_memory_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.failure_memory_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "semantic_failed_proposal_memory_ready"
    record["missing_evidence"]["semantic_failed_proposal_retrieval"] = "recorded"
    sidecar = tmp_path / paper_manifest.FAILURE_MEMORY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "failure_memory_boundary_claim_ready_overclaim" in codes
    assert "failure_memory_boundary_invalid_boundary_status" in codes
    assert (
        "failure_memory_boundary_invalid_missing_evidence_semantic_failed_proposal_retrieval"
        in codes
    )


def test_validate_paper_manifest_requires_failure_memory_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "failure_memory_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_program_output_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PROGRAM_OUTPUT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.program_output_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_program_output_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.program_output_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "semantic_output_retrieval_ready"
    record["missing_evidence"]["semantic_output_similarity_search"] = "recorded"
    sidecar = tmp_path / paper_manifest.PROGRAM_OUTPUT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "program_output_boundary_claim_ready_overclaim" in codes
    assert "program_output_boundary_invalid_boundary_status" in codes
    assert (
        "program_output_boundary_invalid_missing_evidence_semantic_output_similarity_search"
        in codes
    )


def test_validate_paper_manifest_requires_program_output_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "program_output_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_artifact_index_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.ARTIFACT_INDEX_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.artifact_index_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_artifact_index_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.artifact_index_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "full_content_artifact_search_ready"
    record["missing_evidence"]["full_artifact_content_search"] = "recorded"
    sidecar = tmp_path / paper_manifest.ARTIFACT_INDEX_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "artifact_index_boundary_claim_ready_overclaim" in codes
    assert "artifact_index_boundary_invalid_boundary_status" in codes
    assert (
        "artifact_index_boundary_invalid_missing_evidence_full_artifact_content_search"
        in codes
    )


def test_validate_paper_manifest_requires_artifact_index_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "artifact_index_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_release_artifact_reproducibility_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.RELEASE_ARTIFACT_REPRODUCIBILITY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.release_artifact_reproducibility_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_release_artifact_reproducibility_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.release_artifact_reproducibility_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "verified_release_distribution"
    record["partial_evidence"]["release_artifact_provenance"] = "signed_release_ready"
    record["missing_evidence"]["signed_release_provenance"] = "recorded"
    record["missing_evidence"]["published_index_verification"] = "recorded"
    sidecar = tmp_path / paper_manifest.RELEASE_ARTIFACT_REPRODUCIBILITY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "release_artifact_reproducibility_boundary_claim_ready_overclaim" in codes
    assert "release_artifact_reproducibility_boundary_invalid_boundary_status" in codes
    assert (
        "release_artifact_reproducibility_boundary_invalid_partial_evidence_release_artifact_provenance"
        in codes
    )
    assert (
        "release_artifact_reproducibility_boundary_invalid_missing_evidence_signed_release_provenance"
        in codes
    )
    assert (
        "release_artifact_reproducibility_boundary_invalid_missing_evidence_published_index_verification"
        in codes
    )


def test_validate_paper_manifest_requires_release_artifact_reproducibility_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "release_artifact_reproducibility_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_release_checklist_documentation_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    source_root = Path(__file__).resolve().parents[1]
    for relative_path in (
        "docs/release-checklist.md",
        ".github/workflows/tests.yml",
        "libreevolve/tools/release_artifact_provenance.py",
        "papers/release_artifact_reproducibility_boundary.json",
        "papers/ci_workflow_coverage_boundary.json",
        "tests/test_agents_docs.py",
        "libreevolve/problems/benchmarks/release_artifact_reproducibility_boundary.py",
    ):
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((source_root / relative_path).read_bytes())
    marker_files = {
        "docs/development.md": "[docs/release-checklist.md](release-checklist.md)\n",
        "docs/run-artifacts.md": "papers/release_artifact_reproducibility_boundary.json\n",
        "ROADMAP.md": "release-smoke checklist is documented\n",
        "papers/README.md": "the local release-smoke checklist is documented\n",
        "docs/todo/readme.md": "Add release-checklist documentation drift evidence.\n",
    }
    for relative_path, content in marker_files.items():
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    record = paper_manifest.release_checklist_documentation_boundary_record(tmp_path)
    sidecar = tmp_path / paper_manifest.RELEASE_CHECKLIST_DOCUMENTATION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_release_checklist_documentation_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.release_checklist_documentation_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "release_checklist_signed_release_ready"
    record["missing_evidence"]["signed_release_provenance"] = "recorded"
    sidecar = tmp_path / paper_manifest.RELEASE_CHECKLIST_DOCUMENTATION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "release_checklist_documentation_boundary_claim_ready_overclaim" in codes
    assert "release_checklist_documentation_boundary_invalid_boundary_status" in codes
    assert (
        "release_checklist_documentation_boundary_invalid_missing_evidence_signed_release_provenance"
        in codes
    )


def test_validate_paper_manifest_requires_release_checklist_documentation_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "release_checklist_documentation_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_task_specification_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.TASK_SPECIFICATION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.task_specification_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_task_specification_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.task_specification_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "full_task_spec_parity_ready"
    record["source_section_ids"] = ["2.2"]
    record["source_figure_ids"] = ["Figure 1"]
    record["missing_evidence"]["full_alphaevolve_task_spec_parity"] = "recorded"
    sidecar = tmp_path / paper_manifest.TASK_SPECIFICATION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "task_specification_boundary_claim_ready_overclaim" in codes
    assert "task_specification_boundary_invalid_boundary_status" in codes
    assert "task_specification_boundary_invalid_source_section_ids" in codes
    assert "task_specification_boundary_invalid_source_figure_ids" in codes
    assert (
        "task_specification_boundary_invalid_missing_evidence_full_alphaevolve_task_spec_parity"
        in codes
    )


def test_validate_paper_manifest_requires_task_specification_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "task_specification_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_collaborator_feedback_provenance_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.COLLABORATOR_FEEDBACK_PROVENANCE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.collaborator_feedback_provenance_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_collaborator_feedback_provenance_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.collaborator_feedback_provenance_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "collaborator_feedback_ready"
    record["source_section_ids"] = ["Contributions"]
    record["missing_evidence"]["alphaevolve_collaborator_feedback_parity"] = "recorded"
    sidecar = tmp_path / paper_manifest.COLLABORATOR_FEEDBACK_PROVENANCE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "collaborator_feedback_provenance_boundary_claim_ready_overclaim" in codes
    assert "collaborator_feedback_provenance_boundary_invalid_boundary_status" in codes
    assert "collaborator_feedback_provenance_boundary_invalid_source_section_ids" in codes
    assert (
        "collaborator_feedback_provenance_boundary_invalid_missing_evidence_alphaevolve_collaborator_feedback_parity"
        in codes
    )


def test_validate_paper_manifest_requires_collaborator_feedback_provenance_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "collaborator_feedback_provenance_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_acknowledgement_role_provenance_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.ACKNOWLEDGEMENT_ROLE_PROVENANCE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.acknowledgement_role_provenance_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_acknowledgement_role_provenance_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.acknowledgement_role_provenance_boundary_record()
    record["claim_ready"] = False
    record["boundary_status"] = "publication_author_ready"
    record["source_section_ids"] = ["Contributions"]
    record["excluded_claims"]["publication_author_metadata"] = "claimed"
    sidecar = tmp_path / paper_manifest.ACKNOWLEDGEMENT_ROLE_PROVENANCE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "acknowledgement_role_provenance_boundary_claim_ready_underclaim" in codes
    assert "acknowledgement_role_provenance_boundary_invalid_boundary_status" in codes
    assert "acknowledgement_role_provenance_boundary_invalid_source_section_ids" in codes
    assert (
        "acknowledgement_role_provenance_boundary_invalid_excluded_claim_publication_author_metadata"
        in codes
    )


def test_validate_paper_manifest_requires_acknowledgement_role_provenance_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "acknowledgement_role_provenance_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_paper_author_metadata_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PAPER_AUTHOR_METADATA_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.paper_author_metadata_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_paper_author_metadata_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.paper_author_metadata_boundary_record()
    record["claim_ready"] = False
    record["boundary_status"] = "title_page_affiliation_ready"
    record["source_section_ids"] = ["Acknowledgements"]
    record["excluded_claims"]["title_page_affiliation_metadata"] = "claimed"
    sidecar = tmp_path / paper_manifest.PAPER_AUTHOR_METADATA_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "paper_author_metadata_boundary_claim_ready_underclaim" in codes
    assert "paper_author_metadata_boundary_invalid_boundary_status" in codes
    assert "paper_author_metadata_boundary_invalid_source_section_ids" in codes
    assert (
        "paper_author_metadata_boundary_invalid_excluded_claim_title_page_affiliation_metadata"
        in codes
    )


def test_validate_paper_manifest_requires_paper_author_metadata_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "paper_author_metadata_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_title_page_affiliation_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.TITLE_PAGE_AFFILIATION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.title_page_affiliation_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_title_page_affiliation_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.title_page_affiliation_boundary_record()
    record["claim_ready"] = False
    record["boundary_status"] = "local_affiliation_ready"
    record["source_section_ids"] = ["Acknowledgements"]
    record["excluded_claims"]["local_libreevolve_affiliation_or_endorsement"] = "claimed"
    sidecar = tmp_path / paper_manifest.TITLE_PAGE_AFFILIATION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "title_page_affiliation_boundary_claim_ready_underclaim" in codes
    assert "title_page_affiliation_boundary_invalid_boundary_status" in codes
    assert "title_page_affiliation_boundary_invalid_source_section_ids" in codes
    assert (
        "title_page_affiliation_boundary_invalid_excluded_claim_local_libreevolve_affiliation_or_endorsement"
        in codes
    )


def test_validate_paper_manifest_requires_title_page_affiliation_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "title_page_affiliation_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_system_contribution_provenance_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.SYSTEM_CONTRIBUTION_PROVENANCE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.system_contribution_provenance_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_system_contribution_provenance_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.system_contribution_provenance_boundary_record()
    record["claim_ready"] = False
    record["boundary_status"] = "git_history_ready"
    record["source_section_ids"] = ["Author information"]
    record["excluded_claims"]["generic_git_history_or_commit_authorship"] = "claimed"
    sidecar = tmp_path / paper_manifest.SYSTEM_CONTRIBUTION_PROVENANCE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "system_contribution_provenance_boundary_claim_ready_underclaim" in codes
    assert "system_contribution_provenance_boundary_invalid_boundary_status" in codes
    assert "system_contribution_provenance_boundary_invalid_source_section_ids" in codes
    assert (
        "system_contribution_provenance_boundary_invalid_excluded_claim_generic_git_history_or_commit_authorship"
        in codes
    )


def test_validate_paper_manifest_requires_system_contribution_provenance_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "system_contribution_provenance_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_initial_program_idea_provenance_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.INITIAL_PROGRAM_IDEA_PROVENANCE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.initial_program_idea_provenance_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_initial_program_idea_provenance_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.initial_program_idea_provenance_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "human_seeded_benchmark_ready"
    record["source_section_ids"] = ["2.1"]
    record["missing_evidence"]["alphaevolve_human_seeded_benchmark_parity"] = "recorded"
    sidecar = tmp_path / paper_manifest.INITIAL_PROGRAM_IDEA_PROVENANCE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "initial_program_idea_provenance_boundary_claim_ready_overclaim" in codes
    assert "initial_program_idea_provenance_boundary_invalid_boundary_status" in codes
    assert "initial_program_idea_provenance_boundary_invalid_source_section_ids" in codes
    assert (
        "initial_program_idea_provenance_boundary_invalid_missing_evidence_alphaevolve_human_seeded_benchmark_parity"
        in codes
    )


def test_validate_paper_manifest_requires_initial_program_idea_provenance_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "initial_program_idea_provenance_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_initial_program_seed_variant_matrix(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.INITIAL_PROGRAM_SEED_VARIANT_MATRIX_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.initial_program_seed_variant_matrix_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_initial_program_seed_variant_matrix_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.initial_program_seed_variant_matrix_record()
    record["claim_ready"] = True
    record["matrix_status"] = "equal_budget_seed_results_ready"
    record["seed_variants"][2]["paper_role"] = "ready"
    record["missing_evidence"]["equal_budget_seed_variant_results"] = "recorded"
    sidecar = tmp_path / paper_manifest.INITIAL_PROGRAM_SEED_VARIANT_MATRIX_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "initial_program_seed_variant_matrix_claim_ready_overclaim" in codes
    assert "initial_program_seed_variant_matrix_invalid_matrix_status" in codes
    assert "initial_program_seed_variant_matrix_invalid_researcher_idea_initial_program_paper_role" in codes
    assert (
        "initial_program_seed_variant_matrix_invalid_missing_evidence_equal_budget_seed_variant_results"
        in codes
    )


def test_validate_paper_manifest_requires_initial_program_seed_variant_matrix_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "initial_program_seed_variant_matrix_manifest_missing" in codes


def test_validate_paper_manifest_accepts_initial_program_validity_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.INITIAL_PROGRAM_VALIDITY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.initial_program_validity_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_initial_program_validity_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.initial_program_validity_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "complete_initial_program_ready"
    record["source_section_ids"] = ["2.2"]
    record["missing_evidence"][
        "alphaevolve_complete_initial_program_parity_default_run"
    ] = "recorded"
    sidecar = tmp_path / paper_manifest.INITIAL_PROGRAM_VALIDITY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "initial_program_validity_boundary_claim_ready_overclaim" in codes
    assert "initial_program_validity_boundary_invalid_boundary_status" in codes
    assert "initial_program_validity_boundary_invalid_source_section_ids" in codes
    assert (
        "initial_program_validity_boundary_invalid_missing_evidence_alphaevolve_complete_initial_program_parity_default_run"
        in codes
    )


def test_validate_paper_manifest_requires_initial_program_validity_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "initial_program_validity_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_existing_codebase_integration_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.EXISTING_CODEBASE_INTEGRATION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.existing_codebase_integration_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_existing_codebase_integration_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.existing_codebase_integration_boundary_record()
    record["claim_ready"] = True
    record["source_section_ids"] = ["2.3"]
    record["source_figure_ids"] = ["Figure 1"]
    sidecar = tmp_path / paper_manifest.EXISTING_CODEBASE_INTEGRATION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "existing_codebase_integration_boundary_claim_ready_overclaim" in codes
    assert "existing_codebase_integration_boundary_invalid_source_section_ids" in codes
    assert "existing_codebase_integration_boundary_invalid_source_figure_ids" in codes


def test_validate_paper_manifest_requires_existing_codebase_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "existing_codebase_integration_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_candidate_language_runner_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.candidate_language_runner_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_candidate_language_runner_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.candidate_language_runner_boundary_record()
    record["claim_ready"] = True
    sidecar = tmp_path / paper_manifest.CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "candidate_language_runner_boundary_claim_ready_overclaim" in codes


def test_validate_paper_manifest_requires_candidate_language_runner_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "candidate_language_runner_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_candidate_abstraction_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.CANDIDATE_ABSTRACTION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.candidate_abstraction_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_candidate_abstraction_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.candidate_abstraction_boundary_record()
    record["selected_abstraction"] = "constructor_function"
    record["source_section_ids"] = ["2.1"]
    sidecar = tmp_path / paper_manifest.CANDIDATE_ABSTRACTION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "candidate_abstraction_boundary_invalid_selected_abstraction" in codes
    assert "candidate_abstraction_boundary_invalid_source_section_ids" in codes


def test_validate_paper_manifest_requires_candidate_abstraction_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "candidate_abstraction_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_candidate_abstraction_bias_matrix(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.CANDIDATE_ABSTRACTION_BIAS_MATRIX_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.candidate_abstraction_bias_matrix_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_candidate_abstraction_bias_matrix_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.candidate_abstraction_bias_matrix_record()
    record["claim_ready"] = True
    record["matrix_status"] = "executed_bias_benchmarks_ready"
    record["abstraction_families"][1]["symmetry_structure_assumption"] = "unknown"
    record["missing_evidence"]["benchmark_result_tables"] = "recorded"
    sidecar = tmp_path / paper_manifest.CANDIDATE_ABSTRACTION_BIAS_MATRIX_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "candidate_abstraction_bias_matrix_claim_ready_overclaim" in codes
    assert "candidate_abstraction_bias_matrix_invalid_matrix_status" in codes
    assert (
        "candidate_abstraction_bias_matrix_invalid_constructor_function_symmetry_structure_assumption"
        in codes
    )
    assert (
        "candidate_abstraction_bias_matrix_invalid_missing_evidence_benchmark_result_tables"
        in codes
    )


def test_validate_paper_manifest_requires_candidate_abstraction_bias_matrix_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "candidate_abstraction_bias_matrix_manifest_missing" in codes


def test_validate_paper_manifest_accepts_ci_workflow_coverage_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.CI_WORKFLOW_COVERAGE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.ci_workflow_coverage_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_ci_workflow_coverage_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.ci_workflow_coverage_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "full_alphaevolve_ci_ready"
    record["partial_evidence"]["cross_platform_ci_matrix"] = "full_cross_platform_ci_ready"
    sidecar = tmp_path / paper_manifest.CI_WORKFLOW_COVERAGE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "ci_workflow_coverage_boundary_claim_ready_overclaim" in codes
    assert "ci_workflow_coverage_boundary_invalid_boundary_status" in codes
    assert (
        "ci_workflow_coverage_boundary_invalid_partial_evidence_cross_platform_ci_matrix"
        in codes
    )


def test_validate_paper_manifest_requires_ci_workflow_coverage_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "ci_workflow_coverage_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_config_validation_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.CONFIG_VALIDATION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.config_validation_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_config_validation_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.config_validation_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "live_provider_api_compatible"
    record["missing_evidence"]["live_provider_model_registry_validation"] = "recorded"
    sidecar = tmp_path / paper_manifest.CONFIG_VALIDATION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "config_validation_boundary_claim_ready_overclaim" in codes
    assert "config_validation_boundary_invalid_boundary_status" in codes
    assert (
        "config_validation_boundary_invalid_missing_evidence_live_provider_model_registry_validation"
        in codes
    )


def test_validate_paper_manifest_requires_config_validation_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "config_validation_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_map_elites_illumination_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.MAP_ELITES_ILLUMINATION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.map_elites_illumination_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_map_elites_illumination_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.map_elites_illumination_boundary_record()
    record["claim_ready"] = True
    sidecar = tmp_path / paper_manifest.MAP_ELITES_ILLUMINATION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "map_elites_illumination_boundary_claim_ready_overclaim" in codes


def test_validate_paper_manifest_requires_map_elites_illumination_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "map_elites_illumination_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_gigaevo_framework_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.GIGAEVO_FRAMEWORK_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.gigaevo_framework_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_gigaevo_framework_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.gigaevo_framework_boundary_record()
    record["claim_ready"] = True
    sidecar = tmp_path / paper_manifest.GIGAEVO_FRAMEWORK_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "gigaevo_framework_boundary_claim_ready_overclaim" in codes


def test_validate_paper_manifest_requires_gigaevo_framework_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "gigaevo_framework_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_kernel_tiling_shape_corpus_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.KERNEL_TILING_SHAPE_CORPUS_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.kernel_tiling_shape_corpus_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_kernel_tiling_shape_corpus_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.kernel_tiling_shape_corpus_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "pallas_shape_corpus_runtime_ready"
    record["missing_evidence"]["real_accelerator_runtime_artifacts"] = "recorded"
    sidecar = tmp_path / paper_manifest.KERNEL_TILING_SHAPE_CORPUS_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "kernel_tiling_shape_corpus_boundary_claim_ready_overclaim" in codes
    assert "kernel_tiling_shape_corpus_boundary_invalid_boundary_status" in codes
    assert (
        "kernel_tiling_shape_corpus_boundary_invalid_missing_evidence_real_accelerator_runtime_artifacts"
        in codes
    )


def test_validate_paper_manifest_requires_kernel_tiling_shape_corpus_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "kernel_tiling_shape_corpus_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_pallas_workflow_baseline_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PALLAS_WORKFLOW_BASELINE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.pallas_workflow_baseline_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_pallas_workflow_baseline_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.pallas_workflow_baseline_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "pallas_workflow_baseline_ready"
    record["missing_evidence"]["baseline_workflow_class"] = "recorded"
    sidecar = tmp_path / paper_manifest.PALLAS_WORKFLOW_BASELINE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "pallas_workflow_baseline_boundary_claim_ready_overclaim" in codes
    assert "pallas_workflow_baseline_boundary_invalid_boundary_status" in codes
    assert (
        "pallas_workflow_baseline_boundary_invalid_missing_evidence_baseline_workflow_class"
        in codes
    )


def test_validate_paper_manifest_requires_pallas_workflow_baseline_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "pallas_workflow_baseline_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_codeevolve_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.CODEEVOLVE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.codeevolve_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_codeevolve_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.codeevolve_boundary_record()
    record["claim_ready"] = True
    sidecar = tmp_path / paper_manifest.CODEEVOLVE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "codeevolve_boundary_claim_ready_overclaim" in codes


def test_validate_paper_manifest_requires_codeevolve_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "codeevolve_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_codebase_scale_benchmark_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.CODEBASE_SCALE_BENCHMARK_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.codebase_scale_benchmark_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_codebase_scale_benchmark_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.codebase_scale_benchmark_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "table1_code_scale_ready"
    record["source_section_ids"] = ["2.2"]
    record["source_table_ids"] = ["Table 2"]
    record["missing_evidence"]["large_multi_component_benchmark_fixture"] = "recorded"
    sidecar = tmp_path / paper_manifest.CODEBASE_SCALE_BENCHMARK_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "codebase_scale_benchmark_boundary_claim_ready_overclaim" in codes
    assert "codebase_scale_benchmark_boundary_invalid_boundary_status" in codes
    assert "codebase_scale_benchmark_boundary_invalid_source_section_ids" in codes
    assert "codebase_scale_benchmark_boundary_invalid_source_table_ids" in codes
    assert (
        "codebase_scale_benchmark_boundary_invalid_missing_evidence_large_multi_component_benchmark_fixture"
        in codes
    )


def test_validate_paper_manifest_requires_codebase_scale_benchmark_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "codebase_scale_benchmark_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_sorting_network_rediscovery_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.SORTING_NETWORK_REDISCOVERY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.sorting_network_rediscovery_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_sorting_network_rediscovery_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.sorting_network_rediscovery_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "certified_rediscovery"
    record["problem_ids"] = ["sorting_network_8"]
    record["missing_evidence"]["repeated_seed_run_tables"] = "recorded"
    sidecar = tmp_path / paper_manifest.SORTING_NETWORK_REDISCOVERY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "sorting_network_rediscovery_boundary_claim_ready_overclaim" in codes
    assert "sorting_network_rediscovery_boundary_invalid_boundary_status" in codes
    assert "sorting_network_rediscovery_boundary_invalid_problem_ids" in codes
    assert (
        "sorting_network_rediscovery_boundary_invalid_missing_evidence_repeated_seed_run_tables"
        in codes
    )


def test_validate_paper_manifest_requires_sorting_network_rediscovery_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "sorting_network_rediscovery_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_table1_capability_exhibit_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.TABLE1_CAPABILITY_EXHIBIT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.table1_capability_exhibit_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_table1_capability_exhibit_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.table1_capability_exhibit_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "table1_parity_ready"
    record["row_ids"] = ["table1.function_vs_file_scope"]
    record["missing_evidence"]["full_table1_parity"] = "recorded"
    sidecar = tmp_path / paper_manifest.TABLE1_CAPABILITY_EXHIBIT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "table1_capability_exhibit_boundary_claim_ready_overclaim" in codes
    assert "table1_capability_exhibit_boundary_invalid_boundary_status" in codes
    assert "table1_capability_exhibit_boundary_invalid_row_ids" in codes
    assert (
        "table1_capability_exhibit_boundary_invalid_missing_evidence_full_table1_parity"
        in codes
    )


def test_validate_paper_manifest_requires_table1_capability_exhibit_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "table1_capability_exhibit_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_self_improvement_distillation_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.SELF_IMPROVEMENT_DISTILLATION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.self_improvement_distillation_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_self_improvement_distillation_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.self_improvement_distillation_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "self_improvement_ready"
    record["source_section_ids"] = ["Section 3"]
    record["missing_evidence"]["distillation_training_run"] = "recorded"
    sidecar = tmp_path / paper_manifest.SELF_IMPROVEMENT_DISTILLATION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "self_improvement_distillation_boundary_claim_ready_overclaim" in codes
    assert "self_improvement_distillation_boundary_invalid_boundary_status" in codes
    assert "self_improvement_distillation_boundary_invalid_source_section_ids" in codes
    assert (
        "self_improvement_distillation_boundary_invalid_missing_evidence_distillation_training_run"
        in codes
    )


def test_validate_paper_manifest_requires_self_improvement_distillation_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "self_improvement_distillation_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_self_improvement_cadence_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.SELF_IMPROVEMENT_CADENCE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.self_improvement_cadence_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_self_improvement_cadence_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.self_improvement_cadence_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "cadence_roi_ready"
    record["source_section_ids"] = ["Section 3"]
    record["missing_evidence"]["environment_setup_cost"] = "recorded"
    sidecar = tmp_path / paper_manifest.SELF_IMPROVEMENT_CADENCE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "self_improvement_cadence_boundary_claim_ready_overclaim" in codes
    assert "self_improvement_cadence_boundary_invalid_boundary_status" in codes
    assert "self_improvement_cadence_boundary_invalid_source_section_ids" in codes
    assert (
        "self_improvement_cadence_boundary_invalid_missing_evidence_environment_setup_cost"
        in codes
    )


def test_validate_paper_manifest_requires_self_improvement_cadence_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "self_improvement_cadence_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_thetaevolve_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.THETAEVOLVE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.thetaevolve_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_thetaevolve_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.thetaevolve_boundary_record()
    record["claim_ready"] = True
    sidecar = tmp_path / paper_manifest.THETAEVOLVE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "thetaevolve_boundary_claim_ready_overclaim" in codes


def test_validate_paper_manifest_requires_thetaevolve_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "thetaevolve_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_improvevolve_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.IMPROVEVOLVE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.improvevolve_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_improvevolve_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.improvevolve_boundary_record()
    record["claim_ready"] = True
    sidecar = tmp_path / paper_manifest.IMPROVEVOLVE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "improvevolve_boundary_claim_ready_overclaim" in codes


def test_validate_paper_manifest_requires_improvevolve_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "improvevolve_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_madevolve_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.MADEVOLVE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.madevolve_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_madevolve_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.madevolve_boundary_record()
    record["claim_ready"] = True
    sidecar = tmp_path / paper_manifest.MADEVOLVE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "madevolve_boundary_claim_ready_overclaim" in codes


def test_validate_paper_manifest_requires_madevolve_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "madevolve_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_causalevolve_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.CAUSALEVOLVE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.causalevolve_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_causalevolve_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.causalevolve_boundary_record()
    record["claim_ready"] = True
    sidecar = tmp_path / paper_manifest.CAUSALEVOLVE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "causalevolve_boundary_claim_ready_overclaim" in codes


def test_validate_paper_manifest_requires_causalevolve_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "causalevolve_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_deepevolve_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.DEEPEVOLVE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.deepevolve_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_deepevolve_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.deepevolve_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["cross_file_coding_ready"] = True
    sidecar = tmp_path / paper_manifest.DEEPEVOLVE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "deepevolve_boundary_claim_ready_overclaim" in codes
    assert "deepevolve_boundary_local_evidence_cross_file_coding_ready_overclaim" in codes


def test_validate_paper_manifest_requires_deepevolve_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "deepevolve_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_magellan_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.MAGELLAN_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.magellan_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_magellan_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.magellan_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["compiler_pass_runner_ready"] = True
    sidecar = tmp_path / paper_manifest.MAGELLAN_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "magellan_boundary_claim_ready_overclaim" in codes
    assert "magellan_boundary_local_evidence_compiler_pass_runner_ready_overclaim" in codes


def test_validate_paper_manifest_requires_magellan_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "magellan_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_archagent_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.ARCHAGENT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.archagent_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_archagent_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.archagent_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["champsim_runner_ready"] = True
    sidecar = tmp_path / paper_manifest.ARCHAGENT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "archagent_boundary_claim_ready_overclaim" in codes
    assert "archagent_boundary_local_evidence_champsim_runner_ready_overclaim" in codes


def test_validate_paper_manifest_requires_archagent_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "archagent_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_multiagent_learning_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.MULTIAGENT_LEARNING_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.multiagent_learning_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_multiagent_learning_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.multiagent_learning_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["cfr_candidate_schema_ready"] = True
    sidecar = tmp_path / paper_manifest.MULTIAGENT_LEARNING_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "multiagent_learning_boundary_claim_ready_overclaim" in codes
    assert (
        "multiagent_learning_boundary_local_evidence_cfr_candidate_schema_ready_overclaim"
        in codes
    )


def test_validate_paper_manifest_requires_multiagent_learning_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "multiagent_learning_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_sample_efficiency_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.SAMPLE_EFFICIENCY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.sample_efficiency_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_sample_efficiency_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.sample_efficiency_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "benchmark_sample_efficiency_ready"
    record["missing_evidence"]["target_hit_sample_index"] = "recorded"
    sidecar = tmp_path / paper_manifest.SAMPLE_EFFICIENCY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "sample_efficiency_boundary_claim_ready_overclaim" in codes
    assert "sample_efficiency_boundary_invalid_boundary_status" in codes
    assert "sample_efficiency_boundary_invalid_missing_evidence_target_hit_sample_index" in codes


def test_validate_paper_manifest_requires_sample_efficiency_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "sample_efficiency_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_parallel_evaluation_readiness_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PARALLEL_EVALUATION_READINESS_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.parallel_evaluation_readiness_boundary_record(), indent=2
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_parallel_evaluation_readiness_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.parallel_evaluation_readiness_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "async_parallel_evaluation_ready"
    record["missing_evidence"]["candidate_level_async_evaluation_queue"] = "recorded"
    sidecar = tmp_path / paper_manifest.PARALLEL_EVALUATION_READINESS_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "parallel_evaluation_readiness_boundary_claim_ready_overclaim" in codes
    assert "parallel_evaluation_readiness_boundary_invalid_boundary_status" in codes
    assert (
        "parallel_evaluation_readiness_boundary_invalid_missing_evidence_candidate_level_async_evaluation_queue"
        in codes
    )


def test_validate_paper_manifest_requires_parallel_evaluation_readiness_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "parallel_evaluation_readiness_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_expensive_evaluation_budget_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.EXPENSIVE_EVALUATION_BUDGET_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.expensive_evaluation_budget_boundary_record(), indent=2
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_expensive_evaluation_budget_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.expensive_evaluation_budget_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "compute_hour_accelerator_budget_ready"
    record["missing_evidence"]["per_candidate_compute_hour_accounting"] = "recorded"
    sidecar = tmp_path / paper_manifest.EXPENSIVE_EVALUATION_BUDGET_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "expensive_evaluation_budget_boundary_claim_ready_overclaim" in codes
    assert "expensive_evaluation_budget_boundary_invalid_boundary_status" in codes
    assert (
        "expensive_evaluation_budget_boundary_invalid_missing_evidence_per_candidate_compute_hour_accounting"
        in codes
    )


def test_validate_paper_manifest_requires_expensive_evaluation_budget_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "expensive_evaluation_budget_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_distributed_pipeline_topology_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.DISTRIBUTED_PIPELINE_TOPOLOGY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.distributed_pipeline_topology_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_distributed_pipeline_topology_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.distributed_pipeline_topology_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "async_distributed_topology_ready"
    record["source_section_ids"] = ["2.4"]
    record["missing_evidence"]["async_controller_queues"] = "recorded"
    sidecar = tmp_path / paper_manifest.DISTRIBUTED_PIPELINE_TOPOLOGY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "distributed_pipeline_topology_boundary_claim_ready_overclaim" in codes
    assert "distributed_pipeline_topology_boundary_invalid_boundary_status" in codes
    assert "distributed_pipeline_topology_boundary_invalid_source_section_ids" in codes
    assert (
        "distributed_pipeline_topology_boundary_invalid_missing_evidence_async_controller_queues"
        in codes
    )


def test_validate_paper_manifest_requires_distributed_pipeline_topology_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "distributed_pipeline_topology_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_workspace_materialization_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.WORKSPACE_MATERIALIZATION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.workspace_materialization_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_workspace_materialization_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.workspace_materialization_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "future_topology_surfaces_ready"
    record["source_section_ids"] = ["2.6"]
    record["missing_evidence"]["bulk_directory_operation_diagnostics"] = "recorded"
    sidecar = tmp_path / paper_manifest.WORKSPACE_MATERIALIZATION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "workspace_materialization_boundary_claim_ready_overclaim" in codes
    assert "workspace_materialization_boundary_invalid_boundary_status" in codes
    assert "workspace_materialization_boundary_invalid_source_section_ids" in codes
    assert (
        "workspace_materialization_boundary_invalid_missing_evidence_bulk_directory_operation_diagnostics"
        in codes
    )


def test_validate_paper_manifest_requires_workspace_materialization_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "workspace_materialization_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_whole_run_source_workspace_integrity_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.WHOLE_RUN_SOURCE_WORKSPACE_INTEGRITY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.whole_run_source_workspace_integrity_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_whole_run_source_workspace_integrity_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.whole_run_source_workspace_integrity_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "whole_run_database_ready"
    record["missing_evidence"]["durable_whole_run_query_surface"] = "recorded"
    sidecar = tmp_path / paper_manifest.WHOLE_RUN_SOURCE_WORKSPACE_INTEGRITY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "whole_run_source_workspace_integrity_boundary_claim_ready_overclaim" in codes
    assert "whole_run_source_workspace_integrity_boundary_invalid_boundary_status" in codes
    assert (
        "whole_run_source_workspace_integrity_boundary_invalid_missing_evidence_durable_whole_run_query_surface"
        in codes
    )


def test_validate_paper_manifest_requires_whole_run_source_workspace_integrity_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "whole_run_source_workspace_integrity_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_repeated_sampling_baseline_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.REPEATED_SAMPLING_BASELINE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.repeated_sampling_baseline_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_repeated_sampling_baseline_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.repeated_sampling_baseline_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "controlled_comparator_ready"
    record["missing_evidence"]["budget_parity_validation"] = "recorded"
    sidecar = tmp_path / paper_manifest.REPEATED_SAMPLING_BASELINE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "repeated_sampling_baseline_boundary_claim_ready_overclaim" in codes
    assert "repeated_sampling_baseline_boundary_invalid_boundary_status" in codes
    assert (
        "repeated_sampling_baseline_boundary_invalid_missing_evidence_budget_parity_validation"
        in codes
    )


def test_validate_paper_manifest_requires_repeated_sampling_baseline_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "repeated_sampling_baseline_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_sampling_balance_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.SAMPLING_BALANCE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.sampling_balance_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_sampling_balance_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.sampling_balance_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "calibrated_alphaevolve_sampling_balance"
    record["missing_evidence"]["equal_budget_strategy_comparisons"] = "recorded"
    sidecar = tmp_path / paper_manifest.SAMPLING_BALANCE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "sampling_balance_boundary_claim_ready_overclaim" in codes
    assert "sampling_balance_boundary_invalid_boundary_status" in codes
    assert (
        "sampling_balance_boundary_invalid_missing_evidence_equal_budget_strategy_comparisons"
        in codes
    )


def test_validate_paper_manifest_requires_sampling_balance_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "sampling_balance_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_gemini_provider_parity_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.GEMINI_PROVIDER_PARITY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.gemini_provider_parity_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_gemini_provider_parity_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.gemini_provider_parity_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "first_class_gemini_provider_ready"
    record["missing_evidence"]["built_in_google_gemini_adapter"] = "recorded"
    sidecar = tmp_path / paper_manifest.GEMINI_PROVIDER_PARITY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "gemini_provider_parity_boundary_claim_ready_overclaim" in codes
    assert "gemini_provider_parity_boundary_invalid_boundary_status" in codes
    assert (
        "gemini_provider_parity_boundary_invalid_missing_evidence_built_in_google_gemini_adapter"
        in codes
    )


def test_validate_paper_manifest_requires_gemini_provider_parity_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "gemini_provider_parity_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_gemini_self_training_loop_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.GEMINI_SELF_TRAINING_LOOP_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.gemini_self_training_loop_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_gemini_self_training_loop_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.gemini_self_training_loop_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "gemini_self_training_loop_ready"
    record["missing_evidence"]["gemini_training_workload_identity"] = "recorded"
    sidecar = tmp_path / paper_manifest.GEMINI_SELF_TRAINING_LOOP_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "gemini_self_training_loop_boundary_claim_ready_overclaim" in codes
    assert "gemini_self_training_loop_boundary_invalid_boundary_status" in codes
    assert (
        "gemini_self_training_loop_boundary_invalid_missing_evidence_gemini_training_workload_identity"
        in codes
    )


def test_validate_paper_manifest_requires_gemini_self_training_loop_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "gemini_self_training_loop_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_hardware_rtl_eda_evidence_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.HARDWARE_RTL_EDA_EVIDENCE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.hardware_rtl_eda_evidence_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_hardware_rtl_eda_evidence_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.hardware_rtl_eda_evidence_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "hardware_rtl_eda_artifacts_ready"
    record["missing_evidence"]["source_rtl_or_verilog_artifact"] = "recorded"
    sidecar = tmp_path / paper_manifest.HARDWARE_RTL_EDA_EVIDENCE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "hardware_rtl_eda_evidence_boundary_claim_ready_overclaim" in codes
    assert "hardware_rtl_eda_evidence_boundary_invalid_boundary_status" in codes
    assert (
        "hardware_rtl_eda_evidence_boundary_invalid_missing_evidence_source_rtl_or_verilog_artifact"
        in codes
    )


def test_validate_paper_manifest_requires_hardware_rtl_eda_evidence_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "hardware_rtl_eda_evidence_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_hardware_rewrite_artifact_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.HARDWARE_REWRITE_ARTIFACT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.hardware_rewrite_artifact_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_hardware_rewrite_artifact_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.hardware_rewrite_artifact_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "hardware_rewrite_artifacts_ready"
    record["missing_evidence"]["source_verilog_artifact"] = "recorded"
    sidecar = tmp_path / paper_manifest.HARDWARE_REWRITE_ARTIFACT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "hardware_rewrite_artifact_boundary_claim_ready_overclaim" in codes
    assert "hardware_rewrite_artifact_boundary_invalid_boundary_status" in codes
    assert (
        "hardware_rewrite_artifact_boundary_invalid_missing_evidence_source_verilog_artifact"
        in codes
    )


def test_validate_paper_manifest_requires_hardware_rewrite_artifact_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "hardware_rewrite_artifact_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_hardware_contribution_attribution_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = (
        tmp_path / paper_manifest.HARDWARE_CONTRIBUTION_ATTRIBUTION_BOUNDARY_FILE
    )
    sidecar.write_text(
        json.dumps(
            paper_manifest.hardware_contribution_attribution_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_hardware_contribution_attribution_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.hardware_contribution_attribution_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "gemini_tpu_attribution_artifacts_ready"
    record["missing_evidence"]["gemini_model_family_identity"] = "recorded"
    sidecar = (
        tmp_path / paper_manifest.HARDWARE_CONTRIBUTION_ATTRIBUTION_BOUNDARY_FILE
    )
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert (
        "hardware_contribution_attribution_boundary_claim_ready_overclaim"
        in codes
    )
    assert (
        "hardware_contribution_attribution_boundary_invalid_boundary_status"
        in codes
    )
    assert (
        "hardware_contribution_attribution_boundary_invalid_missing_evidence_gemini_model_family_identity"
        in codes
    )


def test_validate_paper_manifest_requires_hardware_contribution_attribution_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "hardware_contribution_attribution_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_compiler_ir_reference_check_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.COMPILER_IR_REFERENCE_CHECK_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.compiler_ir_reference_check_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_compiler_ir_reference_check_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.compiler_ir_reference_check_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "compiler_ir_reference_check_artifacts_ready"
    record["missing_evidence"]["per_edit_reference_check_outputs"] = "recorded"
    sidecar = tmp_path / paper_manifest.COMPILER_IR_REFERENCE_CHECK_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "compiler_ir_reference_check_boundary_claim_ready_overclaim" in codes
    assert "compiler_ir_reference_check_boundary_invalid_boundary_status" in codes
    assert (
        "compiler_ir_reference_check_boundary_invalid_missing_evidence_per_edit_reference_check_outputs"
        in codes
    )


def test_validate_paper_manifest_requires_compiler_ir_reference_check_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "compiler_ir_reference_check_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_compiler_adoption_path_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.COMPILER_ADOPTION_PATH_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.compiler_adoption_path_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_compiler_adoption_path_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.compiler_adoption_path_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "compiler_adoption_artifacts_ready"
    record["missing_evidence"]["reviewer_signoff_file"] = "recorded"
    sidecar = tmp_path / paper_manifest.COMPILER_ADOPTION_PATH_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "compiler_adoption_path_boundary_claim_ready_overclaim" in codes
    assert "compiler_adoption_path_boundary_invalid_boundary_status" in codes
    assert (
        "compiler_adoption_path_boundary_invalid_missing_evidence_reviewer_signoff_file"
        in codes
    )


def test_validate_paper_manifest_requires_compiler_adoption_path_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "compiler_adoption_path_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_compiler_stack_context_boundary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.COMPILER_STACK_CONTEXT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.compiler_stack_context_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_compiler_stack_context_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.compiler_stack_context_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "flashattention_stack_artifacts_ready"
    record["missing_evidence"]["lowered_ir_artifact"] = "recorded"
    sidecar = tmp_path / paper_manifest.COMPILER_STACK_CONTEXT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "compiler_stack_context_boundary_claim_ready_overclaim" in codes
    assert "compiler_stack_context_boundary_invalid_boundary_status" in codes
    assert (
        "compiler_stack_context_boundary_invalid_missing_evidence_lowered_ir_artifact"
        in codes
    )


def test_validate_paper_manifest_requires_compiler_stack_context_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "compiler_stack_context_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_ramsey_numbers_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.RAMSEY_NUMBERS_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.ramsey_numbers_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_ramsey_numbers_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.ramsey_numbers_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["graph_verifier_ready"] = True
    sidecar = tmp_path / paper_manifest.RAMSEY_NUMBERS_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "ramsey_numbers_boundary_claim_ready_overclaim" in codes
    assert "ramsey_numbers_boundary_local_evidence_graph_verifier_ready_overclaim" in codes


def test_validate_paper_manifest_requires_ramsey_numbers_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "ramsey_numbers_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_combinatorics_berczy_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.COMBINATORICS_BERCZY_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.combinatorics_berczy_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_combinatorics_berczy_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.combinatorics_berczy_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["bipartite_harness_ready"] = True
    sidecar = tmp_path / paper_manifest.COMBINATORICS_BERCZY_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "combinatorics_berczy_boundary_claim_ready_overclaim" in codes
    assert (
        "combinatorics_berczy_boundary_local_evidence_bipartite_harness_ready_overclaim"
        in codes
    )


def test_validate_paper_manifest_requires_combinatorics_berczy_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "combinatorics_berczy_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_ttt_discover_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.TTT_DISCOVER_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.ttt_discover_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_ttt_discover_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.ttt_discover_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["policy_update_loop_ready"] = True
    sidecar = tmp_path / paper_manifest.TTT_DISCOVER_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "ttt_discover_boundary_claim_ready_overclaim" in codes
    assert (
        "ttt_discover_boundary_local_evidence_policy_update_loop_ready_overclaim"
        in codes
    )


def test_validate_paper_manifest_requires_ttt_discover_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "ttt_discover_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_bruhat_intervals_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.BRUHAT_INTERVALS_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.bruhat_intervals_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_bruhat_intervals_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.bruhat_intervals_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["bruhat_order_verifier_ready"] = True
    sidecar = tmp_path / paper_manifest.BRUHAT_INTERVALS_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "bruhat_intervals_boundary_claim_ready_overclaim" in codes
    assert (
        "bruhat_intervals_boundary_local_evidence_bruhat_order_verifier_ready_overclaim"
        in codes
    )


def test_validate_paper_manifest_requires_bruhat_intervals_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "bruhat_intervals_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_fault2flow_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.FAULT2FLOW_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.fault2flow_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_fault2flow_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.fault2flow_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["n8n_workflow_builder_ready"] = True
    sidecar = tmp_path / paper_manifest.FAULT2FLOW_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "fault2flow_boundary_claim_ready_overclaim" in codes
    assert (
        "fault2flow_boundary_local_evidence_n8n_workflow_builder_ready_overclaim"
        in codes
    )


def test_validate_paper_manifest_requires_fault2flow_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "fault2flow_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_global_nlp_optimization_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.GLOBAL_NLP_OPTIMIZATION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.global_nlp_optimization_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_global_nlp_optimization_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.global_nlp_optimization_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["xpress_runner_ready"] = True
    sidecar = tmp_path / paper_manifest.GLOBAL_NLP_OPTIMIZATION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "global_nlp_optimization_boundary_claim_ready_overclaim" in codes
    assert (
        "global_nlp_optimization_boundary_local_evidence_xpress_runner_ready_overclaim"
        in codes
    )


def test_validate_paper_manifest_requires_global_nlp_optimization_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "global_nlp_optimization_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_autoconvolution_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.AUTOCONVOLUTION_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.autoconvolution_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_autoconvolution_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.autoconvolution_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["formula3_checker_ready"] = True
    sidecar = tmp_path / paper_manifest.AUTOCONVOLUTION_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "autoconvolution_boundary_claim_ready_overclaim" in codes
    assert (
        "autoconvolution_boundary_local_evidence_formula3_checker_ready_overclaim"
        in codes
    )


def test_validate_paper_manifest_requires_autoconvolution_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "autoconvolution_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_sums_differences_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.SUMS_DIFFERENCES_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.sums_differences_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_sums_differences_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.sums_differences_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["theta_recomputation_ready"] = True
    sidecar = tmp_path / paper_manifest.SUMS_DIFFERENCES_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "sums_differences_boundary_claim_ready_overclaim" in codes
    assert (
        "sums_differences_boundary_local_evidence_theta_recomputation_ready_overclaim"
        in codes
    )


def test_validate_paper_manifest_requires_sums_differences_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "sums_differences_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_sums_differences_sequence_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.SUMS_DIFFERENCES_SEQUENCE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.sums_differences_sequence_boundary_record(), indent=2
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_sums_differences_sequence_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.sums_differences_sequence_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["theta0_recomputation_ready"] = True
    sidecar = tmp_path / paper_manifest.SUMS_DIFFERENCES_SEQUENCE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "sums_differences_sequence_boundary_claim_ready_overclaim" in codes
    assert (
        "sums_differences_sequence_boundary_local_evidence_theta0_recomputation_ready_overclaim"
        in codes
    )


def test_validate_paper_manifest_requires_sums_differences_sequence_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "sums_differences_sequence_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_ucb1_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.UCB1_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.ucb1_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_ucb1_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.ucb1_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["regret_report_ready"] = True
    sidecar = tmp_path / paper_manifest.UCB1_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "ucb1_boundary_claim_ready_overclaim" in codes
    assert "ucb1_boundary_local_evidence_regret_report_ready_overclaim" in codes


def test_validate_paper_manifest_requires_ucb1_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "ucb1_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_alphaevolve_2026_impact_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_2026_IMPACT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.alphaevolve_2026_impact_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_alphaevolve_2026_impact_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.alphaevolve_2026_impact_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["spanner_fixture_ready"] = True
    sidecar = tmp_path / paper_manifest.ALPHAEVOLVE_2026_IMPACT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_2026_impact_boundary_claim_ready_overclaim" in codes
    assert (
        "alphaevolve_2026_impact_boundary_local_evidence_spanner_fixture_ready_overclaim"
        in codes
    )


def test_validate_paper_manifest_requires_alphaevolve_2026_impact_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "alphaevolve_2026_impact_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_bilateral_trade_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.BILATERAL_TRADE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.bilateral_trade_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_bilateral_trade_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.bilateral_trade_boundary_record()
    record["claim_ready"] = True
    record["local_evidence"]["gft_evaluator_ready"] = True
    sidecar = tmp_path / paper_manifest.BILATERAL_TRADE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "bilateral_trade_boundary_claim_ready_overclaim" in codes
    assert "bilateral_trade_boundary_local_evidence_gft_evaluator_ready_overclaim" in codes


def test_validate_paper_manifest_requires_bilateral_trade_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "bilateral_trade_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_evaluator_oracle_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.EVALUATOR_ORACLE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.evaluator_oracle_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_evaluator_oracle_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.evaluator_oracle_boundary_record()
    record["claim_ready"] = True
    record["source_section_ids"] = ["2.3"]
    sidecar = tmp_path / paper_manifest.EVALUATOR_ORACLE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "evaluator_oracle_boundary_claim_ready_overclaim" in codes
    assert "evaluator_oracle_boundary_invalid_source_section_ids" in codes


def test_validate_paper_manifest_requires_evaluator_oracle_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "evaluator_oracle_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_automated_evaluator_scope_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.AUTOMATED_EVALUATOR_SCOPE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.automated_evaluator_scope_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_automated_evaluator_scope_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.automated_evaluator_scope_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "robust_evaluator_environment_ready"
    record["source_section_ids"] = ["2.1"]
    record["missing_evidence"]["robust_evaluator_environment_fixture"] = "recorded"
    sidecar = tmp_path / paper_manifest.AUTOMATED_EVALUATOR_SCOPE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "automated_evaluator_scope_boundary_claim_ready_overclaim" in codes
    assert "automated_evaluator_scope_boundary_invalid_boundary_status" in codes
    assert "automated_evaluator_scope_boundary_invalid_source_section_ids" in codes
    assert (
        "automated_evaluator_scope_boundary_invalid_missing_evidence_robust_evaluator_environment_fixture"
        in codes
    )


def test_validate_paper_manifest_requires_automated_evaluator_scope_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "automated_evaluator_scope_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_embedded_evaluator_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.EMBEDDED_EVALUATOR_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.embedded_evaluator_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_embedded_evaluator_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.embedded_evaluator_boundary_record()
    record["claim_ready"] = True
    record["source_section_ids"] = ["2.1"]
    record["source_figure_ids"] = ["Figure 2"]
    sidecar = tmp_path / paper_manifest.EMBEDDED_EVALUATOR_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "embedded_evaluator_boundary_claim_ready_overclaim" in codes
    assert "embedded_evaluator_boundary_invalid_source_section_ids" in codes
    assert "embedded_evaluator_boundary_invalid_source_figure_ids" in codes


def test_validate_paper_manifest_requires_embedded_evaluator_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "embedded_evaluator_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_figure3_supervised_exhibit_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.FIGURE3_SUPERVISED_EXHIBIT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.figure3_supervised_exhibit_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_figure3_supervised_exhibit_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.figure3_supervised_exhibit_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "figure3_supervised_exhibit_reproduced"
    record["source_section_ids"] = ["2.4"]
    record["source_figure_ids"] = ["Figure 2"]
    record["missing_evidence"]["assembled_prompt_excerpt_artifact"] = "recorded"
    sidecar = tmp_path / paper_manifest.FIGURE3_SUPERVISED_EXHIBIT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "figure3_supervised_exhibit_boundary_claim_ready_overclaim" in codes
    assert "figure3_supervised_exhibit_boundary_invalid_boundary_status" in codes
    assert "figure3_supervised_exhibit_boundary_invalid_source_section_ids" in codes
    assert "figure3_supervised_exhibit_boundary_invalid_source_figure_ids" in codes
    assert (
        "figure3_supervised_exhibit_boundary_invalid_missing_evidence_assembled_prompt_excerpt_artifact"
        in codes
    )


def test_validate_paper_manifest_requires_figure3_supervised_exhibit_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "figure3_supervised_exhibit_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_figure6_scheduling_exhibit_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.FIGURE6_SCHEDULING_EXHIBIT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.figure6_scheduling_exhibit_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_figure6_scheduling_exhibit_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.figure6_scheduling_exhibit_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "figure6_exhibit_artifacts_ready"
    record["missing_evidence"]["rendered_heatmap_artifact_hash"] = "recorded"
    sidecar = tmp_path / paper_manifest.FIGURE6_SCHEDULING_EXHIBIT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "figure6_scheduling_exhibit_boundary_claim_ready_overclaim" in codes
    assert "figure6_scheduling_exhibit_boundary_invalid_boundary_status" in codes
    assert (
        "figure6_scheduling_exhibit_boundary_invalid_missing_evidence_rendered_heatmap_artifact_hash"
        in codes
    )


def test_validate_paper_manifest_requires_figure6_scheduling_exhibit_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "figure6_scheduling_exhibit_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_figure7_pallas_tiling_exhibit_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.FIGURE7_PALLAS_TILING_EXHIBIT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.figure7_pallas_tiling_exhibit_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_figure7_pallas_tiling_exhibit_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.figure7_pallas_tiling_exhibit_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "figure7_exhibit_artifacts_ready"
    record["missing_evidence"]["rendered_diagram_artifact_hash"] = "recorded"
    sidecar = tmp_path / paper_manifest.FIGURE7_PALLAS_TILING_EXHIBIT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "figure7_pallas_tiling_exhibit_boundary_claim_ready_overclaim" in codes
    assert "figure7_pallas_tiling_exhibit_boundary_invalid_boundary_status" in codes
    assert (
        "figure7_pallas_tiling_exhibit_boundary_invalid_missing_evidence_rendered_diagram_artifact_hash"
        in codes
    )


def test_validate_paper_manifest_requires_figure7_pallas_tiling_exhibit_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "figure7_pallas_tiling_exhibit_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_process_exhibit_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PROCESS_EXHIBIT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.process_exhibit_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_process_exhibit_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.process_exhibit_boundary_record()
    record["claim_ready"] = True
    record["source_section_ids"] = ["2.1"]
    sidecar = tmp_path / paper_manifest.PROCESS_EXHIBIT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "process_exhibit_boundary_claim_ready_overclaim" in codes
    assert "process_exhibit_boundary_invalid_source_section_ids" in codes


def test_validate_paper_manifest_requires_process_exhibit_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "process_exhibit_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_proposal_lifecycle_audit_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.PROPOSAL_LIFECYCLE_AUDIT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.proposal_lifecycle_audit_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_proposal_lifecycle_audit_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.proposal_lifecycle_audit_boundary_record()
    record["claim_ready"] = True
    sidecar = tmp_path / paper_manifest.PROPOSAL_LIFECYCLE_AUDIT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "proposal_lifecycle_audit_boundary_claim_ready_overclaim" in codes


def test_validate_paper_manifest_requires_proposal_lifecycle_audit_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "proposal_lifecycle_audit_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_incorrect_suggestion_audit_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.INCORRECT_SUGGESTION_AUDIT_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.incorrect_suggestion_audit_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_incorrect_suggestion_audit_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.incorrect_suggestion_audit_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "publication_strength_ready"
    record["missing_evidence"]["audited_false_acceptance_rate"] = "recorded"
    sidecar = tmp_path / paper_manifest.INCORRECT_SUGGESTION_AUDIT_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "incorrect_suggestion_audit_boundary_claim_ready_overclaim" in codes
    assert "incorrect_suggestion_audit_boundary_invalid_boundary_status" in codes
    assert (
        "incorrect_suggestion_audit_boundary_invalid_missing_evidence_audited_false_acceptance_rate"
        in codes
    )


def test_validate_paper_manifest_requires_incorrect_suggestion_audit_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "incorrect_suggestion_audit_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_evaluation_cascade_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.EVALUATION_CASCADE_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.evaluation_cascade_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_evaluation_cascade_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.evaluation_cascade_boundary_record()
    record["claim_ready"] = True
    record["source_section_ids"] = ["2.3"]
    sidecar = tmp_path / paper_manifest.EVALUATION_CASCADE_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "evaluation_cascade_boundary_claim_ready_overclaim" in codes
    assert "evaluation_cascade_boundary_invalid_source_section_ids" in codes


def test_validate_paper_manifest_requires_evaluation_cascade_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "evaluation_cascade_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_cascade_hypothesis_test_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.CASCADE_HYPOTHESIS_TEST_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(
            paper_manifest.cascade_hypothesis_test_boundary_record(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_cascade_hypothesis_test_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.cascade_hypothesis_test_boundary_record()
    record["claim_ready"] = True
    record["boundary_status"] = "benchmark_calibrated_hypothesis_cascade_ready"
    record["source_section_ids"] = ["2.3"]
    record["missing_evidence"]["benchmark_calibrated_thresholds"] = "recorded"
    sidecar = tmp_path / paper_manifest.CASCADE_HYPOTHESIS_TEST_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "cascade_hypothesis_test_boundary_claim_ready_overclaim" in codes
    assert "cascade_hypothesis_test_boundary_invalid_boundary_status" in codes
    assert "cascade_hypothesis_test_boundary_invalid_source_section_ids" in codes
    assert (
        "cascade_hypothesis_test_boundary_invalid_missing_evidence_benchmark_calibrated_thresholds"
        in codes
    )


def test_validate_paper_manifest_requires_cascade_hypothesis_test_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "cascade_hypothesis_test_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_controller_backtracking_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    sidecar = tmp_path / paper_manifest.CONTROLLER_BACKTRACKING_BOUNDARY_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.controller_backtracking_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_controller_backtracking_boundary_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    record = paper_manifest.controller_backtracking_boundary_record()
    record["claim_ready"] = True
    sidecar = tmp_path / paper_manifest.CONTROLLER_BACKTRACKING_BOUNDARY_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "controller_backtracking_boundary_claim_ready_overclaim" in codes


def test_validate_paper_manifest_requires_controller_backtracking_boundary_at_repo_root(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "controller_backtracking_boundary_manifest_missing" in codes


def test_validate_paper_manifest_accepts_math_outcome_boundary_sidecars(monkeypatch, tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_math_outcome_boundary_sidecars(tmp_path)
    drifted = paper_manifest.alphaevolve_math_starting_construction_boundary()
    drifted["status"] = "recorded"
    monkeypatch.setattr(
        paper_manifest,
        "alphaevolve_math_starting_construction_boundary",
        lambda: drifted,
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_math_outcome_boundary_sidecar_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_math_outcome_boundary_sidecars(tmp_path)
    starting_path = tmp_path / paper_manifest.MATH_STARTING_CONSTRUCTION_BOUNDARY_FILE
    starting = json.loads(starting_path.read_text(encoding="utf-8"))
    starting["status"] = "recorded"
    starting["source_section_ids"] = ["3.1"]
    starting["missing_evidence"]["baseline_metric_values"] = "recorded"
    starting_path.write_text(json.dumps(starting, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "math_starting_construction_invalid_starting_status" in codes
    assert "math_starting_construction_invalid_starting_source_section_ids" in codes
    assert "math_starting_construction_invalid_starting_missing_baseline_metric_values" in codes


def test_validate_paper_manifest_requires_math_outcome_boundary_sidecars_at_repo_root(
    monkeypatch, tmp_path
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "math_outcome_boundary_manifest_missing" in codes
    assert "math_starting_construction_boundary_manifest_missing" in codes
    assert "math_heuristic_handoff_boundary_manifest_missing" in codes
    assert "math_heuristic_stage_sequence_boundary_manifest_missing" in codes


def test_rehydrate_paper_cache_downloads_missing_pdf_and_validates_hash(tmp_path, monkeypatch):
    content = _valid_pdf_bytes()
    row = _row(tmp_path, content=content)
    (tmp_path / row["file"]).unlink()
    _write_manifest(tmp_path, [row])

    def fake_urlopen(request, timeout):
        assert request.full_url == row["url"]
        assert timeout == 60.0
        response = BytesIO(content)
        response.status = 200
        return response

    monkeypatch.setattr(paper_manifest, "urlopen", fake_urlopen)

    report = rehydrate_paper_cache(tmp_path)

    assert report.ok is True
    assert report.downloaded_count == 1
    assert report.verified_existing_count == 0
    assert report.results[0].status == "downloaded"
    assert validate_paper_manifest(tmp_path, require_local_pdfs=True).ok is True


def test_rehydrate_paper_cache_skips_existing_matching_pdf(tmp_path, monkeypatch):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])

    def fail_urlopen(request, timeout):
        raise AssertionError("matching local PDFs should not be downloaded")

    monkeypatch.setattr(paper_manifest, "urlopen", fail_urlopen)

    report = rehydrate_paper_cache(tmp_path)

    assert report.ok is True
    assert report.downloaded_count == 0
    assert report.verified_existing_count == 1
    assert report.results[0].status == "verified_existing"


def test_rehydrate_paper_cache_force_redownloads_matching_pdf(tmp_path, monkeypatch):
    content = _valid_pdf_bytes()
    row = _row(tmp_path, content=content)
    _write_manifest(tmp_path, [row])
    calls = 0

    def fake_urlopen(request, timeout):
        nonlocal calls
        calls += 1
        response = BytesIO(content)
        response.status = 200
        return response

    monkeypatch.setattr(paper_manifest, "urlopen", fake_urlopen)

    report = rehydrate_paper_cache(tmp_path, force=True)

    assert report.ok is True
    assert calls == 1
    assert report.downloaded_count == 1
    assert (tmp_path / row["file"]).read_bytes() == content


def test_paper_manifest_rehydrate_json_reports_redacted_network_failure(tmp_path, monkeypatch, capsys):
    row = _row(tmp_path)
    (tmp_path / row["file"]).unlink()
    _write_manifest(tmp_path, [row])

    def fake_urlopen(request, timeout):
        raise OSError("network down api_key=sk-proj_paperrehydrate_secret_1234567890")  # pragma: allowlist secret

    monkeypatch.setattr(paper_manifest, "urlopen", fake_urlopen)

    exit_code = main(["--root", str(tmp_path), "--rehydrate", "--json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert exit_code == 1
    assert data["failed_count"] == 1
    assert data["results"][0]["status"] == "failed"
    assert "[REDACTED]" in captured.out
    assert "sk-proj_paperrehydrate_secret_1234567890" not in captured.out


def test_validate_paper_manifest_reports_missing_pdf_only_when_required(tmp_path):
    row = _row(tmp_path)
    (tmp_path / row["file"]).unlink()
    _write_manifest(tmp_path, [row])

    optional_report = validate_paper_manifest(tmp_path)
    required_report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    assert optional_report.ok is True
    assert optional_report.local_missing_count == 1
    assert optional_report.availability[0].local_status == "missing"
    assert required_report.ok is False
    assert [issue.code for issue in required_report.issues] == ["missing_pdf"]


def test_validate_paper_manifest_rejects_grouped_sha256(tmp_path):
    grouped = "f092c8cb-d65da899-51ee6496-374da9a5-4963f903-5758c25a-c6e4625f-506df9ad"
    row = _row(tmp_path, sha256=grouped)
    _write_manifest(tmp_path, [row])

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "invalid_sha256" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_rejects_csv_json_mismatch(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    csv_path = tmp_path / "papers" / "download_manifest.csv"
    text = csv_path.read_text(encoding="utf-8").replace("AlphaEvolve", "DifferentTitle", 1)
    csv_path.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "csv_json_mismatch" in {issue.code for issue in report.issues}


def test_paper_manifest_cli_returns_failure_for_invalid_manifest(tmp_path, capsys):
    row = _row(tmp_path, bytes_value=1)
    _write_manifest(tmp_path, [row])

    exit_code = main(["--root", str(tmp_path), "--require-local-pdfs"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "byte_count_mismatch" in captured.out


def test_paper_manifest_cli_reports_redacted_local_pdf_stat_error(tmp_path, monkeypatch, capsys):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    target = tmp_path / row["file"]
    real_exists = Path.exists
    real_stat = Path.stat

    def fake_exists(path):
        if path == target:
            return True
        return real_exists(path)

    def fake_stat(path, *args, **kwargs):
        if path == target:
            raise PermissionError("cannot stat api_key=sk-proj_paperpdfstatsecret1234567890")
        return real_stat(path, *args, **kwargs)

    monkeypatch.setattr(Path, "exists", fake_exists)
    monkeypatch.setattr(Path, "stat", fake_stat)

    exit_code = main(["--root", str(tmp_path), "--require-local-pdfs"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "local_pdf_stat_error" in captured.out
    assert "papers/2506.13131__AlphaEvolve.pdf" in captured.out
    assert "[REDACTED]" in captured.out
    assert "sk-proj_paperpdfstatsecret1234567890" not in captured.out


def test_paper_manifest_json_reports_redacted_local_pdf_read_error(tmp_path, monkeypatch, capsys):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    target = tmp_path / row["file"]
    real_open = Path.open

    def fake_open(path, *args, **kwargs):
        if path == target:
            raise PermissionError("cannot read api_key=sk-proj_paperpdfreadsecret1234567890")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fake_open)

    exit_code = main(["--root", str(tmp_path), "--require-local-pdfs", "--json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert exit_code == 1
    assert data["issues"][0]["code"] == "local_pdf_read_error"
    assert data["issues"][0]["row_id"] == "2506.13131"
    assert "papers/2506.13131__AlphaEvolve.pdf" in data["issues"][0]["message"]
    assert "[REDACTED]" in data["issues"][0]["message"]
    assert "sk-proj_paperpdfreadsecret1234567890" not in captured.out


def test_validate_paper_manifest_reports_directory_shaped_pdf(tmp_path):
    row = _row(tmp_path)
    paper_path = tmp_path / row["file"]
    paper_path.unlink()
    paper_path.mkdir()
    _write_manifest(tmp_path, [row])

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    assert report.ok is False
    assert report.local_present_count == 1
    assert report.availability[0].local_status == "present"
    assert [issue.code for issue in report.issues] == ["local_pdf_not_file"]
    assert report.issues[0].row_id == "2506.13131"


def test_validate_paper_manifest_reports_git_tracked_pdf_status(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "add", row["file"]], cwd=tmp_path, check=True, capture_output=True)

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert report.availability[0].git_tracked is True
    assert "tracked_pdf" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_allows_retained_alphaevolve_pdf(tmp_path):
    source_root = Path(__file__).resolve().parents[1]
    content = (source_root / "papers" / "2506.13131__AlphaEvolve.pdf").read_bytes()
    row = _row(tmp_path, content=content)
    _write_manifest(tmp_path, [row])
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "add", row["file"]], cwd=tmp_path, check=True, capture_output=True)

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.availability[0].git_tracked is True
    assert "tracked_pdf" not in {issue.code for issue in report.issues}


def test_validate_paper_manifest_rejects_unsafe_pdf_paths(tmp_path):
    rows = [
        {
            **_row(
                tmp_path,
                row_id="2506.00001",
                file="papers/safe1.pdf",
                url="https://arxiv.org/pdf/2506.00001.pdf",
            ),
            "file": "papers/CON.pdf",
        },
        {
            **_row(
                tmp_path,
                row_id="2506.00002",
                file="papers/safe2.pdf",
                url="https://arxiv.org/pdf/2506.00002.pdf",
            ),
            "file": "papers/bad\u202egnp.pdf",
        },
        {
            **_row(
                tmp_path,
                row_id="2506.00003",
                file="papers/safe3.pdf",
                url="https://arxiv.org/pdf/2506.00003.pdf",
            ),
            "file": "papers/.hidden.pdf",
        },
    ]
    _write_manifest(tmp_path, rows)

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert [issue.code for issue in report.issues].count("invalid_file_path") == 3


def test_validate_paper_manifest_reports_duplicate_file_targets(tmp_path):
    row = _row(tmp_path, file="papers/shared.pdf")
    duplicate = {
        **row,
        "id": "2506.99999",
        "url": "https://arxiv.org/pdf/2506.99999.pdf",
    }
    _write_manifest(tmp_path, [row, duplicate])

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "duplicate_file_path" in codes
    assert "duplicate_sha256" in codes
    assert report.local_present_count == 1
    assert report.local_unique_file_count == 1


def test_validate_paper_manifest_rejects_arxiv_url_id_mismatch(tmp_path):
    row = _row(
        tmp_path,
        row_id="2506.00001",
        file="papers/2506.00001__Mismatch.pdf",
        url="https://arxiv.org/pdf/2506.99999.pdf",
    )
    _write_manifest(tmp_path, [row])

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "arxiv_url_id_mismatch" in codes


def test_validate_paper_manifest_accepts_versioned_arxiv_url_identity(tmp_path):
    row = _row(
        tmp_path,
        row_id="2506.00001",
        file="papers/2506.00001__Versioned.pdf",
        url="https://arxiv.org/pdf/2506.00001v2",
    )
    _write_manifest(tmp_path, [row])

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_rejects_file_source_id_mismatch(tmp_path):
    row = _row(
        tmp_path,
        row_id="2506.00001",
        file="papers/2506.99999__Wrong.pdf",
        url="https://arxiv.org/pdf/2506.00001.pdf",
    )
    _write_manifest(tmp_path, [row])

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "file_source_id_mismatch" in codes


def test_validate_paper_manifest_rejects_non_arxiv_file_source_id_mismatch(tmp_path):
    row = _row(
        tmp_path,
        row_id="auer-cesa-bianchi-fischer-2002",
        file="papers/ucb1.pdf",
        url="https://web.engr.oregonstate.edu/~afern/classes/cs533/notes/ucb.pdf",
    )
    _write_manifest(tmp_path, [row])

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "file_source_id_mismatch" in codes
    assert "non_arxiv_source_identity_missing" in codes


def test_validate_paper_manifest_accepts_non_arxiv_slug_file_source_id(tmp_path):
    row = _row(
        tmp_path,
        row_id="auer-cesa-bianchi-fischer-2002",
        file="papers/auer-cesa-bianchi-fischer-2002__UCB1.pdf",
        url="https://web.engr.oregonstate.edu/~afern/classes/cs533/notes/ucb.pdf",
    )
    _write_manifest(tmp_path, [row])

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_reports_duplicate_csv_ids_before_comparison(tmp_path):
    row_a = _row(tmp_path, row_id="2506.00001", file="papers/2506.00001__A.pdf", url="https://arxiv.org/pdf/2506.00001.pdf")
    row_b = _row(tmp_path, row_id="2506.00002", file="papers/2506.00002__B.pdf", url="https://arxiv.org/pdf/2506.00002.pdf")
    _write_manifest(tmp_path, [row_a, row_b])
    csv_path = tmp_path / "papers" / "download_manifest.csv"
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    lines[2] = lines[2].replace("2506.00002", "2506.00001", 1)
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "duplicate_csv_id" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_rejects_secret_like_row_ids(tmp_path, capsys):
    secret_id = "api_key=sk-proj_paperid_secret_1234567890"
    row = _row(tmp_path, row_id=secret_id)
    _write_manifest(tmp_path, [row])

    exit_code = main(["--root", str(tmp_path), "--json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert exit_code == 1
    assert "invalid_id" in {issue["code"] for issue in data["issues"]}
    assert "[REDACTED]" in captured.out
    assert secret_id not in captured.out


def test_validate_paper_manifest_checks_readme_badge_count(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    readme = tmp_path / "README.md"
    readme.write_text(
        'LibreEvolve is informed by a local cache of 1 papers.\n'
        '<img src="https://img.shields.io/badge/local%20paper%20cache-24-9E6A03" '
        'alt="Local paper cache">\n',
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    issues = [issue for issue in report.issues if issue.code == "documented_count_conflict"]
    assert len(issues) == 1
    assert "README.md prose=1" in issues[0].message
    assert "README.md badge=24" in issues[0].message
    assert "cache of 1 papers" in issues[0].message


def test_validate_paper_manifest_reports_conflicting_count_sources_with_paths(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    (tmp_path / "README.md").write_text(
        "LibreEvolve is informed by a local cache of 1 papers.\n",
        encoding="utf-8",
    )
    (tmp_path / "papers" / "README.md").write_text(
        "This directory contains 2 locally cached PDFs plus download manifests.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    issues = [issue for issue in report.issues if issue.code == "documented_count_conflict"]
    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert len(issues) == 1
    assert "README.md prose=1" in issues[0].message
    assert "papers/README.md prose=2" in issues[0].message
    assert "contains 2 locally cached PDFs" in issues[0].message
    assert "documented_count_mismatch" not in codes


def test_validate_paper_manifest_accepts_matching_multiple_count_sources(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    (tmp_path / "README.md").write_text(
        'LibreEvolve is informed by a local cache of 1 papers.\n'
        '<img src="https://img.shields.io/badge/local%20paper%20cache-1-9E6A03" '
        'alt="Local paper cache">\n',
        encoding="utf-8",
    )
    (tmp_path / "papers" / "README.md").write_text(
        "This directory contains 1 locally cached PDF plus download manifests.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    codes = {issue.code for issue in report.issues}
    assert "documented_count_conflict" not in codes
    assert "documented_count_mismatch" not in codes


def test_validate_paper_manifest_allows_absent_documented_counts(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    (tmp_path / "README.md").write_text("LibreEvolve paper cache.\n", encoding="utf-8")
    (tmp_path / "papers" / "README.md").write_text("Paper cache index.\n", encoding="utf-8")

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    codes = {issue.code for issue in report.issues}
    assert "documented_count_conflict" not in codes
    assert "documented_count_mismatch" not in codes


def test_validate_paper_manifest_rejects_malformed_readme_badge_count(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    readme = tmp_path / "README.md"
    readme.write_text(
        '<img src="https://img.shields.io/badge/local%20paper%20cache-many-9E6A03" '
        'alt="Local paper cache">\n',
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "malformed_paper_count_badge" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_checks_cached_pdf_prose_count(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    (tmp_path / "README.md").write_text("LibreEvolve paper cache.\n", encoding="utf-8")
    (tmp_path / "papers" / "README.md").write_text(
        "This directory is the paper-cache index. On the working machine it "
        "contains 24 locally cached PDFs plus download manifests.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    assert report.ok is False
    assert "documented_count_mismatch" in {issue.code for issue in report.issues}
    assert "documented paper count is 24 but manifest has 1 rows" in {
        issue.message for issue in report.issues
    }


def test_validate_paper_manifest_reports_unreadable_readme_count_source(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    (tmp_path / "README.md").write_bytes(b"\xff\xfe\x00")

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    issues = [issue for issue in report.issues if issue.code == "readme_count_source_unreadable"]
    assert report.ok is False
    assert len(issues) == 1
    assert issues[0].message.startswith("README.md:")


def test_validate_paper_manifest_reports_unreadable_papers_readme_count_source(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    (tmp_path / "papers" / "README.md").write_bytes(b"\xff\xfe\x00")

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    issues = [issue for issue in report.issues if issue.code == "readme_count_source_unreadable"]
    assert report.ok is False
    assert len(issues) == 1
    assert issues[0].message.startswith("papers/README.md:")


def test_validate_paper_manifest_rejects_unsafe_urls(tmp_path, capsys):
    secret_url = "file:///C:/Users/timot/api_key=sk-proj_paperurl_secret_1234567890.pdf"  # pragma: allowlist secret
    row = _row(tmp_path, url=secret_url)
    _write_manifest(tmp_path, [row])

    exit_code = main(["--root", str(tmp_path), "--json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert exit_code == 1
    assert "invalid_url" in {issue["code"] for issue in data["issues"]}
    assert secret_url not in captured.out
    assert "sk-proj_paperurl_secret_1234567890" not in captured.out


def test_validate_paper_manifest_redacts_and_bounds_download_messages(tmp_path):
    message = "download failed api_key=sk-proj_papermsg_secret_1234567890 " + ("x" * 5000)  # pragma: allowlist secret
    row = _row(tmp_path, message=message)
    _write_manifest(tmp_path, [row])

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "unsafe_message" in codes
    assert "message_too_long" in codes
    assert "[REDACTED]" in report.availability[0].download_message
    assert "sk-proj_papermsg_secret_1234567890" not in report.availability[0].download_message
    assert len(report.availability[0].download_message) <= 512


def test_validate_paper_manifest_rejects_unsupported_json_fields_and_csv_headers(tmp_path, capsys):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    json_path = tmp_path / "papers" / "download_manifest.json"
    json_rows = json.loads(json_path.read_text(encoding="utf-8"))
    json_rows[0]["api_key"] = "sk-proj_extra_json_secret_1234567890"  # pragma: allowlist secret
    json_path.write_text(json.dumps(json_rows), encoding="utf-8")
    csv_path = tmp_path / "papers" / "download_manifest.csv"
    text = csv_path.read_text(encoding="utf-8")
    text = text.replace("id,title,url,file,ok,bytes,sha256,message", "id,title,url,file,ok,bytes,sha256,message,api_key")
    text = text.replace("\ndownloaded", "\ndownloaded,sk-proj_extra_csv_secret_1234567890")
    csv_path.write_text(text, encoding="utf-8")

    exit_code = main(["--root", str(tmp_path), "--json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    codes = {issue["code"] for issue in data["issues"]}
    assert exit_code == 1
    assert "unsupported_json_field" in codes
    assert "unsupported_csv_header" in codes
    assert "csv_header_order" in codes
    assert "sk-proj_extra_json_secret_1234567890" not in captured.out
    assert "sk-proj_extra_csv_secret_1234567890" not in captured.out


def test_validate_paper_manifest_rejects_duplicate_json_keys(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    manifest = tmp_path / "papers" / "download_manifest.json"
    manifest.write_text(
        "[{"
        '"id": "2506.13131",'
        '"title": "AlphaEvolve",'
        '"url": "https://arxiv.org/pdf/first.pdf",'
        '"url": "https://arxiv.org/pdf/2506.13131.pdf",'
        '"file": "papers/2506.13131__AlphaEvolve.pdf",'
        '"ok": true,'
        f'"bytes": {row["bytes"]},'
        f'"sha256": "{row["sha256"]}",'
        '"message": "downloaded"'
        "}]",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    assert report.ok is False
    assert "duplicate_json_key" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_checks_appendix_a_matrix_registry_when_present(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [
                    {
                        "id": "mm_4x4x4",
                        "dimensions": [4, 4, 4],
                        "best_known_rank": 49,
                        "alphaevolve_rank": 49,
                        "outcome": "surpassed",
                        "exact_algorithm": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "appendix_a_invalid_target_count" in codes
    assert "appendix_a_invalid_surpassed_rank" in codes
    assert "appendix_a_missing_exact_algorithm" in codes
    assert "appendix_a_curation_missing_included_target" in codes


def test_validate_paper_manifest_accepts_committed_matrix_curation_sidecars(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_CURATION_FILE).write_text(
        json.dumps(appendix_a_matrix_curation_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_EXCLUDED_TARGET_CURATION_FILE).write_text(
        json.dumps(appendix_a_matrix_excluded_target_curation_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_matrix_curation_sidecar_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    curation = appendix_a_matrix_curation_record()
    curation["selection_policy"]["rough_m_max"] = 6
    (tmp_path / paper_manifest.APPENDIX_A_CURATION_FILE).write_text(
        json.dumps(curation, indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_EXCLUDED_TARGET_CURATION_FILE).write_text(
        json.dumps(appendix_a_matrix_excluded_target_curation_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "appendix_a_curation_invalid_selection_rough_m_max" in codes


def test_validate_paper_manifest_rejects_matrix_excluded_target_curation_sidecar_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    excluded_boundary = appendix_a_matrix_excluded_target_curation_boundary_record()
    excluded_boundary["curation_status"] = "recorded"
    excluded_boundary["coverage_policy"] = {
        "status": "partial_with_scope",
        "scope": "fixture scope",
    }
    (tmp_path / paper_manifest.APPENDIX_A_CURATION_FILE).write_text(
        json.dumps(appendix_a_matrix_curation_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_EXCLUDED_TARGET_CURATION_FILE).write_text(
        json.dumps(excluded_boundary, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "appendix_a_excluded_target_curation_missing_excluded_targets" in codes


def test_validate_paper_manifest_requires_matrix_curation_sidecars_at_repo_root(
    tmp_path,
    monkeypatch,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "appendix_a_curation_manifest_missing" in codes
    assert "appendix_a_excluded_target_curation_manifest_missing" in codes


def test_validate_paper_manifest_checks_matrix_excluded_target_curation_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.appendix_a_matrix_excluded_target_curation_boundary_record()
    boundary["curation_status"] = "recorded"
    boundary["coverage_policy"] = {
        "status": "partial_with_scope",
        "scope": "fixture scope",
    }
    monkeypatch.setattr(
        paper_manifest,
        "appendix_a_matrix_excluded_target_curation_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "appendix_a_excluded_target_curation_missing_excluded_targets" in codes


def test_validate_paper_manifest_accepts_committed_matrix_resource_frontier_sidecars(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_RESOURCE_FRONTIER_FILE).write_text(
        json.dumps(appendix_a_matrix_resource_frontier_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_LOCAL_RESOURCE_FRONTIER_FILE).write_text(
        json.dumps(appendix_a_matrix_local_resource_frontier_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_matrix_resource_frontier_sidecar_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    resource = appendix_a_matrix_resource_frontier_record()
    resource["frontier_observations"][0]["seed_count"] = 100
    (tmp_path / paper_manifest.APPENDIX_A_RESOURCE_FRONTIER_FILE).write_text(
        json.dumps(resource, indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_LOCAL_RESOURCE_FRONTIER_FILE).write_text(
        json.dumps(appendix_a_matrix_local_resource_frontier_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "appendix_a_resource_frontier_invalid_seed_count" in codes


def test_validate_paper_manifest_rejects_matrix_local_resource_frontier_sidecar_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    local_resource = appendix_a_matrix_local_resource_frontier_record()
    local_resource["local_frontier_status"] = "attempts_recorded"
    local_resource["excluded_target_policy"] = {
        "status": "defined",
        "boundary": "fixture policy",
    }
    (tmp_path / paper_manifest.APPENDIX_A_RESOURCE_FRONTIER_FILE).write_text(
        json.dumps(appendix_a_matrix_resource_frontier_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_LOCAL_RESOURCE_FRONTIER_FILE).write_text(
        json.dumps(local_resource, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "appendix_a_local_resource_frontier_missing_local_attempts" in codes


def test_validate_paper_manifest_requires_matrix_resource_frontier_sidecars_at_repo_root(
    tmp_path,
    monkeypatch,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "appendix_a_resource_frontier_manifest_missing" in codes
    assert "appendix_a_local_resource_frontier_manifest_missing" in codes


def test_validate_paper_manifest_checks_matrix_cascade_run_runtime_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.matrix_cascade_run_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    monkeypatch.setattr(
        paper_manifest,
        "matrix_cascade_run_runtime_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "matrix_cascade_run_runtime_missing_runtime_cascade_run_records" in codes


def test_validate_paper_manifest_accepts_committed_matrix_cascade_run_runtime_sidecar(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.MATRIX_CASCADE_RUN_RUNTIME_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.matrix_cascade_run_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_matrix_cascade_run_runtime_sidecar_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    record = paper_manifest.matrix_cascade_run_runtime_boundary_record()
    record["runtime_emission_status"] = "emitted"
    sidecar = tmp_path / paper_manifest.MATRIX_CASCADE_RUN_RUNTIME_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_cascade_run_runtime_missing_runtime_cascade_run_records" in codes


def test_validate_paper_manifest_requires_matrix_cascade_run_runtime_sidecar_at_repo_root(
    tmp_path,
    monkeypatch,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_BASELINE_COMPONENT_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_baseline_component_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_cascade_run_runtime_manifest_missing" in codes


def test_validate_paper_manifest_checks_matrix_baseline_component_runtime_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.matrix_baseline_component_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    monkeypatch.setattr(
        paper_manifest,
        "matrix_baseline_component_runtime_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "matrix_baseline_component_runtime_missing_runtime_baseline_component_records" in codes


def test_validate_paper_manifest_accepts_committed_matrix_baseline_component_runtime_sidecar(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.MATRIX_BASELINE_COMPONENT_RUNTIME_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.matrix_baseline_component_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_matrix_baseline_component_runtime_sidecar_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    record = paper_manifest.matrix_baseline_component_runtime_boundary_record()
    record["runtime_emission_status"] = "emitted"
    sidecar = tmp_path / paper_manifest.MATRIX_BASELINE_COMPONENT_RUNTIME_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_baseline_component_runtime_missing_runtime_baseline_component_records" in codes


def test_validate_paper_manifest_requires_matrix_baseline_component_runtime_sidecar_at_repo_root(
    tmp_path,
    monkeypatch,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_baseline_component_runtime_manifest_missing" in codes


def test_validate_paper_manifest_checks_pinned_strassen_bundle(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        paper_manifest,
        "validate_strassen_2x2_publication_bundle",
        lambda: SimpleNamespace(
            issues=[
                SimpleNamespace(
                    code="strassen_regeneration_hash_mismatch",
                    message="pinned Strassen artifact does not match regenerated output",
                )
            ]
        ),
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "matrix_strassen_bundle_strassen_regeneration_hash_mismatch" in codes


def test_validate_paper_manifest_checks_matrix_suite_publication_artifact_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.matrix_suite_publication_artifact_boundary_record()
    boundary["artifact_status"] = "generated"
    monkeypatch.setattr(
        paper_manifest,
        "matrix_suite_publication_artifact_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "matrix_suite_publication_artifact_missing_suite_publication_artifacts" in codes


def test_validate_paper_manifest_accepts_committed_matrix_suite_publication_artifact_sidecar(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.MATRIX_SUITE_PUBLICATION_ARTIFACTS_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.matrix_suite_publication_artifact_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_matrix_suite_publication_artifact_sidecar_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    record = paper_manifest.matrix_suite_publication_artifact_boundary_record()
    record["artifact_status"] = "generated"
    sidecar = tmp_path / paper_manifest.MATRIX_SUITE_PUBLICATION_ARTIFACTS_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_suite_publication_artifact_missing_suite_publication_artifacts" in codes


def test_validate_paper_manifest_requires_matrix_suite_publication_artifact_sidecar_at_repo_root(
    tmp_path,
    monkeypatch,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_CURATION_FILE).write_text(
        json.dumps(appendix_a_matrix_curation_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_EXCLUDED_TARGET_CURATION_FILE).write_text(
        json.dumps(appendix_a_matrix_excluded_target_curation_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_BASELINE_CITATIONS_FILE).write_text(
        json.dumps(appendix_a_matrix_baseline_citation_boundary_from_builtin_citations(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_RESOURCE_FRONTIER_FILE).write_text(
        json.dumps(appendix_a_matrix_resource_frontier_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_LOCAL_RESOURCE_FRONTIER_FILE).write_text(
        json.dumps(appendix_a_matrix_local_resource_frontier_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_SUBSET_SCOPE_ARTIFACTS_FILE).write_text(
        json.dumps(paper_manifest.appendix_a_matrix_subset_scope_artifact_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.APPENDIX_A_ROW_NOTE_ARTIFACTS_FILE).write_text(
        json.dumps(paper_manifest.appendix_a_matrix_row_note_artifact_boundary_record(), indent=2),
        encoding="utf-8",
    )
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_suite_publication_artifact_manifest_missing" in codes


def test_validate_paper_manifest_checks_matrix_near_integrality_runtime_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.matrix_near_integrality_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    monkeypatch.setattr(
        paper_manifest,
        "matrix_near_integrality_runtime_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "matrix_near_integrality_runtime_missing_runtime_near_integrality_records" in codes


def test_validate_paper_manifest_accepts_committed_matrix_near_integrality_runtime_sidecar(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.MATRIX_NEAR_INTEGRALITY_RUNTIME_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.matrix_near_integrality_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_matrix_near_integrality_runtime_sidecar_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    record = paper_manifest.matrix_near_integrality_runtime_boundary_record()
    record["runtime_emission_status"] = "emitted"
    sidecar = tmp_path / paper_manifest.MATRIX_NEAR_INTEGRALITY_RUNTIME_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_near_integrality_runtime_missing_runtime_near_integrality_records" in codes


def test_validate_paper_manifest_requires_matrix_near_integrality_runtime_sidecar_at_repo_root(
    tmp_path,
    monkeypatch,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_BASELINE_COMPONENT_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_baseline_component_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_CASCADE_RUN_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_cascade_run_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_near_integrality_runtime_manifest_missing" in codes


def test_validate_paper_manifest_checks_matrix_baseline_citation_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.appendix_a_matrix_baseline_citation_boundary_record()
    boundary["citation_status"] = "recorded"
    monkeypatch.setattr(
        paper_manifest,
        "appendix_a_matrix_baseline_citation_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "appendix_a_baseline_citation_missing_baseline_citations" in codes


def test_validate_paper_manifest_accepts_committed_matrix_baseline_citation_sidecar(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.APPENDIX_A_BASELINE_CITATIONS_FILE
    sidecar.write_text(
        json.dumps(
            appendix_a_matrix_baseline_citation_boundary_from_builtin_citations(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_matrix_baseline_citation_sidecar_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    record = appendix_a_matrix_baseline_citation_boundary_from_builtin_citations()
    record["baseline_citations"][0]["cited_reference_id"] = "999"
    sidecar = tmp_path / paper_manifest.APPENDIX_A_BASELINE_CITATIONS_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "appendix_a_baseline_citation_invalid_cited_reference_id" in codes


def test_validate_paper_manifest_checks_matrix_scalar_field_runtime_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.matrix_scalar_field_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    monkeypatch.setattr(
        paper_manifest,
        "matrix_scalar_field_runtime_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "matrix_scalar_field_runtime_missing_runtime_scalar_field_records" in codes


def test_validate_paper_manifest_accepts_committed_matrix_scalar_field_runtime_sidecar(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.MATRIX_SCALAR_FIELD_RUNTIME_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.matrix_scalar_field_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_matrix_scalar_field_runtime_sidecar_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    record = paper_manifest.matrix_scalar_field_runtime_boundary_record()
    record["runtime_emission_status"] = "emitted"
    sidecar = tmp_path / paper_manifest.MATRIX_SCALAR_FIELD_RUNTIME_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_scalar_field_runtime_missing_runtime_scalar_field_records" in codes


def test_validate_paper_manifest_requires_matrix_scalar_field_runtime_sidecar_at_repo_root(
    tmp_path,
    monkeypatch,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_BASELINE_COMPONENT_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_baseline_component_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_CASCADE_RUN_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_cascade_run_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_NEAR_INTEGRALITY_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_near_integrality_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_scalar_field_runtime_manifest_missing" in codes


def test_validate_paper_manifest_checks_matrix_sweep_space_runtime_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.matrix_sweep_space_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    monkeypatch.setattr(
        paper_manifest,
        "matrix_sweep_space_runtime_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "matrix_sweep_space_runtime_missing_runtime_sweep_space_records" in codes


def test_validate_paper_manifest_accepts_committed_matrix_sweep_space_runtime_sidecar(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.MATRIX_SWEEP_SPACE_RUNTIME_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.matrix_sweep_space_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_matrix_sweep_space_runtime_sidecar_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    record = paper_manifest.matrix_sweep_space_runtime_boundary_record()
    record["runtime_emission_status"] = "emitted"
    sidecar = tmp_path / paper_manifest.MATRIX_SWEEP_SPACE_RUNTIME_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_sweep_space_runtime_missing_runtime_sweep_space_records" in codes


def test_validate_paper_manifest_requires_matrix_sweep_space_runtime_sidecar_at_repo_root(
    tmp_path,
    monkeypatch,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_BASELINE_COMPONENT_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_baseline_component_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_CASCADE_RUN_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_cascade_run_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_NEAR_INTEGRALITY_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_near_integrality_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_SCALAR_FIELD_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_scalar_field_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_sweep_space_runtime_manifest_missing" in codes


def test_validate_paper_manifest_checks_matrix_tensor_rank_runtime_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.matrix_tensor_rank_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    monkeypatch.setattr(
        paper_manifest,
        "matrix_tensor_rank_runtime_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "matrix_tensor_rank_runtime_missing_runtime_tensor_rank_records" in codes


def test_validate_paper_manifest_accepts_committed_matrix_tensor_rank_runtime_sidecar(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.MATRIX_TENSOR_RANK_RUNTIME_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.matrix_tensor_rank_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_matrix_tensor_rank_runtime_sidecar_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    record = paper_manifest.matrix_tensor_rank_runtime_boundary_record()
    record["runtime_emission_status"] = "emitted"
    sidecar = tmp_path / paper_manifest.MATRIX_TENSOR_RANK_RUNTIME_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_tensor_rank_runtime_missing_runtime_tensor_rank_records" in codes


def test_validate_paper_manifest_requires_matrix_tensor_rank_runtime_sidecar_at_repo_root(
    tmp_path,
    monkeypatch,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_BASELINE_COMPONENT_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_baseline_component_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_CASCADE_RUN_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_cascade_run_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_NEAR_INTEGRALITY_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_near_integrality_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_SCALAR_FIELD_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_scalar_field_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_SWEEP_SPACE_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_sweep_space_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_tensor_rank_runtime_manifest_missing" in codes


def test_validate_paper_manifest_checks_matrix_headline_historicity_runtime_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.matrix_headline_historicity_runtime_boundary_record()
    boundary["runtime_emission_status"] = "emitted"
    monkeypatch.setattr(
        paper_manifest,
        "matrix_headline_historicity_runtime_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "matrix_headline_historicity_runtime_missing_runtime_headline_historicity_records" in codes


def test_validate_paper_manifest_accepts_committed_matrix_headline_historicity_sidecar(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.MATRIX_HEADLINE_HISTORICITY_ARTIFACTS_FILE
    sidecar.write_text(
        json.dumps(
            matrix_headline_historicity_runtime_boundary_from_builtin_evidence(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_matrix_headline_historicity_sidecar_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    record = matrix_headline_historicity_runtime_boundary_from_builtin_evidence()
    record["emitted_records"][0]["rank"] = 49
    sidecar = tmp_path / paper_manifest.MATRIX_HEADLINE_HISTORICITY_ARTIFACTS_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert (
        "matrix_headline_historicity_runtime_runtime_record_0_headline_historicity_rank_mismatch"
        in codes
    )


def test_validate_paper_manifest_checks_matrix_rank_table_artifact_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.matrix_rank_table_artifact_boundary_record()
    boundary["artifact_status"] = "emitted"
    monkeypatch.setattr(
        paper_manifest,
        "matrix_rank_table_artifact_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "matrix_rank_table_artifact_missing_matrix_rank_table_artifacts" in codes


def test_validate_paper_manifest_accepts_committed_matrix_rank_table_artifact_sidecar(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.MATRIX_RANK_TABLE_ARTIFACTS_FILE
    sidecar.write_text(
        json.dumps(
            matrix_rank_table_artifact_boundary_from_builtin_exhibit(),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_matrix_rank_table_artifact_sidecar_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    record = matrix_rank_table_artifact_boundary_from_builtin_exhibit()
    record["emitted_artifacts"][0]["row_count"] = 999
    sidecar = tmp_path / paper_manifest.MATRIX_RANK_TABLE_ARTIFACTS_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "matrix_rank_table_artifact_invalid_artifact_nested_row_count" in codes


def test_validate_paper_manifest_checks_figure9_matrix_diff_artifact_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.figure9_matrix_diff_artifact_boundary_record()
    boundary["artifact_status"] = "emitted"
    boundary["source_figure_ids"] = ["Figure 9a"]
    monkeypatch.setattr(
        paper_manifest,
        "figure9_matrix_diff_artifact_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "figure9_matrix_diff_artifact_invalid_source_figure_ids" in codes
    assert "figure9_matrix_diff_artifact_missing_figure9_matrix_diff_artifacts" in codes


def test_validate_paper_manifest_accepts_committed_figure9_matrix_diff_artifact_sidecar(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.FIGURE9_MATRIX_DIFF_ARTIFACTS_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.figure9_matrix_diff_artifact_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_figure9_matrix_diff_artifact_sidecar_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    record = paper_manifest.figure9_matrix_diff_artifact_boundary_record()
    record["artifact_status"] = "emitted"
    record["source_figure_ids"] = ["Figure 9a"]
    sidecar = tmp_path / paper_manifest.FIGURE9_MATRIX_DIFF_ARTIFACTS_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "figure9_matrix_diff_artifact_invalid_source_figure_ids" in codes
    assert "figure9_matrix_diff_artifact_missing_figure9_matrix_diff_artifacts" in codes


def test_validate_paper_manifest_requires_figure9_matrix_diff_artifact_sidecar_at_repo_root(
    tmp_path,
    monkeypatch,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_BASELINE_COMPONENT_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_baseline_component_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_CASCADE_RUN_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_cascade_run_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_NEAR_INTEGRALITY_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_near_integrality_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_SCALAR_FIELD_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_scalar_field_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_SWEEP_SPACE_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_sweep_space_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_TENSOR_RANK_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_tensor_rank_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_HEADLINE_HISTORICITY_ARTIFACTS_FILE).write_text(
        json.dumps(matrix_headline_historicity_runtime_boundary_from_builtin_evidence(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_RANK_TABLE_ARTIFACTS_FILE).write_text(
        json.dumps(matrix_rank_table_artifact_boundary_from_builtin_exhibit(), indent=2),
        encoding="utf-8",
    )
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "figure9_matrix_diff_artifact_manifest_missing" in codes


def test_validate_paper_manifest_checks_figure4_matrix_discovery_artifact_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.figure4_matrix_discovery_artifact_boundary_record()
    boundary["artifact_status"] = "emitted"
    boundary["source_figure_ids"] = ["Figure 5"]
    monkeypatch.setattr(
        paper_manifest,
        "figure4_matrix_discovery_artifact_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "figure4_matrix_discovery_artifact_invalid_source_figure_ids" in codes
    assert "figure4_matrix_discovery_artifact_missing_figure4_matrix_discovery_artifacts" in codes


def test_validate_paper_manifest_accepts_committed_figure4_matrix_discovery_artifact_sidecar(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.FIGURE4_MATRIX_DISCOVERY_ARTIFACTS_FILE
    sidecar.write_text(
        json.dumps(paper_manifest.figure4_matrix_discovery_artifact_boundary_record(), indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_figure4_matrix_discovery_artifact_sidecar_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    record = paper_manifest.figure4_matrix_discovery_artifact_boundary_record()
    record["artifact_status"] = "emitted"
    record["source_figure_ids"] = ["Figure 5"]
    sidecar = tmp_path / paper_manifest.FIGURE4_MATRIX_DISCOVERY_ARTIFACTS_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "figure4_matrix_discovery_artifact_invalid_source_figure_ids" in codes
    assert "figure4_matrix_discovery_artifact_missing_figure4_matrix_discovery_artifacts" in codes


def test_validate_paper_manifest_requires_figure4_matrix_discovery_artifact_sidecar_at_repo_root(
    tmp_path,
    monkeypatch,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_BASELINE_COMPONENT_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_baseline_component_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_CASCADE_RUN_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_cascade_run_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_NEAR_INTEGRALITY_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_near_integrality_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_SCALAR_FIELD_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_scalar_field_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_SWEEP_SPACE_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_sweep_space_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_TENSOR_RANK_RUNTIME_FILE).write_text(
        json.dumps(paper_manifest.matrix_tensor_rank_runtime_boundary_record(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_HEADLINE_HISTORICITY_ARTIFACTS_FILE).write_text(
        json.dumps(matrix_headline_historicity_runtime_boundary_from_builtin_evidence(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.MATRIX_RANK_TABLE_ARTIFACTS_FILE).write_text(
        json.dumps(matrix_rank_table_artifact_boundary_from_builtin_exhibit(), indent=2),
        encoding="utf-8",
    )
    (tmp_path / paper_manifest.FIGURE9_MATRIX_DIFF_ARTIFACTS_FILE).write_text(
        json.dumps(paper_manifest.figure9_matrix_diff_artifact_boundary_record(), indent=2),
        encoding="utf-8",
    )
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "figure4_matrix_discovery_artifact_manifest_missing" in codes


def test_validate_paper_manifest_checks_matrix_subset_scope_artifact_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.appendix_a_matrix_subset_scope_artifact_boundary_record()
    boundary["artifact_status"] = "emitted"
    monkeypatch.setattr(
        paper_manifest,
        "appendix_a_matrix_subset_scope_artifact_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "appendix_a_subset_scope_artifact_missing_subset_scope_artifacts" in codes


def test_validate_paper_manifest_accepts_committed_matrix_subset_scope_artifact_sidecar(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.APPENDIX_A_SUBSET_SCOPE_ARTIFACTS_FILE
    sidecar.write_text(
        json.dumps(
            appendix_a_matrix_subset_scope_artifact_boundary_from_records(
                artifact_paths_by_subset_id={
                    "appendix_a_full": [paper_manifest.APPENDIX_A_SUBSET_SCOPE_ARTIFACTS_FILE],
                    "main_text_mnp_le_5": [paper_manifest.APPENDIX_A_SUBSET_SCOPE_ARTIFACTS_FILE],
                    "table_2_selected": [paper_manifest.APPENDIX_A_SUBSET_SCOPE_ARTIFACTS_FILE],
                }
            ),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_matrix_subset_scope_artifact_sidecar_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    record = appendix_a_matrix_subset_scope_artifact_boundary_from_records(
        artifact_paths_by_subset_id={
            "appendix_a_full": [paper_manifest.APPENDIX_A_SUBSET_SCOPE_ARTIFACTS_FILE],
            "main_text_mnp_le_5": [paper_manifest.APPENDIX_A_SUBSET_SCOPE_ARTIFACTS_FILE],
            "table_2_selected": [paper_manifest.APPENDIX_A_SUBSET_SCOPE_ARTIFACTS_FILE],
        }
    )
    record["emitted_artifacts"][0]["row_count"] = 999
    sidecar = tmp_path / paper_manifest.APPENDIX_A_SUBSET_SCOPE_ARTIFACTS_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "appendix_a_subset_scope_artifact_invalid_artifact_row_count" in codes


def test_validate_paper_manifest_checks_matrix_row_note_artifact_boundary(
    monkeypatch,
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            {
                "schema": "libreevolve.alphaevolve_appendix_a_matrix_registry.v1",
                "source_paper_id": "2506.13131",
                "target_suite": "alphaevolve_appendix_a",
                "targets": [],
            }
        ),
        encoding="utf-8",
    )
    boundary = paper_manifest.appendix_a_matrix_row_note_artifact_boundary_record()
    boundary["artifact_status"] = "emitted"
    monkeypatch.setattr(
        paper_manifest,
        "appendix_a_matrix_row_note_artifact_boundary_record",
        lambda: boundary,
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "appendix_a_row_note_artifact_missing_row_note_artifacts" in codes


def test_validate_paper_manifest_accepts_committed_matrix_row_note_artifact_sidecar(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    sidecar = tmp_path / paper_manifest.APPENDIX_A_ROW_NOTE_ARTIFACTS_FILE
    sidecar.write_text(
        json.dumps(
            appendix_a_matrix_row_note_artifact_boundary_from_records(
                artifact_paths_by_note_id={
                    "concurrent_work_rank90_mm_4x5x6": [
                        paper_manifest.APPENDIX_A_ROW_NOTE_ARTIFACTS_FILE,
                    ]
                }
            ),
            indent=2,
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_matrix_row_note_artifact_sidecar_drift(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    registry = tmp_path / "libreevolve" / "problems" / "benchmarks" / "alphaevolve_appendix_a_matrix.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        Path(paper_manifest.APPENDIX_A_MATRIX_REGISTRY_PATH).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    record = appendix_a_matrix_row_note_artifact_boundary_from_records(
        artifact_paths_by_note_id={
            "concurrent_work_rank90_mm_4x5x6": [
                paper_manifest.APPENDIX_A_ROW_NOTE_ARTIFACTS_FILE,
            ]
        }
    )
    record["emitted_artifacts"][0]["target_id"] = "mm_4x4x4"
    sidecar = tmp_path / paper_manifest.APPENDIX_A_ROW_NOTE_ARTIFACTS_FILE
    sidecar.write_text(json.dumps(record, indent=2), encoding="utf-8")

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "appendix_a_row_note_artifact_invalid_artifact_target_id" in codes


def test_validate_paper_manifest_checks_example_scope_records(monkeypatch, tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    records = paper_manifest.example_benchmark_scope_records()
    records[0]["alphaevolve_comparable"] = True
    monkeypatch.setattr(paper_manifest, "example_benchmark_scope_records", lambda: records)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "example_scope_smoke_marked_comparable" in codes


def test_validate_paper_manifest_accepts_example_scope_sidecar(monkeypatch, tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    scope_path = tmp_path / paper_manifest.EXAMPLE_BENCHMARK_SCOPE_FILE
    scope_path.write_text(
        json.dumps(paper_manifest.example_benchmark_scope_records(), indent=2),
        encoding="utf-8",
    )
    invalid_records = paper_manifest.example_benchmark_scope_records()
    invalid_records[0]["alphaevolve_comparable"] = True
    monkeypatch.setattr(paper_manifest, "example_benchmark_scope_records", lambda: invalid_records)

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True
    assert report.issues == []


def test_validate_paper_manifest_rejects_drifted_example_scope_sidecar(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    records = paper_manifest.example_benchmark_scope_records()
    records[0]["alphaevolve_comparable"] = True
    (tmp_path / paper_manifest.EXAMPLE_BENCHMARK_SCOPE_FILE).write_text(
        json.dumps(records, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "example_scope_smoke_marked_comparable" in codes


def test_validate_paper_manifest_requires_example_scope_sidecar_at_repo_root(monkeypatch, tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    monkeypatch.setattr(paper_manifest, "_repo_root", lambda: tmp_path)

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "example_scope_manifest_missing" in codes


def test_validate_paper_manifest_reports_invalid_encoding_json_manifest(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    json_path = tmp_path / "papers" / "download_manifest.json"
    json_path.write_bytes(b"\xff\xfe\x00")

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert report.row_count == 0
    assert "json_manifest_unreadable" in codes


def test_paper_manifest_cli_redacts_missing_manifest_paths(tmp_path, capsys):
    root = tmp_path / "api_key=sk-proj_papermanifestroot_secret_1234567890"  # pragma: allowlist secret
    root.mkdir()

    exit_code = main(["--root", str(root)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "json_manifest_unreadable" in captured.out
    assert "csv_manifest_unreadable" in captured.out
    assert "papers/download_manifest.json" in captured.out
    assert "papers/download_manifest.csv" in captured.out
    assert str(root) not in captured.out
    assert "sk-proj_papermanifestroot_secret_1234567890" not in captured.out


def test_paper_manifest_json_redacts_malformed_manifest_paths(tmp_path, capsys):
    root = tmp_path / "api_key=sk-proj_papermanifestroot_secret_1234567890"  # pragma: allowlist secret
    root.mkdir()
    row = _row(root)
    _write_manifest(root, [row])
    (root / "papers" / "download_manifest.json").write_text("{", encoding="utf-8")

    exit_code = main(["--root", str(root), "--json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    messages = [issue["message"] for issue in data["issues"]]
    assert exit_code == 1
    assert any(message.startswith("papers/download_manifest.json:") for message in messages)
    assert str(root) not in captured.out
    assert "sk-proj_papermanifestroot_secret_1234567890" not in captured.out


def test_validate_paper_manifest_rejects_duplicate_csv_headers(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    csv_path = tmp_path / "papers" / "download_manifest.csv"
    text = csv_path.read_text(encoding="utf-8")
    text = text.replace("id,title,url,file,ok,bytes,sha256,message", "id,title,url,url,file,ok,bytes,sha256,message")
    text = text.replace("AlphaEvolve,https://", "AlphaEvolve,https://arxiv.org/pdf/2506.13131.pdf,https://")
    csv_path.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "duplicate_csv_header" in {issue.code for issue in report.issues}


def test_paper_manifest_cli_reports_malformed_csv_quotes_in_text(tmp_path, capsys):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    csv_path = tmp_path / "papers" / "download_manifest.csv"
    csv_path.write_text(
        "id,title,url,file,ok,bytes,sha256,message\n"
        '"2506.13131","unterminated title\n',
        encoding="utf-8",
    )

    exit_code = main(["--root", str(tmp_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "csv_manifest_unreadable" in captured.out
    assert "papers/download_manifest.csv" in captured.out


def test_paper_manifest_cli_reports_malformed_csv_quotes_in_json(tmp_path, capsys):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    csv_path = tmp_path / "papers" / "download_manifest.csv"
    csv_path.write_text(
        "id,title,url,file,ok,bytes,sha256,message\n"
        '"2506.13131","unterminated title\n',
        encoding="utf-8",
    )

    exit_code = main(["--root", str(tmp_path), "--json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert exit_code == 1
    assert "csv_manifest_unreadable" in {issue["code"] for issue in data["issues"]}
    assert any(
        issue["message"].startswith("papers/download_manifest.csv:")
        for issue in data["issues"]
    )


def test_validate_paper_manifest_reports_invalid_encoding_csv_manifest(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    csv_path = tmp_path / "papers" / "download_manifest.csv"
    csv_path.write_bytes(b"\xff\xfe\x00")

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert report.row_count == 1
    assert "csv_manifest_unreadable" in codes


def test_paper_manifest_cli_reports_wrong_json_top_level_schema(tmp_path, capsys):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    (tmp_path / "papers" / "download_manifest.json").write_text("{}", encoding="utf-8")

    exit_code = main(["--root", str(tmp_path), "--json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert exit_code == 1
    assert "json_manifest_schema" in {issue["code"] for issue in data["issues"]}


def test_paper_manifest_cli_reports_json_row_schema_and_missing_fields(tmp_path, capsys):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    (tmp_path / "papers" / "download_manifest.json").write_text(
        json.dumps([{"id": "2506.13131"}, "not a row"]),
        encoding="utf-8",
    )

    exit_code = main(["--root", str(tmp_path), "--json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    codes = {issue["code"] for issue in data["issues"]}
    assert exit_code == 1
    assert "missing_fields" in codes
    assert "json_row_schema" in codes


def test_paper_manifest_json_redacts_readme_source_exception_paths(tmp_path, monkeypatch, capsys):
    root = tmp_path / "api_key=sk-proj_papermanifestroot_secret_1234567890"  # pragma: allowlist secret
    root.mkdir()
    row = _row(root)
    _write_manifest(root, [row])
    target = root / "papers" / "README.md"
    real_read_text = Path.read_text

    def fake_read_text(path, *args, **kwargs):
        if path == target:
            raise OSError(f"failed opening {path}")
        return real_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fake_read_text)

    exit_code = main(["--root", str(root), "--json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    messages = [issue["message"] for issue in data["issues"]]
    assert exit_code == 1
    assert any(message == "papers/README.md: failed opening papers/README.md" for message in messages)
    assert str(root) not in captured.out
    assert "sk-proj_papermanifestroot_secret_1234567890" not in captured.out


def test_validate_paper_manifest_checks_empty_csv_headers(tmp_path):
    papers = tmp_path / "papers"
    papers.mkdir()
    (tmp_path / "README.md").write_text("LibreEvolve is informed by a local cache of 0 papers.\n", encoding="utf-8")
    (papers / "README.md").write_text("This directory contains 0 papers.\n", encoding="utf-8")
    (papers / "download_manifest.json").write_text("[]", encoding="utf-8")
    (papers / "download_manifest.csv").write_text("not,the,required,columns\n", encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "missing_csv_header" in codes
    assert "unsupported_csv_header" in codes
    assert "csv_header_order" in codes


def test_validate_paper_manifest_rejects_secret_like_multiline_titles(tmp_path, capsys):
    title = "api_key=sk-proj_papertitle_secret_1234567890\nSecond line"
    row = _row(tmp_path, title=title)
    _write_manifest(tmp_path, [row])

    exit_code = main(["--root", str(tmp_path), "--json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert exit_code == 1
    assert "invalid_title" in {issue["code"] for issue in data["issues"]}
    assert "sk-proj_papertitle_secret_1234567890" not in captured.out


def test_validate_paper_manifest_accepts_matching_status_table(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_accepts_curated_root_readme_paper_summary(tmp_path):
    row_a = _row(tmp_path, row_id="2506.00001", file="papers/2506.00001__A.pdf", url="https://arxiv.org/pdf/2506.00001.pdf")
    row_b = _row(
        tmp_path,
        row_id="2506.00002",
        file="papers/2506.00002__B.pdf",
        url="https://arxiv.org/pdf/2506.00002.pdf",
        content=_valid_pdf_bytes(b"\nsecond"),
    )
    _write_manifest(tmp_path, [row_a, row_b])
    _write_status_table(tmp_path, [row_a["id"], row_b["id"]])
    (tmp_path / "README.md").write_text(
        "LibreEvolve is informed by a local cache of 2 papers.\n"
        "<details>\n"
        "<summary><h2>Local Paper Cache (2)</h2></summary>\n"
        "The tables below are a curated subset for README context. "
        "`papers/README.md` is the complete implementation-status index for all 2 manifest rows.\n"
        f"| [Alpha](https://arxiv.org/abs/{row_a['id']}) | Core |\n"
        "</details>\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_flags_unlabeled_incomplete_root_readme_paper_summary(tmp_path):
    row_a = _row(tmp_path, row_id="2506.00001", file="papers/2506.00001__A.pdf", url="https://arxiv.org/pdf/2506.00001.pdf")
    row_b = _row(
        tmp_path,
        row_id="2506.00002",
        file="papers/2506.00002__B.pdf",
        url="https://arxiv.org/pdf/2506.00002.pdf",
        content=_valid_pdf_bytes(b"\nsecond"),
    )
    _write_manifest(tmp_path, [row_a, row_b])
    _write_status_table(tmp_path, [row_a["id"], row_b["id"]])
    (tmp_path / "README.md").write_text(
        "LibreEvolve is informed by a local cache of 2 papers.\n"
        "<details>\n"
        "<summary><h2>Local Paper Cache (2)</h2></summary>\n"
        f"| [Alpha](https://arxiv.org/abs/{row_a['id']}) | Core |\n"
        "</details>\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    issues = [issue for issue in report.issues if issue.code == "readme_paper_summary_incomplete"]
    assert len(issues) == 1
    assert "lists 1 of 2 manifest ids" in issues[0].message


def test_validate_paper_manifest_reports_missing_and_extra_status_table_rows(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, ["stale-paper-id"])

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "missing_status_table_row" in codes
    assert "extra_status_table_row" in codes


def test_validate_paper_manifest_reports_duplicate_status_table_rows(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"], row["id"]])

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "duplicate_status_table_row" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_reports_non_contiguous_status_table_rows(tmp_path):
    row = _row(tmp_path)
    row_two = _row(
        tmp_path,
        row_id="1504.04909",
        title="MAP-Elites",
        file="papers/1504.04909__MAP_Elites.pdf",
    )
    _write_manifest(tmp_path, [row, row_two])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    status_readme.write_text(
        status_readme.read_text(encoding="utf-8")
        + "\nA prose status note closes the table.\n"
        + f"| {row_two['id']} | Paper 2 | Primary specification target | {PARTIAL_FIXTURE_STATUS} |\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "status_table_non_contiguous" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_reports_status_table_header_mismatch(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    status_readme.write_text(
        status_readme.read_text(encoding="utf-8").replace(
            "| ID | Title | Role | Current LibreEvolve status |",
            "| ID | Title | Role | Status |",
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "status_table_header_mismatch" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_reports_status_table_row_shape(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    status_readme.write_text(
        status_readme.read_text(encoding="utf-8").replace(
            "| 2506.13131 | Paper 1 | Primary specification target | "
            f"{PARTIAL_FIXTURE_STATUS} |",
            "| 2506.13131 | Paper 1 | Primary specification target |",
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "status_table_row_shape" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_reports_invalid_status_table_role_and_status(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Unreviewed marketing claim")
    text = text.replace(PARTIAL_FIXTURE_STATUS, "Production parity proven.")
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "invalid_status_table_role" in codes
    assert "invalid_status_table_status" in codes


def test_validate_paper_manifest_reports_status_table_role_status_mismatch(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Framework inspiration")
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "status_table_role_status_mismatch" in codes
    assert "invalid_status_table_role" not in codes
    assert "invalid_status_table_status" not in codes


def test_validate_paper_manifest_reports_alphaevolve_comparable_status_overclaim(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace(
        PARTIAL_FIXTURE_STATUS,
        "Partially implemented: AlphaEvolve-comparable benchmark evidence is implemented.",
    )
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "status_table_alphaevolve_comparable_overclaim" in codes


def test_validate_paper_manifest_allows_scoped_alphaevolve_comparable_status_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace(
        PARTIAL_FIXTURE_STATUS,
        "Partially implemented: `libreevolve/core/loop.py` is not AlphaEvolve-comparable until benchmark evidence exists.",
    )
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_reports_supported_status_without_local_artifact(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace(PARTIAL_FIXTURE_STATUS, "Partially implemented: fixture status; no full paper behavior.")
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "status_table_supported_status_missing_local_artifact" in codes


def test_validate_paper_manifest_reports_partial_status_without_missing_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace(PARTIAL_FIXTURE_STATUS, "Partially implemented: fixture status.")
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "status_table_partial_status_missing_boundary" in codes


def test_validate_paper_manifest_reports_implemented_status_without_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Foundational archive algorithm")
    text = text.replace(PARTIAL_FIXTURE_STATUS, "Implemented as a local archive.")
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "status_table_implemented_status_missing_boundary" in codes


def test_validate_paper_manifest_allows_implemented_status_with_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Foundational archive algorithm")
    text = text.replace(
        PARTIAL_FIXTURE_STATUS,
        "Implemented as `libreevolve/population/map_elites.py` local archive; richer semantics remain open.",
    )
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_reports_negative_status_implementation_contradiction(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Domain evolution inspiration")
    text = text.replace(
        PARTIAL_FIXTURE_STATUS,
        "Background only; implemented local adapter exists.",
    )
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "status_table_negative_status_contradiction" in codes


def test_validate_paper_manifest_allows_unimplemented_future_benchmark_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Constructive math benchmark candidate")
    text = text.replace(
        PARTIAL_FIXTURE_STATUS,
        "Not implemented; potential future benchmark; no verifier harness.",
    )
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_reports_unimplemented_future_benchmark_without_missing_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Constructive math benchmark candidate")
    text = text.replace(
        PARTIAL_FIXTURE_STATUS,
        "Not implemented; potential future benchmark.",
    )
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "status_table_future_benchmark_missing_boundary" in codes


def test_validate_paper_manifest_reports_background_only_status_without_missing_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Domain evolution inspiration")
    text = text.replace(
        PARTIAL_FIXTURE_STATUS,
        "Background only.",
    )
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "status_table_background_only_missing_boundary" in codes


def test_validate_paper_manifest_allows_background_only_status_with_missing_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Domain evolution inspiration")
    text = text.replace(
        PARTIAL_FIXTURE_STATUS,
        "Background only; no domain-evolution benchmark.",
    )
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_reports_limited_status_without_missing_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Test-time training inspiration")
    text = text.replace(
        PARTIAL_FIXTURE_STATUS,
        "Only clipped-reward export exists.",
    )
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "status_table_limited_status_missing_boundary" in codes


def test_validate_paper_manifest_allows_limited_status_with_missing_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Test-time training inspiration")
    text = text.replace(
        PARTIAL_FIXTURE_STATUS,
        "Only `libreevolve/plugins/ttt_rl.py` clipped-reward export exists; no online training loop.",
    )
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_reports_static_guidance_without_execution_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Modular search inspiration")
    text = text.replace(
        PARTIAL_FIXTURE_STATUS,
        "Static prompt guidance exists for generate/improve/perturb operations.",
    )
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "status_table_static_guidance_missing_execution_boundary" in codes


def test_validate_paper_manifest_allows_static_guidance_execution_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Modular search inspiration")
    text = text.replace(
        PARTIAL_FIXTURE_STATUS,
        "Static prompt guidance exists in `libreevolve/plugins/modular.py` for generate/improve/perturb operations with false execution/enforcement flags.",
    )
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_reports_not_implemented_status_without_missing_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Framework inspiration")
    text = text.replace(
        PARTIAL_FIXTURE_STATUS,
        "Not implemented as described: generic local mutation modes are present.",
    )
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "status_table_not_implemented_missing_boundary" in codes


def test_validate_paper_manifest_allows_not_implemented_status_with_missing_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    status_readme = tmp_path / "papers" / "README.md"
    text = status_readme.read_text(encoding="utf-8")
    text = text.replace("Primary specification target", "Framework inspiration")
    text = text.replace(
        PARTIAL_FIXTURE_STATUS,
        "Not implemented as described: generic local mutation modes are present, but no framework lifecycle database.",
    )
    status_readme.write_text(text, encoding="utf-8")

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_accepts_matching_todo_coverage_table(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_active_todo_ledgers(tmp_path, row["id"])
    completed_cell = _write_completed_todo_ledger(tmp_path)
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS),
                completed_cell,
            )
        ],
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_accepts_matching_status_claim_inventory(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_status_fixture_artifact(tmp_path)
    _write_active_todo_ledgers(tmp_path, row["id"])
    active_cell = _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS)
    completed_cell = _write_completed_todo_ledger(tmp_path)
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                active_cell,
                completed_cell,
            )
        ],
    )
    inventory = paper_manifest.paper_status_claim_inventory_record(tmp_path)
    assert inventory["claim_count"] >= 1
    assert inventory["rows"][0]["source_span"]["path"] == "papers/README.md"
    assert inventory["rows"][0]["source_span"]["line_start"] > 0
    assert inventory["rows"][0]["all_local_artifacts_exist"] is True
    assert inventory["rows"][0]["local_artifact_existing_count"] == 1
    status_artifact_start = PARTIAL_FIXTURE_STATUS.find("`libreevolve/core/loop.py`")
    status_artifact_end = status_artifact_start + len("`libreevolve/core/loop.py`")
    expected_status_artifact_mention = {
        "path": "libreevolve/core/loop.py",
        "status_text_char_start": status_artifact_start,
        "status_text_char_end": status_artifact_end,
        "source_span": {
            "path": "papers/README.md",
            "section": "Implementation status",
            "line_start": inventory["rows"][0]["source_span"]["line_start"],
            "line_end": inventory["rows"][0]["source_span"]["line_start"],
            "status_text_char_start": status_artifact_start,
            "status_text_char_end": status_artifact_end,
        },
    }
    assert inventory["rows"][0]["local_artifact_mention_records"] == [
        expected_status_artifact_mention
    ]
    assert inventory["rows"][0]["local_artifact_records"] == [
        {"path": "libreevolve/core/loop.py", "exists": True, "kind": "file"}
    ]
    assert inventory["unique_local_artifact_count"] == 1
    assert inventory["local_artifact_mention_record_count"] == 1
    assert inventory["missing_local_artifact_paths"] == []
    assert inventory["artifact_existence_status"] == "all_referenced_local_artifacts_present"
    expected_todo_count = len(
        set(inventory["rows"][0]["active_todo_paths"] + inventory["rows"][0]["completed_todo_paths"])
    )
    assert inventory["rows"][0]["todo_evidence_path_count"] == expected_todo_count
    expected_active_path_mentions = [
        {
            "path": path,
            "evidence_kind": "active",
            "todo_cell_char_start": active_cell.find(f"`{path}`"),
            "todo_cell_char_end": active_cell.find(f"`{path}`") + len(f"`{path}`"),
        }
        for path in inventory["rows"][0]["active_todo_paths"]
    ]
    expected_completed_path_mentions = [
        {
            "path": path,
            "evidence_kind": "completed",
            "todo_cell_char_start": completed_cell.find(f"`{path}`"),
            "todo_cell_char_end": completed_cell.find(f"`{path}`") + len(f"`{path}`"),
        }
        for path in inventory["rows"][0]["completed_todo_paths"]
    ]
    assert inventory["rows"][0]["active_todo_path_mention_records"] == expected_active_path_mentions
    assert inventory["rows"][0]["completed_todo_path_mention_records"] == expected_completed_path_mentions
    assert inventory["rows"][0]["todo_evidence_path_mention_count"] == expected_todo_count
    assert inventory["todo_evidence_path_mention_count"] == expected_todo_count
    assert inventory["rows"][0]["all_todo_evidence_paths_exist"] is True
    assert inventory["rows"][0]["todo_evidence_missing_paths"] == []
    assert inventory["unique_todo_evidence_path_count"] == expected_todo_count
    assert inventory["missing_todo_evidence_paths"] == []
    assert inventory["todo_evidence_status"] == "all_referenced_todo_paths_present"
    assert inventory["rows"][0]["local_artifacts_mentioned_in_todo_evidence"] == [
        "libreevolve/core/loop.py"
    ]
    active_content_records = inventory["rows"][0]["active_todo_content_records"]
    completed_content_records = inventory["rows"][0]["completed_todo_content_records"]
    assert active_content_records[0]["row_source_tokens_matched"] == [row["id"]]
    assert completed_content_records[0]["row_source_tokens_matched"] == [row["id"]]
    assert row["id"] in inventory["todo_content_matched_source_tokens"]
    assert (
        inventory["todo_content_matched_source_token_count"]
        == len(inventory["todo_content_matched_source_tokens"])
    )
    active_evidence_text = (
        f"- [ ] Track source-specific gap for `{row['id']}`.\n"
        "  - Current gap: temporary test ledger entry for `libreevolve/core/loop.py`.\n"
        "  - Required result: keep the temporary fixture source-specific.\n"
    )
    expected_active_block_record = {
        "block_kind": "active",
        "block_ordinal": 1,
        "file_text_char_start": 0,
        "file_text_char_end": len(active_evidence_text),
        "line_start": 1,
        "line_end": active_evidence_text.count("\n") + 1,
        "block_sha256": hashlib.sha256(active_evidence_text.encode("utf-8")).hexdigest(),
        "matched_source_tokens": [row["id"]],
        "mentioned_local_artifact_records": [
            {
                "path": "libreevolve/core/loop.py",
                "evidence_text_char_start": active_evidence_text.find("libreevolve/core/loop.py"),
                "evidence_text_char_end": active_evidence_text.find("libreevolve/core/loop.py")
                + len("libreevolve/core/loop.py"),
            }
        ],
        "mentioned_local_artifact_paths": ["libreevolve/core/loop.py"],
    }
    assert [
        record["row_specific_block_records"] for record in active_content_records
    ] == [[expected_active_block_record] for _record in active_content_records]
    active_artifact_start = active_evidence_text.find("libreevolve/core/loop.py")
    active_artifact_end = active_artifact_start + len("libreevolve/core/loop.py")
    expected_active_artifact_record = {
        "path": "libreevolve/core/loop.py",
        "evidence_text_char_start": active_artifact_start,
        "evidence_text_char_end": active_artifact_end,
    }
    assert [
        record["mentioned_local_artifact_records"] for record in active_content_records
    ] == [[expected_active_artifact_record] for _record in active_content_records]
    completed_evidence_text = (
        f"- [x] Completed fixture evidence for `{row['id']}` in "
        "`libreevolve/core/loop.py`.\n"
    )
    assert completed_content_records[0]["row_specific_block_records"] == [
        {
            "block_kind": "completed",
            "block_ordinal": 1,
            "file_text_char_start": 0,
            "file_text_char_end": len(completed_evidence_text),
            "line_start": 1,
            "line_end": completed_evidence_text.count("\n") + 1,
            "block_sha256": hashlib.sha256(completed_evidence_text.encode("utf-8")).hexdigest(),
            "matched_source_tokens": [row["id"]],
            "mentioned_local_artifact_records": [
                {
                    "path": "libreevolve/core/loop.py",
                    "evidence_text_char_start": completed_evidence_text.find(
                        "libreevolve/core/loop.py"
                    ),
                    "evidence_text_char_end": completed_evidence_text.find(
                        "libreevolve/core/loop.py"
                    )
                    + len("libreevolve/core/loop.py"),
                }
            ],
            "mentioned_local_artifact_paths": ["libreevolve/core/loop.py"],
        }
    ]
    completed_artifact_start = completed_evidence_text.find("libreevolve/core/loop.py")
    completed_artifact_end = completed_artifact_start + len("libreevolve/core/loop.py")
    assert completed_content_records[0]["mentioned_local_artifact_records"] == [
        {
            "path": "libreevolve/core/loop.py",
            "evidence_text_char_start": completed_artifact_start,
            "evidence_text_char_end": completed_artifact_end,
        }
    ]
    assert inventory["todo_content_artifact_mention_record_count"] == len(active_content_records) + 1
    assert inventory["todo_content_row_specific_block_record_count"] == (
        sum(len(record["row_specific_block_records"]) for record in active_content_records)
        + sum(len(record["row_specific_block_records"]) for record in completed_content_records)
    )
    assert inventory["rows"][0]["local_artifacts_missing_from_todo_evidence"] == []
    assert inventory["rows"][0]["all_local_artifacts_linked_from_todo_evidence"] is True
    assert (
        inventory["rows"][0]["todo_content_evidence_status"]
        == "all_row_local_artifacts_mentioned_in_todo_evidence"
    )
    assert inventory["local_artifacts_missing_from_todo_evidence"] == []
    assert (
        inventory["todo_content_evidence_status"]
        == "all_row_local_artifacts_mentioned_in_todo_evidence"
    )
    assert inventory["phrase_local_artifacts_missing_from_todo_evidence"] == []
    assert (
        inventory["phrase_todo_content_evidence_status"]
        == "all_phrase_local_artifacts_mentioned_in_todo_evidence"
    )
    assert inventory["absence_phrase_count"] == 1
    assert inventory["absence_signal_record_count"] == 1
    assert inventory["absence_signal_terms"] == ["no"]
    assert inventory["absence_signal_inventory_status"] == (
        "absence_signals_structurally_classified_without_freshness_verification"
    )
    assert inventory["rows"][0]["source_span_status"] == "phrase_offsets_recorded_in_status_cell"
    assert inventory["rows"][0]["status_claims"][0]["source_span"]["line_start"] > 0
    assert (
        inventory["rows"][0]["status_claims"][0]["evidence_link_status"]
        == "candidate_links_recorded_without_semantic_verification"
    )
    assert "row_active_todo_paths" in inventory["rows"][0]["status_claims"][0]["evidence_links"]
    assert (
        inventory["rows"][0]["status_claims"][0]["evidence_links"][
            "phrase_local_artifact_mention_records"
        ]
        == [expected_status_artifact_mention]
    )
    assert inventory["phrase_local_artifact_mention_record_count"] == 1
    phrase_block_records = inventory["rows"][0]["status_claims"][0]["evidence_links"][
        "phrase_todo_content_block_records"
    ]
    assert len(phrase_block_records) == len(active_content_records) + len(completed_content_records)
    assert inventory["phrase_todo_content_block_record_count"] == len(phrase_block_records)
    assert {
        record["phrase_local_artifact_paths_mentioned"][0] for record in phrase_block_records
    } == {"libreevolve/core/loop.py"}
    assert all(record["block_sha256"] for record in phrase_block_records)
    assert (
        inventory["rows"][0]["status_claims"][0]["evidence_links"][
            "phrase_todo_content_evidence_status"
        ]
        == "all_phrase_local_artifacts_mentioned_in_todo_evidence"
    )
    assert inventory["rows"][0]["status_claims"][0]["semantic_status"] == "not_verified"
    absence_claims = [
        claim for claim in inventory["rows"][0]["status_claims"] if claim["has_absence_signal"]
    ]
    assert len(absence_claims) == 1
    assert absence_claims[0]["absence_signal_terms"] == ["no"]
    absence_start = PARTIAL_FIXTURE_STATUS.find("no")
    absence_end = absence_start + len("no")
    absence_phrase_start = absence_claims[0]["status_text_char_start"]
    assert absence_claims[0]["absence_signal_records"] == [
        {
            "term": "no",
            "phrase_text_char_start": absence_start - absence_phrase_start,
            "phrase_text_char_end": absence_end - absence_phrase_start,
            "status_text_char_start": absence_start,
            "status_text_char_end": absence_end,
            "source_span": {
                "path": "papers/README.md",
                "section": "Implementation status",
                "line_start": inventory["rows"][0]["source_span"]["line_start"],
                "line_end": inventory["rows"][0]["source_span"]["line_start"],
                "status_text_char_start": absence_start,
                "status_text_char_end": absence_end,
            },
        }
    ]
    assert absence_claims[0]["freshness_status"] == "not_verified"
    (tmp_path / paper_manifest.STATUS_CLAIM_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_rejects_status_claim_inventory_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_status_fixture_artifact(tmp_path)
    _write_active_todo_ledgers(tmp_path, row["id"])
    completed_cell = _write_completed_todo_ledger(tmp_path)
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS),
                completed_cell,
            )
        ],
    )
    inventory = paper_manifest.paper_status_claim_inventory_record(tmp_path)
    inventory["rows"][0]["status_text_sha256"] = "0" * 64
    (tmp_path / paper_manifest.STATUS_CLAIM_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "status_claim_inventory_rows_mismatch" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_accepts_status_claim_inventory_readme_summary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_status_fixture_artifact(tmp_path)
    _write_active_todo_ledgers(tmp_path, row["id"])
    completed_cell = _write_completed_todo_ledger(tmp_path)
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS),
                completed_cell,
            )
        ],
    )
    inventory = paper_manifest.paper_status_claim_inventory_record(tmp_path)
    (tmp_path / paper_manifest.STATUS_CLAIM_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )
    readme_path = tmp_path / "papers" / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8")
        + "\n"
        + "- `papers/status_claim_inventory.json`: row-level inventory. "
        + "The current inventory records "
        + f"{inventory['todo_content_row_specific_block_record_count']} "
        + "row-specific TODO block hashes/source offsets.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_reports_stale_status_claim_inventory_readme_summary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_status_fixture_artifact(tmp_path)
    _write_active_todo_ledgers(tmp_path, row["id"])
    completed_cell = _write_completed_todo_ledger(tmp_path)
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS),
                completed_cell,
            )
        ],
    )
    inventory = paper_manifest.paper_status_claim_inventory_record(tmp_path)
    (tmp_path / paper_manifest.STATUS_CLAIM_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )
    stale_count = inventory["todo_content_row_specific_block_record_count"] + 1
    readme_path = tmp_path / "papers" / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8")
        + "\n"
        + "- `papers/status_claim_inventory.json`: row-level inventory. "
        + "The current inventory records "
        + f"{stale_count} row-specific TODO block hashes/source offsets.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert (
        "status_claim_inventory_readme_summary_"
        "todo_content_row_specific_block_record_count_mismatch"
    ) in codes


def test_validate_paper_manifest_accepts_status_claim_inventory_status_ledger_summary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_status_fixture_artifact(tmp_path)
    _write_active_todo_ledgers(tmp_path, row["id"])
    completed_cell = _write_completed_todo_ledger(tmp_path)
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS),
                completed_cell,
            )
        ],
    )
    inventory = paper_manifest.paper_status_claim_inventory_record(tmp_path)
    (tmp_path / paper_manifest.STATUS_CLAIM_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )
    status_path = tmp_path / paper_manifest.STATUS_LEDGER_FILE
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(
        "`papers/status_claim_inventory.json` records implementation-status evidence. "
        "Paper-index implementation-status validation now records "
        f"{inventory['todo_content_row_specific_block_record_count']} "
        "row-specific TODO block hashes/source offsets.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_reports_stale_status_claim_inventory_status_ledger_summary(
    tmp_path,
):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_status_fixture_artifact(tmp_path)
    _write_active_todo_ledgers(tmp_path, row["id"])
    completed_cell = _write_completed_todo_ledger(tmp_path)
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS),
                completed_cell,
            )
        ],
    )
    inventory = paper_manifest.paper_status_claim_inventory_record(tmp_path)
    (tmp_path / paper_manifest.STATUS_CLAIM_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )
    stale_count = inventory["todo_content_row_specific_block_record_count"] + 1
    status_path = tmp_path / paper_manifest.STATUS_LEDGER_FILE
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(
        "`papers/status_claim_inventory.json` records implementation-status evidence. "
        "Paper-index implementation-status validation now records "
        f"{stale_count} row-specific TODO block hashes/source offsets.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert (
        "status_claim_inventory_status_ledger_summary_"
        "todo_content_row_specific_block_record_count_mismatch"
    ) in codes


def test_validate_paper_manifest_rejects_missing_status_claim_local_artifact(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_active_todo_ledgers(tmp_path, row["id"])
    completed_cell = _write_completed_todo_ledger(tmp_path)
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS),
                completed_cell,
            )
        ],
    )
    inventory = paper_manifest.paper_status_claim_inventory_record(tmp_path)
    assert inventory["rows"][0]["all_local_artifacts_exist"] is False
    assert inventory["missing_local_artifact_paths"] == ["libreevolve/core/loop.py"]
    (tmp_path / paper_manifest.STATUS_CLAIM_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "status_claim_inventory_missing_local_artifact" in {
        issue.code for issue in report.issues
    }


def test_validate_paper_manifest_rejects_missing_status_claim_todo_evidence_path(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_status_fixture_artifact(tmp_path)
    _write_active_todo_ledgers(tmp_path, row["id"])
    missing_completed_cell = "`docs/todo/Completed/missing.md`"
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS),
                missing_completed_cell,
            )
        ],
    )
    inventory = paper_manifest.paper_status_claim_inventory_record(tmp_path)
    assert inventory["rows"][0]["all_todo_evidence_paths_exist"] is False
    assert inventory["missing_todo_evidence_paths"] == ["docs/todo/Completed/missing.md"]
    (tmp_path / paper_manifest.STATUS_CLAIM_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "status_claim_inventory_missing_todo_evidence_path" in {
        issue.code for issue in report.issues
    }


def test_validate_paper_manifest_rejects_status_claim_artifact_missing_from_todo_evidence(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_status_fixture_artifact(tmp_path)
    _write_active_todo_ledgers(tmp_path, row["id"], paths={"docs/todo/code.md"})
    code_todo = tmp_path / "docs" / "todo" / "code.md"
    code_todo.write_text(
        f"- [ ] Track source-specific gap for `{row['id']}`.\n"
        "  - Current gap: temporary test ledger entry without a cited artifact.\n"
        "  - Required result: keep this fixture source-specific.\n",
        encoding="utf-8",
    )
    completed_path = tmp_path / "docs" / "todo" / "Completed" / "code.md"
    completed_path.parent.mkdir(parents=True, exist_ok=True)
    completed_path.write_text(
        f"- [x] Completed fixture evidence for `{row['id']}` without a cited artifact.\n",
        encoding="utf-8",
    )
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell("docs/todo/code.md"),
                "`docs/todo/Completed/code.md`",
            )
        ],
    )
    inventory = paper_manifest.paper_status_claim_inventory_record(tmp_path)
    assert inventory["local_artifacts_missing_from_todo_evidence"] == [
        "libreevolve/core/loop.py"
    ]
    (tmp_path / paper_manifest.STATUS_CLAIM_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "status_claim_inventory_local_artifact_missing_from_todo_evidence" in {
        issue.code for issue in report.issues
    }


def test_validate_paper_manifest_rejects_status_phrase_artifact_missing_from_todo_evidence(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_status_fixture_artifact(tmp_path)
    _write_active_todo_ledgers(tmp_path, row["id"], paths={"docs/todo/code.md"})
    code_todo = tmp_path / "docs" / "todo" / "code.md"
    code_todo.write_text(
        f"- [ ] Track source-specific gap for `{row['id']}`.\n"
        "  - Current gap: temporary test ledger entry without a cited artifact.\n"
        "  - Required result: keep this fixture source-specific.\n",
        encoding="utf-8",
    )
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell("docs/todo/code.md"),
                "",
            )
        ],
    )
    inventory = paper_manifest.paper_status_claim_inventory_record(tmp_path)
    assert inventory["phrase_local_artifacts_missing_from_todo_evidence"] == [
        "libreevolve/core/loop.py"
    ]
    (tmp_path / paper_manifest.STATUS_CLAIM_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "status_claim_inventory_phrase_local_artifact_missing_from_todo_evidence" in {
        issue.code for issue in report.issues
    }


def test_validate_paper_manifest_rejects_grouped_todo_coverage_policy_text(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_active_todo_ledgers(tmp_path, row["id"])
    completed_cell = _write_completed_todo_ledger(tmp_path)
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS),
                completed_cell,
            )
        ],
    )
    readme_path = tmp_path / "papers" / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8").replace(
            "## TODO coverage cross-references\n\n",
            "## TODO coverage cross-references\n\nGrouped open gap families are accepted.\n\n",
        ),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert report.ok is False
    assert "todo_coverage_grouped_label_policy_ambiguous" in codes


def test_validate_paper_manifest_reports_stale_todo_coverage_active_cell(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_active_todo_ledgers(tmp_path, row["id"])
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell(
                    "docs/todo/code.md",
                    "docs/todo/papers.md",
                    "docs/todo/roadmap.md",
                ),
                "",
            )
        ],
    )

    report = validate_paper_manifest(tmp_path)

    issues = [issue for issue in report.issues if issue.code == "todo_coverage_active_mismatch"]
    assert report.ok is False
    assert len(issues) == 1
    assert issues[0].row_id == row["id"]
    assert "docs/todo/readme.md" in issues[0].message


def test_validate_paper_manifest_reports_missing_todo_coverage_row(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_active_todo_ledgers(tmp_path, row["id"])
    _append_todo_coverage_table(tmp_path, [])

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "missing_todo_coverage_row" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_reports_missing_active_status_evidence(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    completed_cell = _write_completed_todo_ledger(tmp_path)
    _append_todo_coverage_table(tmp_path, [(row["id"], "", completed_cell)])

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "missing_active_status_evidence" in codes


def test_validate_paper_manifest_reports_status_artifact_without_evidence_link(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_active_todo_ledgers(tmp_path, row["id"], paths={"docs/todo/code.md"})
    code_todo = tmp_path / "docs" / "todo" / "code.md"
    code_todo.write_text(
        f"- [ ] Track source-specific gap for `{row['id']}`.\n"
        "  - Current gap: temporary test ledger entry without a cited artifact.\n"
        "  - Required result: keep this fixture source-specific.\n",
        encoding="utf-8",
    )
    completed_path = tmp_path / "docs" / "todo" / "Completed" / "code.md"
    completed_path.parent.mkdir(parents=True, exist_ok=True)
    completed_path.write_text(
        f"- [x] Completed fixture evidence for `{row['id']}` without a cited artifact.\n",
        encoding="utf-8",
    )
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell("docs/todo/code.md"),
                "`docs/todo/Completed/code.md`",
            )
        ],
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "status_table_local_artifact_unlinked_evidence" in codes


def test_validate_paper_manifest_reports_active_todo_block_without_gap_context(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_active_todo_ledgers(tmp_path, row["id"])
    code_todo = tmp_path / "docs" / "todo" / "code.md"
    code_todo.write_text(
        f"- [ ] Track source-specific gap for `{row['id']}`.\n"
        "  - Required result: keep this fixture source-specific.\n",
        encoding="utf-8",
    )
    completed_cell = _write_completed_todo_ledger(tmp_path)
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS),
                completed_cell,
            )
        ],
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "active_todo_coverage_block_missing_gap_context" in codes


def test_validate_paper_manifest_reports_active_todo_block_without_required_result(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_active_todo_ledgers(tmp_path, row["id"])
    code_todo = tmp_path / "docs" / "todo" / "code.md"
    code_todo.write_text(
        f"- [ ] Track source-specific gap for `{row['id']}`.\n"
        "  - Current gap: temporary test ledger entry.\n",
        encoding="utf-8",
    )
    completed_cell = _write_completed_todo_ledger(tmp_path)
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS),
                completed_cell,
            )
        ],
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "active_todo_coverage_block_missing_required_result" in codes


def test_validate_paper_manifest_reports_missing_completed_status_evidence(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_active_todo_ledgers(tmp_path, row["id"])
    _append_todo_coverage_table(
        tmp_path,
        [(row["id"], _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS), "")],
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "missing_completed_status_evidence" in codes


def test_validate_paper_manifest_reports_completed_evidence_without_completed_item(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_active_todo_ledgers(tmp_path, row["id"])
    completed_path = tmp_path / "docs" / "todo" / "Completed" / "code.md"
    completed_path.parent.mkdir(parents=True, exist_ok=True)
    completed_path.write_text("- [ ] Not completed fixture evidence.\n", encoding="utf-8")
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS),
                "`docs/todo/Completed/code.md`",
            )
        ],
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "completed_todo_coverage_without_completed_item" in codes


def test_validate_paper_manifest_reports_completed_evidence_without_source_specific_item(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_active_todo_ledgers(tmp_path, row["id"])
    completed_path = tmp_path / "docs" / "todo" / "Completed" / "code.md"
    completed_path.parent.mkdir(parents=True, exist_ok=True)
    completed_path.write_text("- [x] Completed fixture evidence for another source.\n", encoding="utf-8")
    _append_todo_coverage_table(
        tmp_path,
        [
            (
                row["id"],
                _active_todo_cell(*paper_manifest.ACTIVE_TODO_LEDGER_PATHS),
                "`docs/todo/Completed/code.md`",
            )
        ],
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "completed_todo_coverage_not_source_specific" in codes


def test_validate_paper_manifest_ignores_unscoped_absence_phrase_examples(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_active_todo_ledgers(tmp_path, row["id"])
    code_todo = tmp_path / "docs" / "todo" / "code.md"
    code_todo.write_text(
        code_todo.read_text(encoding="utf-8")
        + "\n- [ ] Track generic stale-phrase validator examples.\n"
        + "  - Current evidence: phrases such as no source-specific code TODO should be scoped.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_reports_stale_source_specific_absence_wording(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    _write_active_todo_ledgers(tmp_path, row["id"])
    code_todo = tmp_path / "docs" / "todo" / "code.md"
    code_todo.write_text(
        code_todo.read_text(encoding="utf-8")
        + f"\n- [ ] Track stale absence wording for `{row['id']}`.\n"
        + "  - Current gap: no source-specific README TODO exists for this paper.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    issues = [issue for issue in report.issues if issue.code == "stale_source_specific_absence_wording"]
    assert report.ok is False
    assert len(issues) == 1
    assert issues[0].row_id == row["id"]
    assert "docs/todo/readme.md" in issues[0].message


def test_validate_paper_manifest_reports_not_implemented_benchmark_under_implemented(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    artifact_path = tmp_path / "libreevolve" / "problems" / "benchmarks" / "matrix_results.py"
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text("# matrix result evidence\n", encoding="utf-8")
    readme_path = tmp_path / "papers" / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8")
        + "\n\n## Benchmark coverage decisions\n\n"
        + "Implemented:\n\n"
        + "- `libreevolve/problems/examples/demo`: self-improvement evidence: not implemented.\n\n"
        + "Planned or background-only:\n\n"
        + "- Future systems fixtures are not implemented.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "benchmark_implemented_not_implemented_contradiction" in codes


def test_validate_paper_manifest_reports_implemented_benchmark_without_local_artifact(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    readme_path = tmp_path / "papers" / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8")
        + "\n\n## Benchmark coverage decisions\n\n"
        + "Implemented:\n\n"
        + "- Evaluation-cascade status: configured stages support thresholds.\n\n"
        + "Planned or background-only:\n\n"
        + "- Future systems fixtures are not implemented.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "benchmark_implemented_missing_local_artifact" in codes


def test_validate_paper_manifest_reports_implemented_benchmark_without_limitation_boundary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    readme_path = tmp_path / "papers" / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8")
        + "\n\n## Benchmark coverage decisions\n\n"
        + "Implemented:\n\n"
        + "- `libreevolve/problems/benchmarks/matrix_results.py`: full matrix benchmark support is implemented.\n\n"
        + "Planned or background-only:\n\n"
        + "- Future systems fixtures are not implemented.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert "benchmark_implemented_missing_limitation_boundary" in codes


def test_validate_paper_manifest_allows_scoped_not_yet_benchmark_under_implemented(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    readme_path = tmp_path / "papers" / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8")
        + "\n\n## Benchmark coverage decisions\n\n"
        + "Implemented:\n\n"
        + "- `libreevolve/problems/benchmarks/matrix_results.py`: implemented locally, but not yet a full benchmark.\n\n"
        + "Planned or background-only:\n\n"
        + "- Self-improvement evidence is not implemented.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_accepts_matching_benchmark_coverage_inventory(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    artifact_path = tmp_path / "libreevolve" / "problems" / "benchmarks" / "matrix_results.py"
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text("# matrix result evidence\n", encoding="utf-8")
    bullet_text = (
        "- `libreevolve/problems/benchmarks/matrix_results.py`: implemented locally, "
        f"tracks `{row['id']}` but not yet a full benchmark."
    )
    readme_path = tmp_path / "papers" / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8")
        + "\n\n## Benchmark coverage decisions\n\n"
        + "Implemented:\n\n"
        + bullet_text
        + "\n\n"
        + "Planned or background-only:\n\n"
        + "- Self-improvement evidence is not implemented.\n",
        encoding="utf-8",
    )
    inventory = paper_manifest.paper_benchmark_coverage_inventory_record(tmp_path)
    assert inventory["implemented_bullet_count"] == 1
    bullet = inventory["implemented_bullets"][0]
    readme_text = readme_path.read_text(encoding="utf-8")
    bullet_file_start = readme_text.find(bullet_text)
    bullet_file_end = bullet_file_start + len(bullet_text)
    assert bullet["source_span"] == {
        "path": "papers/README.md",
        "section": "Benchmark coverage decisions",
        "line_start": bullet["source_span"]["line_start"],
        "line_end": bullet["source_span"]["line_end"],
        "file_text_char_start": bullet_file_start,
        "file_text_char_end": bullet_file_end,
    }
    artifact_start = bullet_text.find("`libreevolve/problems/benchmarks/matrix_results.py`")
    artifact_end = artifact_start + len("`libreevolve/problems/benchmarks/matrix_results.py`")
    assert bullet["has_local_artifact"] is True
    assert bullet["all_local_artifacts_exist"] is True
    assert bullet["local_artifact_existing_count"] == 1
    source_token_start = bullet_text.find(row["id"])
    source_token_end = source_token_start + len(row["id"])
    assert bullet["source_ids_mentioned"] == [row["id"]]
    assert bullet["source_token_match_count"] == 1
    assert bullet["source_token_match_records"] == [
        {
            "row_id": row["id"],
            "token": row["id"],
            "bullet_text_char_start": source_token_start,
            "bullet_text_char_end": source_token_end,
            "source_span": {
                "path": "papers/README.md",
                "section": "Benchmark coverage decisions",
                "line_start": bullet["source_span"]["line_start"],
                "line_end": bullet["source_span"]["line_start"],
                "bullet_text_char_start": source_token_start,
                "bullet_text_char_end": source_token_end,
                "file_text_char_start": bullet_file_start + source_token_start,
                "file_text_char_end": bullet_file_start + source_token_end,
            },
        }
    ]
    assert bullet["local_artifact_mention_records"] == [
        {
            "path": "libreevolve/problems/benchmarks/matrix_results.py",
            "bullet_text_char_start": artifact_start,
            "bullet_text_char_end": artifact_end,
            "source_span": {
                "path": "papers/README.md",
                "section": "Benchmark coverage decisions",
                "line_start": bullet["source_span"]["line_start"],
                "line_end": bullet["source_span"]["line_start"],
                "bullet_text_char_start": artifact_start,
                "bullet_text_char_end": artifact_end,
                "file_text_char_start": bullet_file_start + artifact_start,
                "file_text_char_end": bullet_file_start + artifact_end,
            },
        }
    ]
    assert bullet["local_artifact_records"] == [
        {
            "path": "libreevolve/problems/benchmarks/matrix_results.py",
            "exists": True,
            "kind": "file",
        }
    ]
    assert bullet["limitation_signal_terms"] == ["but", "not"]
    assert [record["term"] for record in bullet["limitation_signal_records"]] == ["but", "not"]
    assert bullet["limitation_signal_records"][0]["bullet_text_char_start"] == bullet_text.find("but")
    assert bullet["limitation_signal_records"][1]["bullet_text_char_start"] == bullet_text.find("not")
    assert bullet["limitation_signal_records"][0]["source_span"]["line_start"] == bullet["source_span"]["line_start"]
    assert bullet["limitation_signal_records"][0]["source_span"]["file_text_char_start"] == (
        bullet_file_start + bullet_text.find("but")
    )
    assert bullet["limitation_signal_records"][1]["source_span"]["file_text_char_start"] == (
        bullet_file_start + bullet_text.find("not")
    )
    assert bullet["has_limitation_boundary"] is True
    assert bullet["limitation_signal_status"] == "limitation_signals_structurally_classified"
    assert inventory["source_ids_mentioned"] == [row["id"]]
    assert inventory["source_id_mention_count"] == 1
    assert inventory["source_token_match_record_count"] == 1
    assert (
        inventory["source_token_coverage_status"]
        == "source_tokens_structurally_recorded_without_semantic_verifier"
    )
    assert inventory["implemented_bullet_source_span_status"] == "file_character_offsets_recorded"
    assert inventory["implemented_bullet_mention_source_span_status"] == "file_character_offsets_recorded"
    assert inventory["unique_local_artifact_count"] == 1
    assert inventory["local_artifact_mention_record_count"] == 1
    assert inventory["missing_local_artifact_paths"] == []
    assert inventory["artifact_existence_status"] == "all_referenced_local_artifacts_present"
    assert inventory["limitation_bullet_count"] == 1
    assert inventory["limitation_bullet_ids"] == ["implemented_benchmark_001"]
    assert inventory["limitation_signal_record_count"] == 2
    assert inventory["limitation_signal_terms"] == ["but", "not"]
    assert (
        inventory["limitation_signal_inventory_status"]
        == "limitation_signals_structurally_classified_without_semantic_verifier"
    )
    assert inventory["not_implemented_contradiction_count"] == 0
    assert inventory["not_implemented_contradiction_bullet_ids"] == []
    (tmp_path / paper_manifest.BENCHMARK_COVERAGE_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_rejects_benchmark_coverage_inventory_drift(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    artifact_path = tmp_path / "libreevolve" / "problems" / "benchmarks" / "matrix_results.py"
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text("# matrix result evidence\n", encoding="utf-8")
    readme_path = tmp_path / "papers" / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8")
        + "\n\n## Benchmark coverage decisions\n\n"
        + "Implemented:\n\n"
        + "- `libreevolve/problems/benchmarks/matrix_results.py`: implemented locally, but not yet a full benchmark.\n\n"
        + "Planned or background-only:\n\n"
        + "- Self-improvement evidence is not implemented.\n",
        encoding="utf-8",
    )
    inventory = paper_manifest.paper_benchmark_coverage_inventory_record(tmp_path)
    inventory["implemented_bullets"][0]["body_sha256"] = "0" * 64
    (tmp_path / paper_manifest.BENCHMARK_COVERAGE_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "benchmark_coverage_inventory_implemented_bullets_mismatch" in {
        issue.code for issue in report.issues
    }


def test_validate_paper_manifest_accepts_benchmark_coverage_readme_summary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    artifact_path = tmp_path / "libreevolve" / "problems" / "benchmarks" / "matrix_results.py"
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text("# matrix result evidence\n", encoding="utf-8")
    readme_path = tmp_path / "papers" / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8")
        + "\n\n## Benchmark coverage decisions\n\n"
        + "Implemented:\n\n"
        + f"- `libreevolve/problems/benchmarks/matrix_results.py`: implemented locally, tracks `{row['id']}` but not yet a full benchmark.\n\n"
        + "Planned or background-only:\n\n"
        + "- Self-improvement evidence is not implemented.\n",
        encoding="utf-8",
    )
    inventory = paper_manifest.paper_benchmark_coverage_inventory_record(tmp_path)
    (tmp_path / paper_manifest.BENCHMARK_COVERAGE_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8")
        + "\n"
        + "- `papers/benchmark_coverage_inventory.json`: structural inventory. "
        + "The current inventory records "
        + f"{inventory['source_id_mention_count']} referenced manifest source IDs across "
        + f"{inventory['source_token_match_record_count']} source-token match records, "
        + f"{inventory['unique_local_artifact_count']} unique referenced local artifact paths, "
        + "and zero missing referenced local artifacts.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is True


def test_validate_paper_manifest_reports_stale_benchmark_coverage_readme_summary(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    artifact_path = tmp_path / "libreevolve" / "problems" / "benchmarks" / "matrix_results.py"
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text("# matrix result evidence\n", encoding="utf-8")
    readme_path = tmp_path / "papers" / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8")
        + "\n\n## Benchmark coverage decisions\n\n"
        + "Implemented:\n\n"
        + f"- `libreevolve/problems/benchmarks/matrix_results.py`: implemented locally, tracks `{row['id']}` but not yet a full benchmark.\n\n"
        + "Planned or background-only:\n\n"
        + "- Self-improvement evidence is not implemented.\n",
        encoding="utf-8",
    )
    inventory = paper_manifest.paper_benchmark_coverage_inventory_record(tmp_path)
    (tmp_path / paper_manifest.BENCHMARK_COVERAGE_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )
    stale_count = inventory["unique_local_artifact_count"] + 1
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8")
        + "\n"
        + "- `papers/benchmark_coverage_inventory.json`: structural inventory. "
        + "The current inventory records "
        + f"{inventory['source_id_mention_count']} referenced manifest source IDs across "
        + f"{inventory['source_token_match_record_count']} source-token match records, "
        + f"{stale_count} unique referenced local artifact paths, "
        + "and zero missing referenced local artifacts.\n",
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert report.ok is False
    assert (
        "benchmark_coverage_inventory_readme_summary_"
        "unique_local_artifact_count_mismatch"
    ) in codes


def test_validate_paper_manifest_rejects_missing_benchmark_coverage_local_artifact(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    _write_status_table(tmp_path, [row["id"]])
    readme_path = tmp_path / "papers" / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8")
        + "\n\n## Benchmark coverage decisions\n\n"
        + "Implemented:\n\n"
        + "- `libreevolve/problems/benchmarks/missing_results.py`: implemented locally, but not yet a full benchmark.\n\n"
        + "Planned or background-only:\n\n"
        + "- Self-improvement evidence is not implemented.\n",
        encoding="utf-8",
    )
    inventory = paper_manifest.paper_benchmark_coverage_inventory_record(tmp_path)
    assert inventory["implemented_bullets"][0]["all_local_artifacts_exist"] is False
    assert inventory["missing_local_artifact_paths"] == [
        "libreevolve/problems/benchmarks/missing_results.py"
    ]
    (tmp_path / paper_manifest.BENCHMARK_COVERAGE_INVENTORY_FILE).write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )

    report = validate_paper_manifest(tmp_path)

    assert report.ok is False
    assert "benchmark_coverage_inventory_missing_local_artifact" in {
        issue.code for issue in report.issues
    }


def test_checked_in_paper_index_maps_each_manifest_id_to_todo_coverage():
    manifest_rows = json.loads(Path("papers/download_manifest.json").read_text(encoding="utf-8"))
    readme = Path("papers/README.md").read_text(encoding="utf-8")

    section = readme.split("## TODO coverage cross-references", 1)[1].split("\n## ", 1)[0]
    for row in manifest_rows:
        prefix = f"| {row['id']} |"
        matches = [line for line in section.splitlines() if line.startswith(prefix)]
        assert len(matches) == 1
        assert "docs/todo/" in matches[0]


def test_checked_in_docs_scope_manifest_title_as_inventory_slug():
    readme = Path("README.md").read_text(encoding="utf-8")
    papers_readme = Path("papers/README.md").read_text(encoding="utf-8")

    for text in (readme, papers_readme):
        assert "Manifest `title`" in text
        assert "inventory/display slug" in text
        assert "not authoritative bibliographic" in text


def test_validate_paper_manifest_rejects_non_pdf_content(tmp_path):
    row = _row(tmp_path, content=b"not a pdf at all\n")
    _write_manifest(tmp_path, [row])

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    assert report.ok is False
    assert "invalid_pdf_header" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_rejects_header_only_fake_pdf(tmp_path):
    row = _row(tmp_path, content=b"%PDF-1.4\nfake\n")
    _write_manifest(tmp_path, [row])

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    assert report.ok is False
    assert "invalid_pdf_structure" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_hashes_local_pdfs_streaming(tmp_path, monkeypatch):
    row = _row(tmp_path, content=_valid_pdf_bytes(b"\n" + (b"x" * 2_000_000)))
    _write_manifest(tmp_path, [row])

    def fail_read_bytes(path):
        raise AssertionError("read_bytes should not be used for paper hashing")

    monkeypatch.setattr(Path, "read_bytes", fail_read_bytes)

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    assert report.ok is True


def test_validate_paper_manifest_rejects_failed_download_rows(tmp_path):
    row = _row(tmp_path, ok=False, message="download failed: HTTP 500")
    _write_manifest(tmp_path, [row])

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    assert report.ok is False
    assert report.availability[0].download_ok is False
    assert "download_failed" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_reports_unmanifested_local_pdfs_when_required(tmp_path):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    (tmp_path / "papers" / "extra.pdf").write_bytes(b"%PDF-1.4\nextra\n")

    optional_report = validate_paper_manifest(tmp_path)
    required_report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    assert optional_report.ok is True
    assert required_report.ok is False
    assert "unmanifested_pdf" in {issue.code for issue in required_report.issues}


def test_validate_paper_manifest_rejects_symlink_backed_local_pdf(tmp_path, monkeypatch):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    target = tmp_path / row["file"]
    real_is_symlink = Path.is_symlink

    def fake_is_symlink(path):
        if path == target:
            return True
        return real_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", fake_is_symlink)

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    assert report.ok is False
    assert "linked_pdf" in {issue.code for issue in report.issues}


def test_validate_paper_manifest_rejects_reparse_point_local_pdf(tmp_path, monkeypatch):
    row = _row(tmp_path)
    _write_manifest(tmp_path, [row])
    target = tmp_path / row["file"]
    real_lstat = Path.lstat
    monkeypatch.setattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024, raising=False)

    def fake_lstat(path):
        if path == target:
            return SimpleNamespace(st_file_attributes=1024, st_mode=stat.S_IFREG | 0o644)
        return real_lstat(path)

    monkeypatch.setattr(Path, "lstat", fake_lstat)

    report = validate_paper_manifest(tmp_path, require_local_pdfs=True)

    assert report.ok is False
    assert "linked_pdf" in {issue.code for issue in report.issues}
