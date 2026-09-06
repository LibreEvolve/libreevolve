"""Independent local verification and truthful artifact reporting contracts."""

import hashlib
import json
import os
import signal
import time

import pytest

from libreevolve import alpha_report as reporting


def baseline():
    return (reporting.BUNDLED_PROBLEM / "initial_programs/seed.py").read_bytes()


def run_fixture(tmp_path, manifest=None, code=None):
    (tmp_path / "best_workspace").mkdir()
    (tmp_path / "best_workspace/seed.py").write_bytes(baseline() if code is None else code)
    if manifest is not None:
        (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path


def test_public_verification_hashes_and_both_splits():
    raw = baseline()
    result = reporting.verify_candidate(raw)
    expected_validator = hashlib.sha256((reporting.BUNDLED_PROBLEM / "validate.py").read_bytes()).hexdigest()
    assert result["code_sha256"] == hashlib.sha256(raw).hexdigest()
    assert result["validator_sha256"] == expected_validator
    for split, count in (("training", 55), ("holdout", 30)):
        row = result[split]
        assert row["status"] == "completed" and row["correctness"] is True
        assert row["metrics"]["case_count"] == count
        assert row["code_sha256"] == result["code_sha256"]
        assert row["validator_sha256"] == expected_validator
        assert 0 < row["score"] <= 1


@pytest.mark.parametrize("code", ["not python!", "def pack(items, capacity): return []", "raise SystemExit(0)"])
def test_invalid_candidates_are_not_verified(code):
    result = reporting.verify_candidate(code)
    for split in ("training", "holdout"):
        assert result[split]["status"] == "completed"
        assert result[split]["correctness"] is False


def test_timeout_is_unknown_correctness(monkeypatch):
    monkeypatch.setattr(reporting, "VERIFY_TIMEOUT_SECONDS", 0.3)
    started = time.monotonic()
    result = reporting.verify_candidate("while True: pass")
    assert time.monotonic() - started < 6
    for split in ("training", "holdout"):
        assert result[split]["status"] == "timeout"
        assert result[split]["correctness"] is None
        assert result[split]["score"] is None


def test_candidate_never_executes_in_parent_and_prints_are_suppressed():
    code = f"import os\nassert os.getpid() != {os.getpid()}\nos.write(1, b'x' * 200000)\nprint('noise' * 100000)\n" + baseline().decode()
    result = reporting.verify_candidate(code)
    assert result["training"]["correctness"] is True
    assert result["holdout"]["correctness"] is True


def test_worker_environment_excludes_credentials_and_python_injection(monkeypatch):
    names = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY",
             "AWS_SECRET_ACCESS_KEY", "CUSTOM_PROVIDER_SECRET", "PYTHONPATH")
    for name in names:
        monkeypatch.setenv(name, "alpha-test-secret-never-inherited")
    code = f"import os\nassert not any(name in os.environ for name in {names!r})\n" + baseline().decode()
    result = reporting.verify_candidate(code)
    assert result["training"]["correctness"] is True
    assert result["holdout"]["correctness"] is True
    assert all(os.environ[name] == "alpha-test-secret-never-inherited" for name in names)


def _child_running(pid):
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.WaitForSingleObject.restype = wintypes.DWORD
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
        if not handle:
            if ctypes.get_last_error() == 87:  # PID no longer exists.
                return False
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            return kernel.WaitForSingleObject(handle, 2000) == 258
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    from pathlib import Path
    stat = Path(f"/proc/{pid}/stat")
    return not (stat.exists() and stat.read_text().split(") ", 1)[1].startswith("Z"))


@pytest.mark.parametrize("ending,status", [
    ("while True: pass", "timeout"),
    ("for fd in range(3, 32):\n    try: os.write(fd, b'x' * 200000)\n    except OSError: pass", "output_limit"),
    ("", "completed"),
])
def test_worker_descendant_cleanup(tmp_path, monkeypatch, ending, status):
    monkeypatch.setattr(reporting, "VERIFY_TIMEOUT_SECONDS", 1.5)
    pid_path = tmp_path / "child.pid"
    code = (
        "import subprocess, sys, os\nfrom pathlib import Path\n"
        "child = subprocess.Popen([sys.executable, '-I', '-c', 'import time; time.sleep(60)'])\n"
        f"Path({str(pid_path)!r}).write_text(str(child.pid))\n"
        + ending + "\n" + baseline().decode()
    )
    validator = (reporting.BUNDLED_PROBLEM / "validate.py").read_bytes()
    result = reporting._verify(code.encode(), validator, "evaluate")
    assert pid_path.exists(), result
    pid = int(pid_path.read_text())
    try:
        assert result["status"] == status
        assert not _child_running(pid), "Verification left its candidate child running"
    finally:
        if _child_running(pid):
            os.kill(pid, signal.SIGTERM)


@pytest.mark.skipif(os.name != "nt", reason="Windows job containment gate")
def test_windows_job_assignment_failure_does_not_execute_candidate(tmp_path, monkeypatch):
    marker = tmp_path / "must-not-exist"
    monkeypatch.setattr(reporting, "_assign_windows_kill_job", lambda process: {"assigned": False})
    result = reporting.verify_candidate(f"from pathlib import Path\nPath({str(marker)!r}).touch()")
    assert result["training"]["status"] == "error"
    assert not marker.exists()


def test_missing_run_does_not_claim_zero_usage(tmp_path):
    result = reporting.build_report(tmp_path / "missing")
    assert result["status"] == "no_result"
    assert result["export_status"] == "absent"
    assert result["best"] is None
    assert result["runtime"]["status"] is None
    assert result["usage"]["total_tokens"] is None
    assert result["usage"]["estimated_cost_usd"] is None
    assert result["baseline"]["training"]["correctness"] is True


@pytest.mark.parametrize("content", ['{', '[]', '{"runtime":{},"runtime":{}}', '{"runtime":{"x":NaN}}'])
def test_corrupt_manifest_retains_independent_evidence(tmp_path, content):
    run_fixture(tmp_path)
    (tmp_path / "manifest.json").write_text(content, encoding="utf-8")
    result = reporting.build_report(tmp_path)
    assert result["manifest_status"] == "corrupt"
    assert result["status"] == "verified"
    assert result["usage"]["total_tokens"] is None
    assert result["score_delta"] == {"training": 0, "holdout": 0}


def test_actual_manifest_consumed_usage_shape(tmp_path):
    manifest = {"config": {"backends": [{"model": "configured"}]},
                "runtime": {"status": "completed", "stop_reason": "max_llm_tokens",
                            "consumed": {"runtime_seconds": 12.5, "llm_calls": 1,
                                         "llm_tokens": 10, "llm_cost_microusd": 30}}}
    run_fixture(tmp_path, manifest)
    (tmp_path / "llm_calls.jsonl").write_text(json.dumps({"backend_metadata": {"model": "observed"},
        "usage": {"input_tokens": 7, "output_tokens": 3, "total_tokens": 10},
        "cost_estimate": {"cost_microusd": 30}}) + "\n", encoding="utf-8")
    result = reporting.build_report(tmp_path)
    assert result["runtime"]["elapsed_seconds"] == 12.5
    assert result["runtime"]["stop_reason"] == "max_llm_tokens"
    assert result["usage"]["total_tokens"] == 10
    assert result["usage"]["estimated_cost_usd"] == 0.00003
    assert result["usage"]["models"] == ["observed"]
    assert result["usage"]["configured_models"] == ["configured"]


@pytest.mark.parametrize("stream", [None, '{}\n', '{"usage":{"total_tokens":3}}\n{'])
def test_partial_usage_does_not_turn_accounting_zero_into_measured_zero(tmp_path, stream):
    run_fixture(tmp_path, {"runtime": {"consumed": {"llm_calls": 1, "llm_tokens": 0, "llm_cost_microusd": 0}}})
    if stream is not None:
        (tmp_path / "llm_calls.jsonl").write_text(stream, encoding="utf-8")
    result = reporting.build_report(tmp_path)
    assert result["usage"]["total_tokens"] is None
    assert result["usage"]["estimated_cost_usd"] is None
    assert result["usage"]["recorded_tokens"] == 0


def test_aborted_no_export_preserves_status_and_checks_history(tmp_path):
    (tmp_path / "manifest.json").write_text(json.dumps({"runtime": {
        "status": "aborted", "stop_reason": "keyboard_interrupt", "abort": {"keyboard_interrupt": True}}}), encoding="utf-8")
    (tmp_path / "history.jsonl").write_text('{broken\n', encoding="utf-8")
    result = reporting.build_report(tmp_path)
    assert result["status"] == "no_result"
    assert result["runtime"]["abort"]["keyboard_interrupt"] is True
    assert result["recoverable_history"]["status"] == "unavailable"


def test_recoverable_history_is_not_implicitly_exported(tmp_path):
    code = baseline().decode("utf-8")
    (tmp_path / "history.jsonl").write_text(json.dumps({
        "id": "seed", "code": code, "fitness": 0.8, "generation": 0,
        "files": {"seed.py": code}, "primary_file": "seed.py"}) + "\n", encoding="utf-8")
    result = reporting.build_report(tmp_path)
    assert result["status"] == "no_result"
    assert result["best"] is None
    assert result["recoverable_history"]["status"] == "available_for_explicit_export"
    assert result["recoverable_history"]["primary_file"] == "seed.py"
    assert not (tmp_path / "best_workspace").exists()


def test_improved_candidate_has_independent_score_deltas_and_diff(tmp_path):
    code = b'''def pack(items, capacity):
    bins = []
    for item in sorted(items, reverse=True):
        for bucket in bins:
            if sum(bucket) + item <= capacity:
                bucket.append(item)
                break
        else:
            bins.append([item])
    return bins
'''
    run_fixture(tmp_path, code=code)
    result = reporting.build_report(tmp_path)
    assert result["status"] == "verified"
    assert result["score_delta"]["training"] > 0
    assert result["score_delta"]["holdout"] > 0
    assert "+    for item in sorted" in result["diff"]
    assert result["best"]["code_sha256"] != result["baseline"]["code_sha256"]


def test_manifest_primary_hash_disagreement_is_explicit(tmp_path):
    run_fixture(tmp_path, {"runtime": {"best_artifact_export": {"paths": {
        "best.py": {"sha256": "0" * 64}}}}})
    result = reporting.build_report(tmp_path)
    assert result["status"] == "verified_modified_export"
    assert result["best"]["manifest_primary_match"] is False
    assert any(issue["status"] == "hash_mismatch" for issue in result["issues"])


def test_windows_export_newline_difference_retains_exact_hashes(tmp_path):
    raw = baseline().replace(b"\r\n", b"\n")
    compatibility = raw.replace(b"\n", b"\r\n")
    expected = hashlib.sha256(compatibility).hexdigest()
    run_fixture(tmp_path, {"runtime": {"best_artifact_export": {"paths": {
        "best.py": {"sha256": expected}}}}}, raw)
    (tmp_path / "best.py").write_bytes(compatibility)
    result = reporting.build_report(tmp_path)
    assert result["status"] == "verified"
    assert result["best"]["manifest_primary_match"] is True
    assert result["best"]["manifest_primary_sha256"] == expected
    assert result["best"]["code_sha256"] == hashlib.sha256(raw).hexdigest()
    assert result["best"]["manifest_primary_match_kind"] == "manifest_verified_best.py_with_CRLF_normalized"
    # Textual equality is insufficient if the compatibility export was changed.
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    manifest["runtime"]["best_artifact_export"]["paths"]["best.py"]["sha256"] = "0" * 64
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert reporting.build_report(tmp_path)["status"] == "verified_modified_export"


def test_primary_escape_is_rejected(tmp_path):
    run_fixture(tmp_path, {"best_program": {"primary_file": "../evil.py"}})
    assert reporting.build_report(tmp_path)["status"] == "no_result"


def test_actual_manifest_seed_primary_is_checked(tmp_path):
    run_fixture(tmp_path, {"problem": {"seed_sources": [{"primary_file": "main.py"}]}})
    assert reporting.build_report(tmp_path)["status"] == "no_result"


def test_worker_crash_is_not_correctness_failure():
    result = reporting.verify_candidate("import os; os._exit(9)")
    assert result["training"]["status"] == "worker_failed"
    assert result["training"]["returncode"] == 9
    assert result["training"]["correctness"] is None


def test_response_pipe_flood_is_bounded(monkeypatch):
    monkeypatch.setattr(reporting, "VERIFY_TIMEOUT_SECONDS", 2)
    # Write to the worker's retained response descriptor. This intentionally
    # demonstrates that process isolation is not a hostile-code sandbox.
    code = """import os
for fd in range(3, 32):
    try:
        os.write(fd, b'x' * 200000)
    except OSError:
        pass
"""
    result = reporting.verify_candidate(code)
    assert result["training"]["status"] == "output_limit"
    assert result["training"]["correctness"] is None


def test_failed_no_valid_programs_manifest_is_not_success(tmp_path):
    (tmp_path / "manifest.json").write_text(json.dumps({"runtime": {
        "status": "completed", "stop_reason": "no_valid_programs",
        "consumed": {"llm_calls": 0, "llm_tokens": 0, "runtime_seconds": 1.453}}}), encoding="utf-8")
    (tmp_path / "history.jsonl").write_text('', encoding="utf-8")
    result = reporting.build_report(tmp_path)
    assert result["status"] == "no_result"
    assert result["runtime"]["status"] == "completed"
    assert result["runtime"]["stop_reason"] == "no_valid_programs"
    assert result["usage"]["total_tokens"] is None
    assert result["best"] is None


def test_html_escapes_all_untrusted_fields():
    attack = '</pre><script>alert("x")</script><img src=x onerror=alert(1)>'
    report = {"status": attack, "scope": attack, "runtime": {"stop_reason": attack},
              "diff": attack, "best": {"code": attack, "training": {"status": attack}}}
    page = reporting.render_html(report)
    assert "<script" not in page and "<img" not in page
    assert "&lt;script&gt;" in page
    assert '<html lang="en">' in page and '<main>' in page and '<caption>' in page
    assert '<script' not in page and '<link' not in page


def test_no_problem_validator_imported_in_parent(tmp_path, monkeypatch):
    fixture = tmp_path / "fixture"
    (fixture / "initial_programs").mkdir(parents=True)
    (fixture / "initial_programs/seed.py").write_bytes(baseline())
    source = (reporting.BUNDLED_PROBLEM / "validate.py").read_text(encoding="utf-8")
    (fixture / "validate.py").write_text(f"import os\nassert os.getpid() != {os.getpid()}\n" + source, encoding="utf-8")
    monkeypatch.setattr(reporting, "BUNDLED_PROBLEM", fixture)
    assert reporting.verify_candidate(baseline())["training"]["correctness"] is True
