"""Synthetic-only public-record admission tests."""

from copy import deepcopy

import pytest

from libreevolve.alpha_share_record import admit_record, approve_record, payload_sha256, source_url


def record():
    return dict(schema_version="libreevolve.public_result.v1", public_result_id="synthetic-example",
                product_status="engineering preview", evidence_class="synthetic_fixture",
                run_status="aborted", selected_source="unknown", candidate_retention="unknown", baseline=None, candidate=None, checks=[],
                observed_activity=dict(calls=None, elapsed_seconds=None),
                usage=dict(tokens=None, cost_usd=None, status="unknown"),
                public_provenance=dict(source_commit=None, candidate_sha256=None, validator_sha256=None),
                approved_source_url=None, limitations=["Synthetic fixture, not a measured experiment."])


def test_allowlisted_copy_and_private_receipt():
    data = record()
    before = deepcopy(data)
    public, receipt = approve_record(data, approved_sha256=payload_sha256(data), approved_by="test-reviewer")
    assert public == before == data
    assert public is not data
    assert "approved_by" not in public
    assert receipt["approved_by"] == "test-reviewer"
    assert public["usage"]["cost_usd"] is None
    assert public["run_status"] == "aborted"


def test_payload_change_invalidates_approval():
    data = record()
    digest = payload_sha256(data)
    data["run_status"] = "completed"
    with pytest.raises(ValueError, match="exact public payload"):
        approve_record(data, approved_sha256=digest, approved_by="reviewer")


def test_source_has_separate_approval():
    data = record()
    data["approved_source_url"] = "https://github.com/LibreEvolve/libreevolve/blob/main/README.md"
    with pytest.raises(ValueError, match="separate"):
        approve_record(data, approved_sha256=payload_sha256(data), approved_by="reviewer")
    assert approve_record(data, approved_sha256=payload_sha256(data), approved_by="reviewer", approve_source_link=True)


@pytest.mark.parametrize("url", ["javascript:alert(1)", "http://example.com", "file:///tmp/code",
    "https://localhost/a", "https://127.0.0.1/a", "https://[::1]/a", "https://host.internal/a",
    "https://user:secret@example.com/a",  # pragma: allowlist secret -- synthetic rejected credential URL
    "https://example.com/a?token=secret", "https://example.com/../a",
    "https://example.com/%2e%2e/a", "https://example.com\\@private.local/a", "https://example.com:bad/a"])
def test_unsafe_urls(url):
    with pytest.raises(ValueError):
        source_url(url)


@pytest.mark.parametrize("host", [
    "127.1", "127.0.1", "0177.0.0.1", "0x7f.0x0.0x0.0x1",
    "0X7F.0X1", "127.0x", "10.1", "192.168.1", "169.254.1",
    "0.0", "0300.0250.1", "8.8", "example.09", "example.0x",
])
def test_numeric_host_aliases_cannot_enter_public_records(host):
    data = record()
    data["approved_source_url"] = f"https://{host}/a"
    with pytest.raises(ValueError, match="invalid public link"):
        admit_record(data)


@pytest.mark.parametrize("host", ["github.com", "123.example.com", "0x7f.example.com"])
def test_numeric_subdomains_of_ordinary_domains_remain_supported(host):
    url = f"https://{host}/a"
    assert source_url(url) == url


@pytest.mark.parametrize("path,value", [
    (("usage", "tokens"), True), (("usage", "cost_usd"), float("nan")),
    (("usage", "cost_usd"), float("inf")), (("observed_activity", "calls"), -1),
    (("observed_activity", "elapsed_seconds"), 10**500),
    (("usage", "status"), "complete"), (("run_status",), []),
    (("checks",), [{"name": "test", "split": "training", "status": "passed", "code": "secret"}]),
    (("limitations",), ["x" * 241]), (("public_result_id",), "../private"),
    (("public_provenance", "source_commit"), "wrong"),
])
def test_malformed_record(path, value):
    data = record()
    target = data
    for component in path[:-1]:
        target = target[component]
    target[path[-1]] = value
    with pytest.raises(ValueError):
        admit_record(data)


def test_private_fields_fail_closed():
    for field in ("source", "prompt", "run_dir", "auth_name", "outcome"):
        with pytest.raises(ValueError):
            admit_record(dict(record(), **{field: "must not leak"}))


def test_hash_is_order_independent_but_content_bound():
    data = record()
    assert payload_sha256(data) == payload_sha256(dict(reversed(list(data.items()))))
    data["evidence_class"] = "observed_local_checks"
    assert payload_sha256(data) != payload_sha256(record())


@pytest.mark.parametrize("bad", ["\ud800", "\udfff", "\u2028", "\u2029", "\u202e", "\u2066"])
def test_unicode_encoding_and_display_controls_rejected(bad):
    data = record()
    data["limitations"] = ["Text" + bad]
    with pytest.raises(ValueError):
        admit_record(data)
    data = record()
    data["checks"] = [{"name": "Check" + bad, "split": "training", "status": "passed"}]
    with pytest.raises(ValueError):
        admit_record(data)
    with pytest.raises(ValueError):
        source_url("https://example.com/" + bad)
