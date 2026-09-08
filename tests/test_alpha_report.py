"""Independent local verification and truthful artifact reporting contracts."""

import errno
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from libreevolve import alpha_report as reporting


def baseline():
    return (reporting.BUNDLED_PROBLEM / "initial_programs/seed.py").read_bytes()


def test_codex_usage_retains_tokens_without_fabricating_subscription_cost(tmp_path):
    manifest = {"config": {"backends": [{"type": "codex", "model": "gpt-5.6-luna"}]},
                "runtime": {"consumed": {"llm_calls": 1, "llm_tokens": 12,
                                         "llm_cost_microusd": 0}}}
    (tmp_path / "llm_calls.jsonl").write_text(json.dumps({
        "backend_name": "codex-cli/gpt-5.6-luna",
        "usage": {"input_tokens": 9, "output_tokens": 3, "total_tokens": 12},
    }) + "\n", encoding="utf-8")
    usage = reporting._usage(tmp_path, manifest, [])
    assert usage["total_tokens"] == 12
    assert usage["estimated_cost_usd"] is None
    assert "does not mean zero cost" in usage["note"]


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("cost_microusd", [None, 30])
def test_successful_call_with_reward_retains_known_usage(tmp_path, legacy, cost_microusd):
    manifest = {"config": {"backends": [{"type": "codex", "model": "gpt-5.6-luna"}]},
                "runtime": {"consumed": {"llm_calls": 1}}}
    call = {"id": "successful-call", "backend_name": "codex-cli/gpt-5.6-luna",
            "backend_metadata": {"model": "gpt-5.6-luna"}, "status": "ok",
            "usage": {"input_tokens": 13289, "output_tokens": 6412, "total_tokens": 19701},
            "cost_estimate": None if cost_microusd is None else {"cost_microusd": cost_microusd}}
    if not legacy:
        call["record_type"] = "call"
    reward = {"record_type": "reward", "call_id": "successful-call",
              "backend_idx": 0, "reward": 0.17657723529567304, "rewarded": True}
    (tmp_path / "llm_calls.jsonl").write_text(
        json.dumps(call) + "\n" + json.dumps(reward) + "\n", encoding="utf-8")
    issues = []
    usage = reporting._usage(tmp_path, manifest, issues)
    assert issues == []
    assert usage["observed_call_records"] == usage["calls"] == 1
    assert usage["models"] == ["gpt-5.6-luna"]
    assert usage["observed_backend_names"] == ["codex-cli/gpt-5.6-luna"]
    assert (usage["input_tokens"], usage["output_tokens"], usage["total_tokens"]) == (13289, 6412, 19701)
    assert usage["estimated_cost_usd"] == (None if cost_microusd is None else 0.00003)
    assert usage["status"] == ("partial" if cost_microusd is None else "complete")
    assert usage["attempt_outcomes"]["successful_calls"] == 1
    assert usage["attempt_outcomes"]["failed_calls"] == 0
    assert usage["attempt_outcomes"]["status"] == "complete"


@pytest.mark.parametrize("record_type", ["unknown", "", None, 1, [], {}])
def test_unknown_record_type_prevents_complete_usage(tmp_path, record_type):
    call = {"record_type": "call", "usage": {"input_tokens": 7, "output_tokens": 3, "total_tokens": 10},
            "cost_estimate": {"cost_microusd": 30}}
    (tmp_path / "llm_calls.jsonl").write_text(
        json.dumps(call) + "\n" + json.dumps({"record_type": record_type}) + "\n", encoding="utf-8")
    issues = []
    usage = reporting._usage(tmp_path, {"runtime": {"consumed": {"llm_calls": 1}}}, issues)
    assert usage["observed_call_records"] == 1
    assert usage["status"] == "partial"
    assert usage["total_tokens"] is None
    assert usage["estimated_cost_usd"] is None
    assert issues[0]["status"] == "corrupt"
    assert "record_type" in issues[0]["detail"]


@pytest.mark.parametrize("ignored_line", ['{"record_type":"reward"}\n', '\n'])
def test_usage_stream_limit_counts_ignored_lines(tmp_path, monkeypatch, ignored_line):
    monkeypatch.setattr(reporting, "MAX_LLM_STREAM_RECORDS", 3)
    call = {"record_type": "call", "usage": {"total_tokens": 10},
            "cost_estimate": {"cost_microusd": 30}}
    path = tmp_path / "llm_calls.jsonl"
    manifest = {"runtime": {"consumed": {"llm_calls": 1}}}
    path.write_text(json.dumps(call) + "\n" + ignored_line * 2, encoding="utf-8")
    issues = []
    assert reporting._usage(tmp_path, manifest, issues)["status"] == "complete"
    assert issues == []
    path.write_text(json.dumps(call) + "\n" + ignored_line * 3, encoding="utf-8")
    usage = reporting._usage(tmp_path, manifest, issues)
    assert usage["observed_call_records"] == 1
    assert usage["total_tokens"] is None
    assert usage["estimated_cost_usd"] is None
    assert usage["status"] == "partial"
    assert issues[0]["status"] == "corrupt"
    assert "exceeds report limit" in issues[0]["detail"]


def run_fixture(tmp_path, manifest=None, code=None):
    (tmp_path / "best_workspace").mkdir()
    (tmp_path / "best_workspace/seed.py").write_bytes(baseline() if code is None else code)
    if manifest is not None:
        (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path


def test_completed_run_with_all_timeouts_explains_unchanged_seed(tmp_path, monkeypatch):
    # Test report composition without adding another execution of the fixture.
    monkeypatch.setattr(reporting, "_verify", lambda *args: {
        "status": "completed", "correctness": True, "score": 0.8})
    manifest = {"runtime": {"status": "completed", "stop_reason": "max_llm_calls",
                           "consumed": {"llm_calls": 3, "llm_tokens": 0,
                                        "llm_cost_microusd": 0, "evaluations": 1,
                                        "seed_evaluations": 1, "candidate_evaluations": 0}}}
    run_fixture(tmp_path, manifest)
    call = {"record_type": "call", "status": "error", "error_type": "ProviderCallTimeoutError",
            "provider_failure_category": "timeout", "usage": None, "cost_estimate": None}
    (tmp_path / "llm_calls.jsonl").write_text((json.dumps(call) + "\n") * 3, encoding="utf-8")
    report = reporting.build_report(tmp_path)
    outcomes = report["usage"]["attempt_outcomes"]
    assert report["status"] == "verified"  # Verification still describes the exported bytes.
    assert report["runtime"]["status"] == "completed"
    assert report["runtime"]["stop_reason"] == "max_llm_calls"
    assert report["runtime"]["evaluation_counts"]["candidate_evaluations"] == 0
    assert outcomes["ledger_status"] == outcomes["status"] == "complete"
    assert outcomes["successful_calls"] == outcomes["unknown_status_calls"] == 0
    assert outcomes["failed_calls"] == outcomes["timeout_calls"] == 3
    assert outcomes["failure_groups"] == [{"category": "timeout", "error_type": "ProviderCallTimeoutError", "calls": 3}]
    assert report["usage"]["total_tokens"] is report["usage"]["estimated_cost_usd"] is None
    page = reporting.render_html(report)
    assert "Selected export is unchanged from the bundled seed." in page
    assert "3 failed (3 timeouts)" in page
    assert "Every observed provider call failed" in page
    assert "The run recorded no generated candidate evaluations." in page
    assert page.index("Every observed provider call failed") < page.index("Usage and estimated cost")


def test_mixed_attempts_keep_provider_success_distinct_from_candidate_success(tmp_path):
    rows = [{"status": "ok"}, {"status": "error", "error_type": "TimeoutError"},
            {"status": "error", "error_type": "HTTPError", "provider_failure_category": "rate_limit"},
            {"record_type": "reward", "status": "ok"}]
    (tmp_path / "llm_calls.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    usage = reporting._usage(tmp_path, {"runtime": {"consumed": {"llm_calls": 3}}}, [])
    outcomes = usage["attempt_outcomes"]
    assert outcomes["successful_calls"] == 1
    assert outcomes["failed_calls"] == 2
    assert outcomes["timeout_calls"] == 1
    assert "Every observed provider call failed" not in outcomes["summary"]
    assert "does not establish a valid, retained or improving candidate" in outcomes["note"]


@pytest.mark.parametrize("status", [None, "", "timeout", "success", [], {}, 1])
def test_unknown_call_status_is_never_inferred_success_or_failure(tmp_path, status):
    (tmp_path / "llm_calls.jsonl").write_text(json.dumps({
        "status": status, "error_type": "TimeoutError", "usage": {"total_tokens": 10},
        "cost_estimate": {"cost_microusd": 30}}) + "\n", encoding="utf-8")
    usage = reporting._usage(tmp_path, {"runtime": {"consumed": {"llm_calls": 1}}}, [])
    outcomes = usage["attempt_outcomes"]
    assert usage["status"] == "complete"  # Usage and outcomes have independent completeness.
    assert outcomes["ledger_status"] == "complete"
    assert outcomes["status"] == "partial"
    assert outcomes["unknown_status_calls"] == 1
    assert outcomes["successful_calls"] == outcomes["failed_calls"] == outcomes["timeout_calls"] == 0


@pytest.mark.parametrize("stream,expected", [(None, "missing"), ("", "partial"), ('{"status":"error"}\n{', "partial")])
def test_missing_or_incomplete_attempt_ledger_does_not_claim_no_provider_calls(tmp_path, stream, expected):
    if stream is not None:
        (tmp_path / "llm_calls.jsonl").write_text(stream, encoding="utf-8")
    usage = reporting._usage(tmp_path, {"runtime": {"consumed": {"llm_calls": 3}}}, [])
    outcomes = usage["attempt_outcomes"]
    assert outcomes["ledger_status"] == expected
    assert "No provider calls were recorded" not in outcomes["summary"]
    assert "ledger is missing" in outcomes["summary"] if stream is None else "counts are partial" in outcomes["summary"]
    assert usage["total_tokens"] is usage["estimated_cost_usd"] is None


def test_attempt_error_labels_are_redacted_and_html_escaped(tmp_path):
    secret = "sk-abcdefghijklmnopqrstuvwxyz"  # pragma: allowlist secret
    attack = '<script>alert("x")</script> api_key=' + secret
    rows = [{"status": "error", "error_type": attack, "error": "private provider error",
             "prompt": "private prompt", "output": "private response"},
            {"status": "private status " + secret, "error_type": {"secret": secret}}]
    (tmp_path / "llm_calls.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    usage = reporting._usage(tmp_path, {"runtime": {"consumed": {"llm_calls": 2}}}, [])
    outcomes = usage["attempt_outcomes"]
    evidence = json.dumps(outcomes)
    assert "[REDACTED]" in evidence
    assert secret not in evidence and "private" not in evidence
    page = reporting.render_html({"usage": usage})
    assert "<script" not in page and "&lt;script&gt;" in page
    assert secret not in page and "private" not in page


def test_attempt_summary_groups_and_labels_are_bounded(tmp_path, monkeypatch):
    monkeypatch.setattr(reporting, "MAX_ATTEMPT_FAILURE_GROUPS", 2)
    monkeypatch.setattr(reporting, "MAX_ATTEMPT_LABEL_CHARS", 20)
    monkeypatch.setattr(reporting, "MAX_LLM_STREAM_RECORDS", 5)
    rows = [{"status": "error", "error_type": f"Error{i}" + "x" * 100} for i in range(6)]
    (tmp_path / "llm_calls.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    usage = reporting._usage(tmp_path, {"runtime": {"consumed": {"llm_calls": 6}}}, [])
    outcomes = usage["attempt_outcomes"]
    assert outcomes["ledger_status"] == "partial"
    assert outcomes["failed_calls"] == 5
    assert len(outcomes["failure_groups"]) == 2
    assert all(len(row["error_type"]) <= 20 for row in outcomes["failure_groups"])
    assert outcomes["other_failure_calls"] == 3


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


def test_timeout_is_unknown_correctness(tmp_path, monkeypatch):
    timeout_seconds = 0.3
    monkeypatch.setattr(reporting, "VERIFY_TIMEOUT_SECONDS", timeout_seconds)
    runner_ready = tmp_path / "runner-ready"
    worker_pids_path = tmp_path / "worker-pids"
    result_path = tmp_path / "result.json"
    candidate_path = tmp_path / "candidate.py"
    runner_path = tmp_path / "run_verify.py"
    candidate_path.write_text("while True: pass\n", encoding="utf-8")
    runner_path.write_text(
        "import json\n"
        "import sys\n"
        "from pathlib import Path\n"
        f"sys.path.insert(0, {str(Path(__file__).resolve().parents[1])!r})\n"
        "from libreevolve import alpha_report\n"
        f"worker_pids_path = Path({str(worker_pids_path)!r})\n"
        "original_popen = alpha_report.subprocess.Popen\n"
        "def recording_popen(*args, **kwargs):\n"
        "    process = original_popen(*args, **kwargs)\n"
        "    command = args[0] if args else kwargs.get('args')\n"
        "    if isinstance(command, (list, tuple)) and any(\n"
        "        str(part).endswith('alpha_verify_worker.py') for part in command\n"
        "    ):\n"
        "        with worker_pids_path.open('a', encoding='ascii') as stream:\n"
        "            stream.write(f'{process.pid}\\n')\n"
        "    return process\n"
        "alpha_report.subprocess.Popen = recording_popen\n"
        f"alpha_report.VERIFY_TIMEOUT_SECONDS = {timeout_seconds!r}\n"
        f"Path({str(runner_ready)!r}).write_text('ready\\n', encoding='ascii')\n"
        f"result = alpha_report.verify_candidate(Path({str(candidate_path)!r}).read_bytes())\n"
        f"Path({str(result_path)!r}).write_text(json.dumps(result), encoding='utf-8')\n",
        encoding="utf-8",
    )
    containment = (
        {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        if os.name == "nt"
        else {"start_new_session": True}
    )
    runner = subprocess.Popen(
        [sys.executable, str(runner_path)],
        cwd=Path(__file__).resolve().parents[1],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        **containment,
    )

    def terminate(pid):
        if os.name == "nt":
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                    timeout=5,
                )
            except subprocess.TimeoutExpired:
                pass
        else:
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    def recorded_worker_pids():
        try:
            return [int(line) for line in worker_pids_path.read_text().splitlines()]
        except (OSError, ValueError):
            return []

    try:
        # Wait for the runner itself before starting the watchdog. Worker
        # startup is included in the bounded post-ready budget below, but a
        # slow test interpreter cannot consume it before verification begins.
        startup_deadline = time.monotonic() + 20.0
        while not runner_ready.exists() and time.monotonic() < startup_deadline:
            if runner.poll() is not None:
                break
            time.sleep(0.01)
        assert runner_ready.exists(), "verification runner did not become ready"

        # Each split has the configured deadline, a finite worker-start grace,
        # process.wait fallback and reader/process-group cleanup. Two splits
        # run sequentially, followed by a small result-writing grace period.
        worker_start_grace_seconds = 5.0
        cleanup_grace_seconds = 8.0  # 2+2s waits, 2s reader joins, 2s group wait.
        post_start_timeout = 2 * (
            timeout_seconds + worker_start_grace_seconds + cleanup_grace_seconds
        ) + 2.0
        try:
            runner.wait(timeout=post_start_timeout)
        except subprocess.TimeoutExpired:
            pytest.fail(
                f"verification exceeded the post-start watchdog of {post_start_timeout:.1f}s"
            )
        assert result_path.exists(), "verification runner did not write a result"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        for split in ("training", "holdout"):
            assert result[split]["status"] == "timeout"
            assert result[split]["correctness"] is None
            assert result[split]["score"] is None
            assert result[split]["elapsed_seconds"] >= timeout_seconds
    finally:
        worker_pids = recorded_worker_pids()
        if runner.poll() is None:
            terminate(runner.pid)
            try:
                runner.wait(timeout=5)
            except subprocess.TimeoutExpired:
                runner.kill()
                runner.wait(timeout=5)
        # The runner owns workers in separate process groups, so clean up the
        # PIDs captured immediately after each worker Popen as a final guard
        # when the outer watchdog has to terminate the runner.
        for _ in range(10):
            latest_pids = recorded_worker_pids()
            if len(latest_pids) > len(worker_pids):
                worker_pids = latest_pids
            if runner.poll() is not None and latest_pids:
                break
            time.sleep(0.01)
        for pid in worker_pids:
            terminate(pid)


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


@pytest.mark.skipif(os.name == "nt", reason="POSIX process-group cleanup")
def test_vanished_process_group_during_cleanup_is_benign(monkeypatch):
    real_killpg = reporting.os.killpg

    def killpg(pgid, sig):
        if sig == signal.SIGKILL:
            raise OSError("group disappeared")
        if sig == 0:
            raise ProcessLookupError
        return real_killpg(pgid, sig)

    monkeypatch.setattr(reporting.os, "killpg", killpg)
    validator = (reporting.BUNDLED_PROBLEM / "validate.py").read_bytes()
    result = reporting._verify(baseline(), validator, "evaluate")
    assert result["status"] == "completed"
    assert result["correctness"] is True


@pytest.mark.skipif(os.name == "nt", reason="POSIX process-group cleanup")
def test_zombie_process_group_permission_error_is_checked_after_reap(monkeypatch):
    real_popen = reporting.subprocess.Popen
    waited = False

    class _TrackedProcess:
        def __init__(self, *args, **kwargs):
            self._process = real_popen(*args, **kwargs)

        def wait(self, *args, **kwargs):
            nonlocal waited
            result = self._process.wait(*args, **kwargs)
            waited = True
            return result

        def __getattr__(self, name):
            return getattr(self._process, name)

    monkeypatch.setattr(
        reporting.subprocess,
        "Popen",
        lambda *args, **kwargs: _TrackedProcess(*args, **kwargs),
    )

    def killpg(_pgid, sig):
        if sig == signal.SIGKILL:
            raise PermissionError(errno.EPERM, "operation not permitted")
        if sig == 0:
            if waited:
                raise ProcessLookupError
            return None
        raise AssertionError(f"unexpected signal: {sig}")

    monkeypatch.setattr(reporting.os, "killpg", killpg)
    validator = (reporting.BUNDLED_PROBLEM / "validate.py").read_bytes()
    result = reporting._verify(baseline(), validator, "evaluate")
    assert result["status"] == "completed"
    assert result["correctness"] is True


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
