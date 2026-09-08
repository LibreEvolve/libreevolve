"""Offline alpha evidence reports; candidate code executes only in workers.

Verification uses the installed bundled bin-packing validator, never a path
supplied by a run. SHA evidence identifies the bytes sampled for this report;
it is not attestation or a hostile-code security boundary.
"""

from __future__ import annotations

import difflib
import errno
import hashlib
import html
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time

from libreevolve.core.jsonl import strict_json_dumps, strict_json_loads_object
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.core.run_inspection import inspect_run
from libreevolve.core.evaluator import (
    _assign_windows_kill_job, _close_windows_job, _terminate_process_tree,
    _validator_env,
)

VERIFY_TIMEOUT_SECONDS = 10.0
MAX_OUTPUT_BYTES = 65536
MAX_SOURCE_BYTES = 1_000_000
MAX_MANIFEST_BYTES = 16_000_000
MAX_LLM_STREAM_RECORDS = 100_000
MAX_ATTEMPT_FAILURE_GROUPS = 8
MAX_ATTEMPT_LABEL_CHARS = 80
BUNDLED_PROBLEM = Path(__file__).parent / "problems" / "examples" / "bin_packing"


def _bytes(path: Path, limit: int = MAX_SOURCE_BYTES) -> bytes:
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"{path.name}: artifact exceeds {limit} bytes")
    return data


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _object(value) -> dict:
    return value if isinstance(value, dict) else {}


def _number(value):
    try:
        return value if type(value) in (int, float) and math.isfinite(value) and value >= 0 else None
    except OverflowError:
        return None


def _darwin_process_exit_observer(process: subprocess.Popen):
    """Register a non-reaping exit observer for a Darwin worker."""
    if sys.platform != "darwin":
        return None
    observer = None
    try:
        import select

        observer = select.kqueue()
        event = select.kevent(
            process.pid,
            filter=select.KQ_FILTER_PROC,
            flags=select.KQ_EV_ADD,
            fflags=select.KQ_NOTE_EXIT,
        )
        observer.control([event], 0, 0)
        return observer
    except (AttributeError, OSError) as exc:
        if observer is not None:
            try:
                observer.close()
            except OSError:
                pass
        raise OSError("Darwin verification requires a kqueue process observer") from exc


def _process_exited(process: subprocess.Popen, observer=None) -> bool:
    """Observe POSIX worker exit without reaping its process group leader.

    ``Popen.poll()`` reaps an exited child.  If the worker spawned a
    descendant that inherited its session, reaping the leader first can make
    a later ``killpg(worker_pid, ...)`` fail on some POSIX implementations,
    leaving that descendant running.  ``waitid(..., WNOWAIT)`` observes the
    exit while retaining the zombie leader until the cleanup path has killed
    the whole group. Darwin uses a ``kqueue`` process event because its Python
    builds do not expose ``waitid(..., WNOWAIT)``. Windows has no equivalent
    here and keeps the normal ``Popen.poll`` path.
    """
    if os.name == "nt":
        return process.poll() is not None
    if sys.platform == "darwin":
        if observer is None:
            raise OSError("Darwin verification requires a kqueue process observer")
        return bool(observer.control(None, 1, 0))
    try:
        observed = os.waitid(
            os.P_PID,
            process.pid,
            os.WEXITED | os.WNOHANG | os.WNOWAIT,
        )
    except (AttributeError, ChildProcessError) as exc:
        # Reaping with poll() here would recreate the process-group race. The
        # supported Python 3.11+ POSIX platforms provide waitid; unknown
        # platforms fail closed rather than execute without cleanup proof.
        raise OSError("POSIX verification requires waitid with WNOWAIT") from exc
    except OSError as exc:
        raise OSError("POSIX verification could not observe worker exit safely") from exc
    return observed is not None and observed.si_pid == process.pid


def _wait_for_process_group_exit(pgid: int, timeout: float = 2.0) -> None:
    """Wait briefly for a killed POSIX worker group to disappear."""
    deadline = time.monotonic() + timeout
    while True:
        try:
            os.killpg(pgid, 0)
        except (ProcessLookupError, PermissionError):
            return
        if time.monotonic() >= deadline:
            return
        time.sleep(0.01)


def _process_group_exists(pgid: int) -> bool:
    """Return whether a process group is still observable by this process."""
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except OSError as exc:
        return exc.errno != errno.ESRCH
    return True


def _verify(code: bytes, validator: bytes, entrypoint: str) -> dict:
    evidence = {"code_sha256": _sha(code), "validator_sha256": _sha(validator),
                "entrypoint": entrypoint, "status": "error", "correctness": None,
                "score": None}
    started = time.monotonic()
    try:
        request = json.dumps(dict(evidence, code=code.decode("utf-8"),
                                  validator=validator.decode("utf-8"))).encode("utf-8")
        # File stdin avoids blocking writes when a worker cannot start. Pipe
        # readers retain at most the cap and kill on overflow; no communicate()
        # accumulation or unbounded output file is used.
        with tempfile.TemporaryDirectory(prefix="libreevolve-alpha-") as temp:
            input_path = Path(temp) / "request.json"
            input_path.write_bytes(request)
            with input_path.open("rb") as stdin:
                release = Path(temp) / "worker-release"
                env = _validator_env([])
                env["LIBREEVOLVE_ALPHA_RELEASE"] = str(release)
                containment = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
                               if os.name == "nt" else {"start_new_session": True})
                process = subprocess.Popen(
                    [sys.executable, "-I", str(Path(__file__).with_name("alpha_verify_worker.py"))],
                    stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    cwd=temp, shell=False, env=env, **containment,
                )
                job = None
                exit_observer = None
                buffers = [bytearray(), bytearray()]
                overflow = threading.Event()

                def drain(stream, target):
                    while chunk := stream.read(4096):
                        remaining = MAX_OUTPUT_BYTES - len(target)
                        target.extend(chunk[:remaining])
                        if len(chunk) > remaining:
                            overflow.set()
                            break
                    stream.close()

                readers = [threading.Thread(target=drain, args=(stream, target), daemon=True)
                           for stream, target in zip((process.stdout, process.stderr), buffers)]
                # Darwin can report EPERM while the exited group leader is
                # still an unreaped zombie. Decide whether cleanup failed
                # only after wait() and the group-disappearance check below.
                posix_group_cleanup_error = None
                try:
                    exit_observer = _darwin_process_exit_observer(process)
                    job = _assign_windows_kill_job(process)
                    # Fail closed before the worker reads or executes code if
                    # Windows cannot guarantee kill-on-close containment.
                    if os.name == "nt" and not (job and job.get("assigned")):
                        raise OSError("Could not assign verification worker to Windows kill job")
                    for reader in readers:
                        reader.start()
                    release.touch()
                    deadline = started + VERIFY_TIMEOUT_SECONDS
                    while not _process_exited(process, exit_observer) and not overflow.is_set():
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            evidence["status"] = "timeout"
                            break
                        overflow.wait(min(0.02, remaining))
                finally:
                    # Always reap descendants, including after successful root
                    # exit. The evaluator helper skips exited roots on POSIX,
                    # so explicitly kill their still-existing session group.
                    if os.name == "nt":
                        if job is not None:
                            closed = _close_windows_job(job)
                            if not closed.get("closed"):
                                if job.get("assigned"):
                                    evidence["status"] = "cleanup_failed"
                                    evidence["cleanup_error"] = "Could not close Windows verification job"
                                _terminate_process_tree(process)
                        else:
                            _terminate_process_tree(process)
                    else:
                        # Kill the session group even when the worker has
                        # already exited.  Its process group leader remains
                        # unreaped until below, allowing descendants to be
                        # terminated as well.
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        except OSError as exc:
                            posix_group_cleanup_error = exc
                            try:
                                process.kill()
                            except (OSError, ProcessLookupError):
                                pass
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        _terminate_process_tree(process)
                        process.wait(timeout=2)
                    for reader in readers:
                        if reader.ident is not None:
                            reader.join(timeout=1)
                    if os.name != "nt":
                        _wait_for_process_group_exit(process.pid)
                        if (
                            posix_group_cleanup_error is not None
                            and _process_group_exists(process.pid)
                        ):
                            evidence["status"] = "cleanup_failed"
                            evidence["cleanup_error"] = str(posix_group_cleanup_error)[:500]
                    if exit_observer is not None:
                        exit_observer.close()
                    for stream, reader in zip((process.stdout, process.stderr), readers):
                        if reader.ident is None:
                            stream.close()
                if evidence["status"] in {"timeout", "cleanup_failed"}:
                    return evidence
                if overflow.is_set() or any(reader.is_alive() for reader in readers):
                    evidence["status"] = "output_limit"
                    return evidence
                if process.returncode:
                    evidence.update(status="worker_failed", returncode=process.returncode)
                    return evidence
                result = strict_json_loads_object(bytes(buffers[0]).decode("utf-8"), source="worker")
                strict_json_dumps(result)
                if any(result.get(key) != evidence[key] for key in ("code_sha256", "validator_sha256")):
                    raise ValueError("Worker evidence mismatch")
                evidence.update(result)
    except (OSError, ValueError, UnicodeError) as exc:
        evidence["error"] = str(exc)[:1000]
    finally:
        evidence["elapsed_seconds"] = time.monotonic() - started
    return evidence


def _attempt_outcomes(rows: list[dict], ledger_status: str) -> dict:
    """Summarize observed calls, never provider messages, prompts or outputs."""
    result = {"source": "llm_calls.jsonl", "ledger_status": ledger_status,
              "successful_calls": 0, "failed_calls": 0, "timeout_calls": 0,
              "unknown_status_calls": 0, "failure_groups": [],
              "other_failure_calls": 0,
              "note": "Counts describe observed provider calls, including retries; timeouts are a subset of failures. "
                      "A successful provider response does not establish a valid, retained or improving candidate."}
    groups = {}
    categories = {"timeout", "rate_limit", "transport", "provider_response",
                  "provider_server_error", "provider_client_error", "unknown"}
    for row in rows:
        if row.get("status") == "ok":
            result["successful_calls"] += 1
        elif row.get("status") == "error":
            result["failed_calls"] += 1
            category = row.get("provider_failure_category")
            if not isinstance(category, str) or category not in categories:
                category = "unknown"
            error_type = row.get("error_type")
            # Older ledgers may lack the category but retain a timeout class.
            if category == "timeout" or error_type in ("ProviderCallTimeoutError", "TimeoutError", "TimeoutExpired", "APITimeoutError"):
                result["timeout_calls"] += 1
                category = "timeout"
            error_type = (" ".join(redact_sensitive_text(error_type).split())[:MAX_ATTEMPT_LABEL_CHARS]
                          if isinstance(error_type, str) else "Unknown / unavailable")
            key = (category, error_type)
            if key in groups or len(groups) < MAX_ATTEMPT_FAILURE_GROUPS:
                groups[key] = groups.get(key, 0) + 1
            else:
                result["other_failure_calls"] += 1
        else:
            result["unknown_status_calls"] += 1
    result["failure_groups"] = [{"category": category, "error_type": error_type, "calls": count}
                                for (category, error_type), count in groups.items()]
    result["status"] = "complete" if ledger_status == "complete" and not result["unknown_status_calls"] else "partial" if rows else "unknown"
    prefix = {"missing": "Provider call ledger is missing; attempt outcomes are unknown. ",
              "partial": "Provider call ledger is incomplete or cannot be reconciled with the recorded call count; observed counts are partial. ",
              "complete": ""}[ledger_status]
    result["summary"] = prefix + (
        f"Observed provider attempts: {result['successful_calls']} successful, "
        f"{result['failed_calls']} failed ({result['timeout_calls']} timeouts), "
        f"{result['unknown_status_calls']} with unknown status."
        if rows else ("No provider calls were recorded." if ledger_status == "complete"
                      else "No provider call outcomes could be established.")
    )
    if rows and result["failed_calls"] == len(rows):
        result["summary"] += " Every observed provider call failed; no successful response was recorded."
    return result


def _usage(run_dir: Path, manifest: dict, issues: list) -> dict:
    runtime = _object(manifest.get("runtime"))
    consumed = _object(runtime.get("consumed"))
    result = {"source": "runtime.consumed", "total_tokens": None,
              "input_tokens": None, "output_tokens": None, "estimated_cost_usd": None,
              "recorded_tokens": _number(consumed.get("llm_tokens")),
              "recorded_cost_microusd": _number(consumed.get("llm_cost_microusd")),
              "calls": _number(consumed.get("llm_calls")), "models": [],
              "configured_models": [], "status": "unknown",
              "note": "Cost is an estimate from configured rates, not provider billing."}
    backends = _object(manifest.get("config")).get("backends", [])
    if isinstance(backends, list):
        result["configured_models"] = [b["model"] for b in backends
                                       if isinstance(b, dict) and isinstance(b.get("model"), str)]
        if backends and all(isinstance(b, dict) and b.get("type") == "codex" for b in backends):
            result["note"] = (
                "Codex CLI reports token usage. Subscription charges and remaining quota "
                "are not reported; a missing dollar estimate does not mean zero cost. "
                "Call and runtime limits bound local work; an in-flight call can exceed "
                "a token threshold."
            )
    path = run_dir / "llm_calls.jsonl"
    rows = []
    complete = True
    if path.exists():
        try:
            with path.open("rb") as stream:
                stream_records = 0
                while line := stream.readline(MAX_SOURCE_BYTES + 1):
                    stream_records += 1
                    if len(line) > MAX_SOURCE_BYTES or stream_records > MAX_LLM_STREAM_RECORDS:
                        raise ValueError("LLM call stream exceeds report limit")
                    if line.strip():
                        row = strict_json_loads_object(line.decode("utf-8"), source="llm_calls.jsonl")
                        strict_json_dumps(row)
                        record_type = row.get("record_type", "call")
                        if record_type == "reward":
                            continue
                        if record_type != "call":
                            raise ValueError("LLM call stream has an invalid record_type")
                        rows.append(row)
        except (OSError, ValueError, UnicodeError) as exc:
            complete = False
            issues.append({"artifact": "llm_calls.jsonl", "status": "corrupt", "detail": str(exc)[:500]})
    else:
        complete = False
    result["models"] = sorted({model for row in rows
                                for model in (_object(row.get("backend_metadata")).get("model", row.get("model")),)
                                if isinstance(model, str)})
    result["observed_backend_names"] = sorted({row["backend_name"] for row in rows
                                               if isinstance(row.get("backend_name"), str)})
    result["observed_call_records"] = len(rows)
    expected = result["calls"]
    complete = complete and expected is not None and expected == len(rows)
    result["attempt_outcomes"] = _attempt_outcomes(
        rows, "complete" if complete else "partial" if path.exists() else "missing")
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        values = [_number(_object(row.get("usage")).get(key)) for row in rows]
        if complete and all(value is not None for value in values):
            result[key] = sum(values)
    costs = [_number(_object(row.get("cost_estimate")).get("cost_microusd")) for row in rows]
    if complete and all(value is not None for value in costs):
        result["estimated_cost_usd"] = sum(costs) / 1_000_000
    result["status"] = "complete" if complete and result["total_tokens"] is not None and result["estimated_cost_usd"] is not None else "partial" if rows or consumed else "unknown"
    return result


def verify_candidate(code: str | bytes) -> dict:
    """Verify frozen primary text with the bundled validator in two workers.

    Returns code, code_sha256, validator_sha256, training and holdout. Each
    split contains status, correctness (bool or null), score (number or null),
    hashes, entrypoint and elapsed_seconds. Invalid packing is a completed
    evaluation with correctness=False; a timeout has correctness=None.
    """
    raw = code.encode("utf-8") if isinstance(code, str) else code
    if not isinstance(raw, bytes) or len(raw) > MAX_SOURCE_BYTES:
        raise ValueError("Candidate must be UTF-8 text of at most 1000000 bytes")
    validator = _bytes(BUNDLED_PROBLEM / "validate.py")
    return {"code": raw.decode("utf-8"), "code_sha256": _sha(raw),
            "validator_sha256": _sha(validator),
            "training": _verify(raw, validator, "evaluate"),
            "holdout": _verify(raw, validator, "evaluate_holdout")}


def build_report(run_dir: Path) -> dict:
    """Reevaluate the exported primary and bundled baseline; never writes the run."""
    run_dir = Path(run_dir)
    issues = []
    manifest = {}
    manifest_status = "missing"
    try:
        manifest = strict_json_loads_object(
            _bytes(run_dir / "manifest.json", MAX_MANIFEST_BYTES).decode("utf-8"), source="manifest.json")
        strict_json_dumps(manifest)
        manifest_status = "present"
    except (OSError, ValueError, UnicodeError) as exc:
        manifest_status = "missing" if not (run_dir / "manifest.json").exists() else "corrupt"
        manifest = {}
        issues.append({"artifact": "manifest.json", "status": manifest_status, "detail": str(exc)[:500]})
    runtime = _object(manifest.get("runtime"))
    if "runtime" in manifest and not isinstance(manifest["runtime"], dict):
        issues.append({"artifact": "manifest.json", "status": "invalid_runtime", "detail": "runtime must be an object"})
    consumed = _object(runtime.get("consumed"))
    report = {"schema": "libreevolve.alpha_report.v1", "run_dir": str(run_dir),
              "status": "unverified", "manifest_status": manifest_status,
              "runtime": {"status": runtime.get("status"), "stop_reason": runtime.get("stop_reason"),
                          "elapsed_seconds": _number(consumed.get("runtime_seconds")),
                          "evaluation_counts": {key: _number(consumed.get(key)) for key in
                                                ("evaluations", "seed_evaluations", "candidate_evaluations", "evaluator_timeouts")},
                          "abort": runtime.get("abort")},
              "usage": _usage(run_dir, manifest, issues), "issues": issues,
              "baseline": None, "best": None, "export_status": "absent",
              "search_outcome": "No exported result was independently verified.",
              "recoverable_history": None,
              "score_delta": {"training": None, "holdout": None},
              "diff": None, "scope": "Bundled bin_packing training and heldout reevaluation; local subprocess, not a security sandbox. Holdout is reporting-only, not search fitness."}
    try:
        validator = _bytes(BUNDLED_PROBLEM / "validate.py")
        baseline = _bytes(BUNDLED_PROBLEM / "initial_programs" / "seed.py")
    except (OSError, ValueError) as exc:
        issues.append({"artifact": "bundled_fixture", "status": "unavailable", "detail": str(exc)[:500]})
        return report
    report["validator_sha256"] = _sha(validator)

    def evaluate(raw, path):
        return {"path": path, "code_sha256": _sha(raw), "code": raw.decode("utf-8"),
                "training": _verify(raw, validator, "evaluate"),
                "holdout": _verify(raw, validator, "evaluate_holdout")}

    try:
        report["baseline"] = evaluate(baseline, "bundled/initial_programs/seed.py")
    except UnicodeError as exc:
        issues.append({"artifact": "bundled_fixture", "status": "corrupt", "detail": str(exc)[:500]})
        return report
    try:
        primary = "seed.py"
        best_record = _object(manifest.get("best_program"))
        seed_sources = _object(manifest.get("problem")).get("seed_sources")
        if isinstance(seed_sources, list):
            declared = [source.get("primary_file") for source in seed_sources if isinstance(source, dict)]
            if declared and any(item != "seed.py" for item in declared):
                raise ValueError("Manifest seed primaries do not match the alpha seed.py contract")
        if "primary_file" in best_record:
            primary = best_record["primary_file"]
        if not isinstance(primary, str) or primary != "seed.py":
            raise ValueError("Alpha bin_packing verification requires primary seed.py")
        workspace = run_dir / "best_workspace"
        candidate = workspace / primary
        candidate.resolve().relative_to(run_dir.resolve())
        raw = _bytes(candidate)
        report["export_status"] = "present"
        report["best"] = evaluate(raw, "best_workspace/" + primary)
        report["search_outcome"] = ("Selected export is unchanged from the bundled seed."
                                    if raw == baseline else "Selected export differs from the bundled seed; see independent score changes below.")
        report["best"]["primary_evidence"] = "manifest.best_program.primary_file" if best_record.get("primary_file") else "alpha seed.py convention; manifest has no primary declaration"
        exported = _object(_object(_object(runtime.get("best_artifact_export")).get("paths")).get("best.py"))
        expected_sha = exported.get("sha256")
        report["best"]["manifest_primary_sha256"] = expected_sha
        report["best"]["manifest_primary_match"] = _sha(raw) == expected_sha if isinstance(expected_sha, str) else None
        report["best"]["manifest_primary_match_kind"] = "exact_bytes" if expected_sha == _sha(raw) else None
        if isinstance(expected_sha, str) and expected_sha != _sha(raw):
            try:
                compatibility = run_dir / "best.py"
                compatibility.resolve().relative_to(run_dir.resolve())
                compatibility_raw = _bytes(compatibility)
                report["best"]["compatibility_export_sha256"] = _sha(compatibility_raw)
                if (_sha(compatibility_raw) == expected_sha
                        and compatibility_raw.replace(b"\r\n", b"\n") == raw.replace(b"\r\n", b"\n")):
                    report["best"]["manifest_primary_match"] = True
                    report["best"]["manifest_primary_match_kind"] = "manifest_verified_best.py_with_CRLF_normalized"
            except (OSError, ValueError):
                pass
        if report["best"]["manifest_primary_match"] is False:
            issues.append({"artifact": "best_workspace/seed.py", "status": "hash_mismatch",
                           "detail": "Export differs from manifest best.py primary hash; metrics describe current bytes only."})
        report["diff"] = "".join(difflib.unified_diff(baseline.decode("utf-8").splitlines(True),
                                  raw.decode("utf-8").splitlines(True), fromfile="baseline/seed.py", tofile="best_workspace/seed.py"))
        passed = True
        for split in ("training", "holdout"):
            before, after = report["baseline"][split], report["best"][split]
            valid = all(item["status"] == "completed" and item["correctness"] is True for item in (before, after))
            passed = passed and valid
            if valid:
                report["score_delta"][split] = after["score"] - before["score"]
        report["status"] = "verified" if passed else "verification_failed"
        if passed and report["best"]["manifest_primary_match"] is False:
            report["status"] = "verified_modified_export"
    except (OSError, ValueError, UnicodeError) as exc:
        issues.append({"artifact": "best_workspace/seed.py", "status": "unavailable", "detail": str(exc)[:500]})
        report["status"] = "no_result"
        if (run_dir / "history.jsonl").exists():
            try:
                _bytes(run_dir / "history.jsonl", MAX_MANIFEST_BYTES)
                recovered = inspect_run(run_dir)
                report["recoverable_history"] = {
                    "status": "available_for_explicit_export", "selection": recovered.selection,
                    "line_number": recovered.best_line_number,
                    "primary_file": recovered.workspace[0] if recovered.workspace else None,
                    "note": "History selection only; no exported result was verified."}
            except (OSError, ValueError, UnicodeError) as history_exc:
                report["recoverable_history"] = {"status": "unavailable", "detail": str(history_exc)[:500]}
    return report


def render_html(report: dict) -> str:
    """Render escaped semantic HTML with embedded CSS and no active content."""
    def escape(value):
        return html.escape("Unknown / unavailable" if value is None else str(value), quote=True)

    def block(title, value):
        text = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) if not isinstance(value, str) else value
        return f"<section><h2>{escape(title)}</h2><pre>{escape(text)}</pre></section>"

    body = f"<header><p class=eyebrow>Local evidence report · Engineering preview</p><h1>LibreEvolve alpha result</h1><p>{escape(report.get('status'))}</p><p>{escape(report.get('scope'))}</p><p>This local report can contain source code and sensitive run details. It is not a public share export.</p></header>"
    attempts = _object(_object(report.get("usage")).get("attempt_outcomes"))
    body += '<section><h2>Search and provider attempt outcomes</h2>'
    body += ''.join(f"<p>{escape(value)}</p>" for value in
                    (report.get("search_outcome"), attempts.get("summary"), attempts.get("note")))
    candidate_evaluations = _object(_object(report.get("runtime")).get("evaluation_counts")).get("candidate_evaluations")
    if candidate_evaluations == 0:
        body += '<p>The run recorded no generated candidate evaluations.</p>'
    elif candidate_evaluations is not None:
        body += f'<p>Generated candidate evaluations recorded by the run: {escape(candidate_evaluations)}. These counts do not establish validity or archive retention.</p>'
    body += '</section>'
    body += block("Run status", report.get("runtime")) + block("Usage and estimated cost", report.get("usage"))
    body += '<section><h2>Independent reevaluation</h2><div class="table-scroll" role="region" aria-label="Independent reevaluation table" tabindex="0"><table><caption>Higher quality is better; correctness is required</caption><thead><tr><th scope="col">Program / split</th><th scope="col">Status</th><th scope="col">Correctness</th><th scope="col">Score</th></tr></thead><tbody>'
    for name in ("baseline", "best"):
        program = _object(report.get(name))
        for split in ("training", "holdout"):
            row = _object(program.get(split))
            body += f'<tr><th scope="row">{name} / {split}</th>' + ''.join(f'<td>{escape(row.get(key))}</td>' for key in ("status", "correctness", "score")) + '</tr>'
    body += '</tbody></table></div></section>'
    body += block("Score change (best minus baseline)", report.get("score_delta"))
    body += block("Artifact issues", report.get("issues")) + block("Source diff", report.get("diff"))
    for name in ("baseline", "best"):
        body += block(name.capitalize() + " code", _object(report.get(name)).get("code"))
    body += block("Machine-readable evidence", report)
    styles = """
    :root{color-scheme:light dark;--paper:#fafbf9;--ink:#18251f;
      --muted:#4e6056;--line:#b5c1b8;--surface:#edf1ec;--accent:#176b49}
    *{box-sizing:border-box}
    body{font:1rem/1.6 system-ui,sans-serif;margin:0;color:var(--ink);background:var(--paper)}
    main{max-width:72rem;margin:auto;padding:2.5rem clamp(1rem,4vw,3rem);overflow-wrap:anywhere}
    header{border-top:.25rem solid var(--accent);padding-top:1.5rem;margin-bottom:3rem}
    .eyebrow{color:var(--muted);font-size:.875rem}
    h1{font-size:clamp(1.8rem,4vw,3rem);line-height:1.15;letter-spacing:-.035em}
    h2{font-size:1.25rem;line-height:1.35;margin:0 0 1rem}
    p{max-width:75ch}
    section{margin:2.5rem 0;padding-top:1.5rem;border-top:1px solid var(--line)}
    pre{font:.875rem/1.65 ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere;
      background:var(--surface);padding:1rem;margin:0;tab-size:4}
    .table-scroll{overflow-x:auto;max-width:100%}
    .table-scroll:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
    table{border-collapse:collapse;width:100%}
    caption{text-align:left;color:var(--muted);padding:0 0 1rem}
    th,td{text-align:left;border-bottom:1px solid var(--line);padding:.75rem;white-space:nowrap}
    th{font-weight:600}thead{background:var(--surface)}
    @media(prefers-color-scheme:dark){:root{--paper:#111b16;--ink:#e5eee7;
      --muted:#b0c1b5;--line:#506358;--surface:#1c2a21;--accent:#81d4a7}}
    @media print{:root{color-scheme:light;--paper:#fff;--ink:#000;--muted:#333;
      --line:#888;--surface:#f4f4f4;--accent:#000}main{padding:0;max-width:none}
      .table-scroll{overflow:visible}th,td{white-space:normal}}
    """
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'"><title>LibreEvolve alpha result</title><style>' + styles + '</style></head><body><main>' + body + '</main></body></html>'
