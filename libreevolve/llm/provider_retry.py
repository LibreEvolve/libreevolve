from __future__ import annotations

from copy import deepcopy

DEFAULT_PROVIDER_MAX_RETRIES = 2
MAX_PROVIDER_MAX_RETRIES = 10
PROVIDER_RETRY_POLICY = "bounded_provider_internal_retries"


def validate_provider_max_retries(
    value: object,
    *,
    field: str = "provider_max_retries",
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be a non-negative integer")
    if value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    if value > MAX_PROVIDER_MAX_RETRIES:
        raise ValueError(f"{field} must be <= {MAX_PROVIDER_MAX_RETRIES}")
    return value


def provider_retry_metadata(
    *,
    max_retries: int,
    attempts: int,
    failures: list[dict],
) -> dict:
    return {
        "policy": PROVIDER_RETRY_POLICY,
        "max_retries": max_retries,
        "attempts": attempts,
        "failed_attempts": len(failures),
        "failures": deepcopy(failures),
    }


def provider_retry_failure(attempt: int, exc: BaseException) -> dict:
    return {
        "attempt": attempt,
        "error_type": exc.__class__.__name__,
    }


def with_provider_retry_metadata(
    metadata: dict,
    *,
    max_retries: int,
    attempts: int,
    failures: list[dict],
) -> dict:
    record = dict(metadata)
    record["adapter_retry"] = provider_retry_metadata(
        max_retries=max_retries,
        attempts=attempts,
        failures=failures,
    )
    return record
