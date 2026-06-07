from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import re


REDACTION_GRAMMAR_VERSION = "libreevolve.redaction.v2"


@dataclass(frozen=True)
class RedactionRule:
    id: str
    description: str
    pattern: re.Pattern[str]
    replacement: str | Callable[[re.Match[str]], str]


_PRIVATE_KEY_BLOCK = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
    re.DOTALL,
)
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)(api[_-]?key|token|secret|password)(\s*[:=]\s*)"
    r"((?:'[^'\r\n]*'?)|(?:\"[^\"\r\n]*\"?)|(?:[^\s,'\"]+))"
)
_AUTHORIZATION_BEARER = re.compile(r"(?i)\b(authorization\s*:\s*bearer\s+)[^\s,;]+")
_URL_BASIC_AUTH = re.compile(
    r"(?i)\b([a-z][a-z0-9+.-]{1,20}://[^/\s:@]+:)[^@\s/]+(@)"
)
_PROVIDER_TOKEN = re.compile(
    r"(?<![A-Za-z0-9])"
    r"(?:sk(?:-proj)?|ghp|gho|ghu|ghs|ghr|github_pat|glpat|hf|xox[abpcrs]?|xapp)"
    r"[_-][A-Za-z0-9_\-]{12,}\b",
    re.IGNORECASE,
)
_AWS_ACCESS_KEY_ID = re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")


def _redact_assignment(match: re.Match[str]) -> str:
    key = match.group(1)
    separator = match.group(2)
    value = match.group(3)
    if value.startswith(("'", '"')):
        quote = value[0]
        closing = quote if len(value) > 1 and value.endswith(quote) else ""
        return f"{key}{separator}{quote}[REDACTED]{closing}"
    return f"{key}{separator}[REDACTED]"


REDACTION_RULES = (
    RedactionRule(
        id="private_key_block",
        description="PEM private-key blocks",
        pattern=_PRIVATE_KEY_BLOCK,
        replacement="[REDACTED_PRIVATE_KEY]",
    ),
    RedactionRule(
        id="secret_assignment",
        description="credential assignment values",
        pattern=_SECRET_ASSIGNMENT,
        replacement=_redact_assignment,
    ),
    RedactionRule(
        id="authorization_bearer",
        description="Authorization: Bearer header values",
        pattern=_AUTHORIZATION_BEARER,
        replacement=r"\1[REDACTED]",
    ),
    RedactionRule(
        id="url_basic_auth_password",
        description="password segment in URL userinfo",
        pattern=_URL_BASIC_AUTH,
        replacement=r"\1[REDACTED]\2",
    ),
    RedactionRule(
        id="provider_token_prefix",
        description=(
            "standalone OpenAI, GitHub, GitLab, Hugging Face, and Slack-like "
            "provider token prefixes"
        ),
        pattern=_PROVIDER_TOKEN,
        replacement="[REDACTED]",
    ),
    RedactionRule(
        id="aws_access_key_id",
        description="AWS access-key id prefixes AKIA and ASIA",
        pattern=_AWS_ACCESS_KEY_ID,
        replacement="[REDACTED]",
    ),
)


def redact_sensitive_text(text: str) -> str:
    for rule in REDACTION_RULES:
        text = rule.pattern.sub(rule.replacement, text)
    return text


def redaction_policy_record() -> dict:
    return {
        "schema": REDACTION_GRAMMAR_VERSION,
        "engine": "ordered_regex_substitution",
        "placeholder": "[REDACTED]",
        "rules": [
            {
                "id": rule.id,
                "description": rule.description,
            }
            for rule in REDACTION_RULES
        ],
    }
