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
    _write_manifest(tmp_path, [row])
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


def test_validate_paper_manifest_accepts_matching_source_identity_manifest(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
    (tmp_path / "papers" / "row_identity.json").write_text(
        json.dumps(paper_source_identity_manifest_record([row]), indent=2),
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


def test_validate_paper_manifest_accepts_matching_follow_on_source_manifest(tmp_path):
    source_record = alphaevolve_source_pdf_version_record()
    row = dict(source_record["manifest_row"])
    row.pop("url_kind")
    row.update({"ok": True, "message": "downloaded"})
    _write_manifest(tmp_path, [row])
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
    _write_manifest(tmp_path, [row])
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
