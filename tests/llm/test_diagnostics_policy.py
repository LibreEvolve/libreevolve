import copy
import hashlib
import json

from libreevolve.llm.diagnostics_policy import (
    LLM_PROVIDER_DIAGNOSTICS_POLICY,
    validate_llm_provider_diagnostics_summary,
)
from libreevolve.llm.ensemble import (
    LLMEnsemble,
    LLM_PROVIDER_DIAGNOSTICS_SCHEMA,
)


class MinimalBackend:
    name = "diagnostics"
    api_mode = "chat"

    def generate(self, prompt, **kwargs):
        return "answer"


def _summary():
    ens = LLMEnsemble([MinimalBackend()])
    ens.generate("prompt text", role="mutation")
    return ens.provider_diagnostics_summary


def _hash_backends(summary):
    payload = json.dumps(summary["backends"], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def test_llm_provider_diagnostics_summary_validates_ensemble_snapshot():
    summary = _summary()

    validation = validate_llm_provider_diagnostics_summary(summary)

    assert validation.ok is True
    assert validation.snapshot_ready is True
    assert validation.live_pricing_ready is False
    assert validation.raw_payload_replay_ready is False
    assert validation.backend_count == 1
    assert validation.issues == []
    assert summary["schema"] == LLM_PROVIDER_DIAGNOSTICS_SCHEMA
    assert summary["policy"] == LLM_PROVIDER_DIAGNOSTICS_POLICY


def test_llm_provider_diagnostics_summary_loads_json_file(tmp_path):
    path = tmp_path / "provider-diagnostics.json"
    path.write_text(json.dumps(_summary()), encoding="utf-8")

    validation = validate_llm_provider_diagnostics_summary(path)

    assert validation.ok is True
    assert validation.backend_count == 1


def test_llm_provider_diagnostics_summary_rejects_core_shape_errors():
    summary = _summary()
    summary["policy"] = "full_raw_provider_payload_replay"
    summary["status"] = "complete_replay"
    summary["source"] = "provider_native_payloads"
    summary["call_history_retention"] = []
    summary["limitations"] = ["provider_native_payloads_retained"]
    summary["provider_native_payloads"] = [{"opaque": True}]

    validation = validate_llm_provider_diagnostics_summary(summary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.snapshot_ready is False
    assert validation.raw_payload_replay_ready is False
    assert "invalid_policy" in codes
    assert "invalid_status" in codes
    assert "invalid_source" in codes
    assert "invalid_call_history_retention" in codes
    assert "missing_required_limitations" in codes
    assert "invalid_provider_native_payloads" in codes


def test_llm_provider_diagnostics_summary_rejects_live_pricing_overclaim():
    summary = _summary()
    summary["totals"]["live_pricing_record_count"] = 1
    summary["backends"][0]["live_pricing_record_count"] = 1
    summary["records_sha256"] = _hash_backends(summary)

    validation = validate_llm_provider_diagnostics_summary(summary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.live_pricing_ready is False
    assert "live_pricing_not_supported" in codes


def test_llm_provider_diagnostics_summary_rejects_configured_pricing_drift():
    summary = _summary()
    summary["totals"]["configured_pricing_estimate_count"] = 1
    summary["backends"][0]["configured_pricing_estimate_count"] = 1
    summary["records_sha256"] = _hash_backends(summary)

    validation = validate_llm_provider_diagnostics_summary(summary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.live_pricing_ready is False
    assert "configured_pricing_count_exceeds_cost_estimates" in codes


def test_llm_provider_diagnostics_summary_rejects_cost_reason_drift():
    summary = _summary()
    summary["backends"][0]["cost_status_reasons"] = {
        "missing_configured_backend_cost_rate": 0,
    }
    summary["records_sha256"] = _hash_backends(summary)

    validation = validate_llm_provider_diagnostics_summary(summary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "not_estimated_reason_count_mismatch" in codes


def test_llm_provider_diagnostics_summary_rejects_count_and_hash_mismatches():
    summary = copy.deepcopy(_summary())
    summary["backend_count"] = 2
    summary["totals"]["call_count"] = 99
    summary["totals"]["cost_estimate_count"] = -1
    summary["backends"][0]["calls"] = -1
    summary["backends"][0]["successes"] = 3
    summary["backends"][0]["failures"] = 3
    summary["backends"][0]["diagnostic_keys"] = {"": -1}

    validation = validate_llm_provider_diagnostics_summary(summary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "backend_count_mismatch" in codes
    assert "call_count_mismatch" in codes
    assert "invalid_totals_cost_estimate_count" in codes
    assert "invalid_backend_calls" in codes
    assert "backend_outcome_count_mismatch" in codes
    assert "invalid_backend_diagnostic_keys_key" in codes
    assert "invalid_backend_diagnostic_keys_count" in codes
    assert "records_sha256_mismatch" in codes


def test_llm_provider_diagnostics_summary_rejects_total_backend_aggregate_drift():
    summary = copy.deepcopy(_summary())
    summary["totals"]["usage_record_count"] += 1
    summary["totals"]["provider_response_retention_modes"] = {
        "unexpected": 1,
    }

    validation = validate_llm_provider_diagnostics_summary(summary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "usage_record_count_mismatch" in codes
    assert "provider_response_retention_modes_mismatch" in codes
