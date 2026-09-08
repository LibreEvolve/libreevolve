"""Explicit trusted local verification -> frozen public proposal (not approval).

Unlike rendering, this operation executes selected candidate Python in the
existing timed verification workers with host access. No provider is called.
Neither a valid export nor this proposal grants permission to publish it.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from libreevolve.alpha_share_io import checked_path
from libreevolve.alpha_share_record import admit_record


def _read_code(path):
    path = checked_path(path, must_exist=True)
    if not path.is_file():
        raise ValueError("Candidate must be a regular file")
    with path.open("rb") as stream:
        raw = stream.read(1_000_001)
    if len(raw) > 1_000_000:
        raise ValueError("Candidate exceeds source limit")
    raw.decode("utf-8")
    return raw


def _corpora():
    completed = subprocess.run(
        [sys.executable, "-I", str(Path(__file__).with_name("alpha_share_corpus_worker.py"))],
        capture_output=True, timeout=10, check=True,
    )
    if len(completed.stdout) > 65_536:
        raise ValueError("Unexpected corpus identity output size")
    return json.loads(completed.stdout)


def prepare_run(run_dir: str | Path, *, public_result_id: str,
                source: str = "auto", split: str = "training") -> tuple[dict, dict]:
    """Return an unapproved public proposal and PRIVATE preparation evidence.

    Resolve the source explicitly before fresh checks. History conflicts are
    not repaired or hidden. Selection is frozen before any held-out checking.
    Public IDs are supplied intentionally, never derived from private paths.
    """
    from libreevolve.alpha_report import BUNDLED_PROBLEM, _usage, verify_candidate
    from libreevolve.core.run_inspection import inspect_run, read_manifest

    if source not in ("auto", "workspace", "history") or split not in ("training", "holdout"):
        raise ValueError("Choose an explicit supported source and split")
    if type(public_result_id) is not str or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", public_result_id) is None:
        raise ValueError("Choose a bounded public result ID before executing candidate checks")
    root = checked_path(run_dir, must_exist=True)
    inspection = inspect_run(root)
    if inspection.workspace is None:
        raise ValueError("No recoverable candidate; do not invent a result")
    primary, workspace = inspection.workspace
    if set(workspace) != {primary} or primary != "seed.py":
        raise ValueError("Sharing supports the public single-file seed.py preview")
    history_code = workspace[primary].encode("utf-8")
    chosen = history_code
    source_kind = "history"
    exported = root / "best_workspace" / primary
    if source == "workspace" or (source == "auto" and (exported.exists() or exported.is_symlink())):
        chosen = _read_code(exported)
        if source == "auto" and chosen.replace(b"\r\n", b"\n") != history_code.replace(b"\r\n", b"\n"):
            raise ValueError("Workspace differs from history; choose source workspace or history explicitly")
        source_kind = "workspace"
    candidate_hash = hashlib.sha256(chosen).hexdigest()
    matches_history = chosen.replace(b"\r\n", b"\n") == history_code.replace(b"\r\n", b"\n")
    baseline_code = _read_code(BUNDLED_PROBLEM / "initial_programs/seed.py")
    identity = _corpora()
    candidate = verify_candidate(chosen)
    baseline = verify_candidate(baseline_code)

    def metric(verification, expected_hash):
        checked = verification[split]
        if (verification.get("code_sha256") != expected_hash
                or checked.get("code_sha256") != expected_hash
                or verification.get("validator_sha256") != identity["validator_sha256"]
                or checked.get("validator_sha256") != identity["validator_sha256"]):
            raise ValueError("Fresh verification hash does not match frozen source/corpus identity")
        values = checked.get("metrics") or {}
        corpus = identity["corpora"][split]
        valid = checked.get("correctness") if checked.get("status") == "completed" else None
        if valid is True and values.get("case_count") != corpus["case_count"]:
            raise ValueError("Fresh checks do not cover the named corpus")
        return dict(corpus, split=split, valid=valid,
                    total_bins=values.get("total_bins"), quality=checked.get("score"))

    before = metric(baseline, hashlib.sha256(baseline_code).hexdigest())
    after = metric(candidate, candidate_hash)
    manifest = read_manifest(root / "manifest.json")
    runtime = manifest.get("runtime") or {}
    usage = _usage(root, manifest, [])
    status = runtime.get("status")
    usage_state = "complete" if usage.get("total_tokens") is not None and usage.get("estimated_cost_usd") is not None else "partial" if usage.get("total_tokens") is not None or usage.get("estimated_cost_usd") is not None else "unknown"
    proposal = {
        "schema_version": "libreevolve.public_result.v1", "public_result_id": public_result_id,
        "product_status": "engineering preview", "evidence_class": "observed_local_checks",
        "run_status": status if status in ("completed", "aborted", "incomplete") else "unknown",
        "selected_source": source_kind,
        "candidate_retention": "retained" if matches_history and inspection.selection == "archive-retained valid" else "not_established",
        "baseline": before, "candidate": after,
        "checks": [{"name": f"Bundled bin-packing {name} correctness", "split": split,
                    "status": "passed" if data["valid"] is True else "failed" if data["valid"] is False else "incomplete"}
                   for name, data in (("baseline", before), ("candidate", after))],
        "observed_activity": {"calls": usage.get("calls"), "elapsed_seconds": (runtime.get("consumed") or {}).get("runtime_seconds")},
        "usage": {"tokens": usage.get("total_tokens"), "cost_usd": usage.get("estimated_cost_usd"), "status": usage_state},
        "public_provenance": {"source_commit": None, "candidate_sha256": candidate_hash, "validator_sha256": identity["validator_sha256"]},
        "approved_source_url": None,
        "limitations": ["Fresh bundled finite checks only; not universal correctness or optimality.",
                        "Candidate execution used host-access local subprocesses, not a security sandbox.",
                        "The bundled held-out split is public reporting data, not a secret benchmark.",
                        "This proposal is not publication approval. Review all fields and hashes."],
    }
    private = {"source_kind": source_kind, "matches_history": matches_history,
               "candidate_sha256": candidate_hash, "selected_before_heldout": True,
               "scope": "private preparation evidence; not public authentication"}
    return admit_record(proposal), private
