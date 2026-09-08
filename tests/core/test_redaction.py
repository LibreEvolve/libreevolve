from libreevolve.core.redaction import (
    REDACTION_GRAMMAR_VERSION,
    redact_sensitive_text,
    redaction_policy_record,
)


def test_redacts_common_provider_key_shapes():
    values = [
        "sk-" + "proj-" + "abcdefghijklmnopqrstuvwxyz123456",
        "sk-" + "proj_" + "abcdefghijklmnopqrstuvwxyz123456",
        "ghp_" + "abcdefghijklmnopqrstuvwxyz123456",
        "github_pat_" + "abcdefghijklmnopqrstuvwxyz123456",
    ]

    redacted = redact_sensitive_text(" ".join(values))

    for value in values:
        assert value not in redacted
    assert redacted.count("[REDACTED]") == len(values)


def test_exports_named_redaction_grammar_policy():
    policy = redaction_policy_record()

    assert policy["schema"] == REDACTION_GRAMMAR_VERSION
    assert policy["engine"] == "ordered_regex_substitution"
    assert policy["placeholder"] == "[REDACTED]"
    assert [rule["id"] for rule in policy["rules"]] == [
        "private_key_block",
        "secret_assignment",
        "authorization_bearer",
        "url_basic_auth_password",
        "provider_token_prefix",
        "aws_access_key_id",
    ]
    assert "pattern" not in policy["rules"][0]


def test_redacts_extended_provider_token_prefixes():
    values = [
        "ghs_" + "abcdefghijklmnopqrstuvwxyz123456",
        "ghr_" + "abcdefghijklmnopqrstuvwxyz123456",
        "glpat-" + "abcdefghijklmnopqrstuvwxyz123456",
        "xoxp-" + "123456789012-abcdefghijklmnopqrstuv",
        "xapp-" + "123456789012-abcdefghijklmnopqrstuv",
    ]

    redacted = redact_sensitive_text(" ".join(values))

    for value in values:
        assert value not in redacted
    assert redacted.count("[REDACTED]") == len(values)


def test_redacts_aws_access_key_ids():
    values = [
        "AKIA" + "ABCDEFGHIJKLMNOP",
        "ASIA" + "ABCDEFGHIJKLMNOP",
    ]

    redacted = redact_sensitive_text(" ".join(values))

    for value in values:
        assert value not in redacted
    assert redacted == "[REDACTED] [REDACTED]"


def test_redacts_private_key_blocks():
    begin = "-----BEGIN " + "PRIVATE KEY-----"
    end = "-----END " + "PRIVATE KEY-----"
    key = (
        f"{begin}\n"
        "abc123secretmaterial\n"
        f"{end}"
    )

    redacted = redact_sensitive_text(f"before\n{key}\nafter")

    assert "abc123secretmaterial" not in redacted
    assert redacted == "before\n[REDACTED_PRIVATE_KEY]\nafter"


def test_redacts_url_basic_auth_passwords():
    text = "postgres://user:supersecret@example.test/db"

    redacted = redact_sensitive_text(text)

    assert "supersecret" not in redacted
    assert redacted == "postgres://user:[REDACTED]@example.test/db"


def test_redacts_provider_key_shapes_case_insensitively():
    values = [
        "SK-PROJ-UPPERSECRET1234567890",
        "GHP_UPPERSECRET1234567890",
        "GitHub_PAT_MixedSecret1234567890",
    ]

    redacted = redact_sensitive_text(" ".join(values))

    for value in values:
        assert value not in redacted
    assert redacted.count("[REDACTED]") == len(values)


def test_redacts_provider_key_shapes_after_filename_separators():
    value = "sk-" + "proj_evalpathsecret1234567890"

    redacted = redact_sensitive_text(f"validate_{value}.py")

    assert value not in redacted
    assert redacted == "validate_[REDACTED].py"


def test_redacts_authorization_bearer_headers():
    values = [
        "Authorization: Bearer hf_abcdefghijklmnopqrstuvwxyz1234567890",
        "authorization: Bearer xoxb-" "123456789012-abcdefghijklmnopqrstuv",
    ]

    redacted = redact_sensitive_text("\n".join(values))

    assert "hf_abcdefghijklmnopqrstuvwxyz1234567890" not in redacted
    assert "xoxb-" "123456789012-abcdefghijklmnopqrstuv" not in redacted
    assert "Authorization: Bearer [REDACTED]" in redacted
    assert "authorization: Bearer [REDACTED]" in redacted


def test_redacts_secret_assignments():
    text = "api_key='secret-value' token: abcdefghijklmnop"

    redacted = redact_sensitive_text(text)

    assert "secret-value" not in redacted
    assert "abcdefghijklmnop" not in redacted
    assert "api_key='[REDACTED]'" in redacted
    assert "token: [REDACTED]" in redacted


def test_redacts_full_quoted_secret_assignments_with_spaces():
    text = (
        'api_key="abc def ghi" '
        "password='hunter2 extra' "
        'token: "Bearer abc def"'
    )

    redacted = redact_sensitive_text(text)

    assert "abc def ghi" not in redacted
    assert "hunter2 extra" not in redacted
    assert "Bearer abc def" not in redacted
    assert 'api_key="[REDACTED]"' in redacted
    assert "password='[REDACTED]'" in redacted
    assert 'token: "[REDACTED]"' in redacted


def test_redacts_unclosed_quoted_secret_assignment_to_line_end():
    text = 'api_key="abc def ghi\nsafe text'

    redacted = redact_sensitive_text(text)

    assert "abc def ghi" not in redacted
    assert 'api_key="[REDACTED]' in redacted
    assert "safe text" in redacted


def test_redaction_false_positive_fixtures_remain_visible():
    text = (
        "token_count=42 "
        "secretariat=horse "
        "sketch-proj-demo "
        "AKIASHORT "
        "https://example.test/path:section"
    )

    assert redact_sensitive_text(text) == text
