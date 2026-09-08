import hashlib
from types import SimpleNamespace

import pytest

from libreevolve import alpha_report
from libreevolve.core import run_inspection
from libreevolve import alpha_share_prepare as prepare


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    run = tmp_path / "run"
    run.mkdir()
    workspace = run / "best_workspace"
    workspace.mkdir()
    (workspace / "seed.py").write_text("seed")
    monkeypatch.setattr(run_inspection, "inspect_run", lambda _: SimpleNamespace(workspace=("seed.py", {"seed.py": "seed"}), selection="archive-retained valid"))
    monkeypatch.setattr(run_inspection, "read_manifest", lambda _: {"runtime": {"status": "aborted", "consumed": {"runtime_seconds": 1}}})
    monkeypatch.setattr(alpha_report, "_usage", lambda *args: {"calls": 0, "total_tokens": None, "estimated_cost_usd": None})
    monkeypatch.setattr(prepare, "_corpora", lambda: {"validator_sha256": "b" * 64, "corpora": {
        split: {"corpus_id": "synthetic-" + split, "corpus_sha256": "c" * 64, "case_count": 4}
        for split in ("training", "holdout")}})
    calls = []
    def verify(code):
        calls.append(code)
        digest = hashlib.sha256(code).hexdigest()
        return {"code_sha256": digest, "validator_sha256": "b" * 64,
                **{split: {"code_sha256": digest, "validator_sha256": "b" * 64,
                           "status": "completed", "correctness": True, "score": 0.8,
                           "metrics": {"case_count": 4, "total_bins": 10}}
                   for split in ("training", "holdout")}}
    monkeypatch.setattr(alpha_report, "verify_candidate", verify)
    return run, calls


def test_proposal_allowlist_and_source_evidence(prepared):
    run, calls = prepared
    public, private = prepare.prepare_run(run, public_result_id="synthetic-test")
    assert len(calls) == 2
    assert public["run_status"] == "aborted"
    assert public["usage"]["cost_usd"] is None
    assert private["source_kind"] == "workspace" and private["matches_history"]
    assert "code" not in public and "run_dir" not in public
    assert public["approved_source_url"] is None
    assert public["candidate_retention"] == "retained"


def test_conflict_rejected_before_execution_and_explicit_history_works(prepared):
    run, calls = prepared
    (run / "best_workspace/seed.py").write_text("different")
    with pytest.raises(ValueError, match="differs"):
        prepare.prepare_run(run, public_result_id="synthetic-test")
    assert calls == []
    _, private = prepare.prepare_run(run, public_result_id="synthetic-test", source="history")
    assert calls[0] == b"seed"
    assert private["source_kind"] == "history"


def test_invalid_public_id_rejected_before_execution(prepared):
    run, calls = prepared
    with pytest.raises(ValueError, match="public result ID"):
        prepare.prepare_run(run, public_result_id="../private")
    assert calls == []


def test_hash_mismatch_fails_closed(prepared, monkeypatch):
    run, _ = prepared
    monkeypatch.setattr(alpha_report, "verify_candidate", lambda _: {"code_sha256": "f" * 64, "training": {}})
    with pytest.raises(ValueError, match="hash"):
        prepare.prepare_run(run, public_result_id="synthetic-test")


def test_explicit_workspace_records_history_mismatch(prepared):
    run, calls = prepared
    (run / "best_workspace/seed.py").write_text("different")
    public, private = prepare.prepare_run(run, public_result_id="synthetic-test", source="workspace")
    assert calls[0] == b"different"
    assert private["source_kind"] == "workspace"
    assert private["matches_history"] is False
    assert public["candidate_retention"] == "not_established"
    assert public["public_provenance"]["candidate_sha256"] == hashlib.sha256(b"different").hexdigest()


def test_corpus_count_mismatch_rejected(prepared, monkeypatch):
    run, _ = prepared
    original = alpha_report.verify_candidate
    def wrong_count(code):
        result = original(code)
        result["training"]["metrics"]["case_count"] = 3
        return result
    monkeypatch.setattr(alpha_report, "verify_candidate", wrong_count)
    with pytest.raises(ValueError, match="named corpus"):
        prepare.prepare_run(run, public_result_id="synthetic-test")


def test_validator_identity_mismatch_rejected(prepared, monkeypatch):
    run, _ = prepared
    original = alpha_report.verify_candidate
    def wrong_validator(code):
        result = original(code)
        result["training"]["validator_sha256"] = "d" * 64
        return result
    monkeypatch.setattr(alpha_report, "verify_candidate", wrong_validator)
    with pytest.raises(ValueError, match="hash"):
        prepare.prepare_run(run, public_result_id="synthetic-test")


def test_holdout_identity_is_distinct(prepared):
    run, _ = prepared
    public, _ = prepare.prepare_run(run, public_result_id="synthetic-test", split="holdout")
    assert public["candidate"]["split"] == "holdout"
    assert public["candidate"]["corpus_id"] == "synthetic-holdout"
    assert all(check["split"] == "holdout" for check in public["checks"])
