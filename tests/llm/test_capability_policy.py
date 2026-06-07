import hashlib
import json

from libreevolve.core.database import _provider_capability_lookup_policy
from libreevolve.llm.capability_policy import (
    PROVIDER_CAPABILITY_LOOKUP_POLICY_SCHEMA,
    validate_provider_capability_lookup_policy,
)


def _policy():
    return _provider_capability_lookup_policy(
        [
            {"type": "openai", "model": "gpt-5-mini"},
            {"type": "anthropic", "model": "claude-sonnet-4"},
        ]
    )


def _hash_records(policy: dict) -> str:
    payload = json.dumps(policy["records"], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def test_provider_capability_lookup_policy_validates_static_boundary():
    policy = _policy()

    validation = validate_provider_capability_lookup_policy(policy)

    assert validation.ok is True
    assert validation.static_lookup_ready is True
    assert validation.live_lookup_ready is False
    assert validation.record_count == 2
    assert validation.issues == []
    assert policy["schema"] == PROVIDER_CAPABILITY_LOOKUP_POLICY_SCHEMA
    assert policy["record_count"] == 2
    assert policy["records_sha256"] == _hash_records(policy)


def test_provider_capability_lookup_policy_loads_json_file(tmp_path):
    path = tmp_path / "provider-capability.json"
    path.write_text(json.dumps(_policy()), encoding="utf-8")

    validation = validate_provider_capability_lookup_policy(path)

    assert validation.ok is True
    assert validation.record_count == 2


def test_provider_capability_lookup_policy_rejects_live_lookup_overclaims():
    policy = _policy()
    policy["live_lookup"] = "supported"
    policy["network_calls_before_run"] = "model_registry_query"
    policy["provider_model_registry"] = "queried"
    policy["provider_service_api_version"] = "queried"
    policy["provider_account_availability"] = "checked"
    policy["records"][0]["live_model_registry_lookup"] = True
    policy["records"][0]["provider_service_api_version_lookup"] = True
    policy["records"][0]["provider_account_availability_check"] = True

    validation = validate_provider_capability_lookup_policy(policy)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.live_lookup_ready is False
    assert "invalid_live_lookup" in codes
    assert "invalid_network_calls_before_run" in codes
    assert "invalid_provider_model_registry" in codes
    assert "invalid_provider_service_api_version" in codes
    assert "invalid_provider_account_availability" in codes
    assert "invalid_live_model_registry_lookup" in codes
    assert "invalid_provider_service_api_version_lookup" in codes
    assert "invalid_provider_account_availability_check" in codes


def test_provider_capability_lookup_policy_rejects_bad_records():
    policy = _policy()
    policy["record_count"] = 3
    policy["records_sha256"] = "0" * 64
    policy["records"][0]["backend_index"] = policy["records"][1]["backend_index"]
    policy["records"][0]["local_validation"] = []
    policy["records"][0].pop("api_mode_policy_ref")
    policy["records"][1]["model"] = ""
    policy["records"][1]["offline_compatible"] = False

    validation = validate_provider_capability_lookup_policy(policy)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "record_count_mismatch" in codes
    assert "records_sha256_mismatch" in codes
    assert "duplicate_backend_index" in codes
    assert "missing_required_local_validation" in codes
    assert "missing_openai_local_validation" in codes
    assert "invalid_openai_api_mode_policy_ref" in codes
    assert "invalid_model" in codes
    assert "invalid_offline_compatible" in codes


def test_provider_capability_lookup_policy_rejects_missing_records():
    policy = _policy()
    policy["records"] = []

    validation = validate_provider_capability_lookup_policy(policy)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.record_count == 0
    assert "invalid_records" in codes
