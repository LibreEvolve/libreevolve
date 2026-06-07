from __future__ import annotations

import re

OPENAI_REASONING_EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh"}
OPENAI_API_MODES = {"auto", "chat_completions", "responses"}

_GPT_5_VERSION_RE = re.compile(r"^gpt-5(?:[.-](\d+))?(?:[-.:/].*)?$")


def validate_openai_reasoning_effort_for_model(
    reasoning_effort: object,
    *,
    model: object | None = None,
    field: str = "reasoning_effort",
) -> str | None:
    """Validate OpenAI reasoning effort with documented model-specific limits."""
    if reasoning_effort is None:
        return None
    if not isinstance(reasoning_effort, str) or reasoning_effort not in OPENAI_REASONING_EFFORTS:
        raise ValueError(f"{field} must be one of {sorted(OPENAI_REASONING_EFFORTS)}")

    if model is None or not isinstance(model, str):
        return reasoning_effort

    normalized = model.lower()
    if _is_gpt_5_pro(normalized) and reasoning_effort != "high":
        raise ValueError(f"{field} for gpt-5-pro models must be high")

    if _is_gpt_5_1_family(normalized):
        allowed = {"none", "low", "medium", "high"}
        if _supports_xhigh_reasoning(normalized):
            allowed.add("xhigh")
        if reasoning_effort not in allowed:
            raise ValueError(
                f"{field} for gpt-5.1 models must be one of {sorted(allowed)}"
            )

    if _is_before_gpt_5_1_reasoning_model(normalized) and reasoning_effort == "none":
        raise ValueError(f"{field}=none requires gpt-5.1 or newer")

    if reasoning_effort == "xhigh" and not _supports_xhigh_reasoning(normalized):
        raise ValueError(f"{field}=xhigh is supported only for eligible OpenAI models")

    return reasoning_effort


def validate_openai_api_mode(
    api_mode: object,
    *,
    reasoning_effort: object | None = None,
    field: str = "api_mode",
) -> str:
    if api_mode is None:
        return "auto"
    if not isinstance(api_mode, str) or api_mode not in OPENAI_API_MODES:
        raise ValueError(f"{field} must be one of {sorted(OPENAI_API_MODES)}")
    if api_mode == "chat_completions" and reasoning_effort is not None:
        raise ValueError(f"{field}=chat_completions cannot be used with reasoning_effort")
    return api_mode


def resolve_openai_api_mode(
    api_mode: object,
    *,
    reasoning_effort: object | None = None,
    field: str = "api_mode",
) -> str:
    validated = validate_openai_api_mode(
        api_mode,
        reasoning_effort=reasoning_effort,
        field=field,
    )
    if validated == "auto":
        return "responses" if reasoning_effort is not None else "chat_completions"
    return validated


def _is_gpt_5_pro(model: str) -> bool:
    return model == "gpt-5-pro" or model.startswith("gpt-5-pro-")


def _is_gpt_5_1_family(model: str) -> bool:
    return model == "gpt-5.1" or model.startswith("gpt-5.1-")


def _is_before_gpt_5_1_reasoning_model(model: str) -> bool:
    if model.startswith(("gpt-4", "o1", "o3", "o4")):
        return True
    match = _GPT_5_VERSION_RE.match(model)
    if match is None:
        return False
    minor = match.group(1)
    if minor is None:
        return True
    return int(minor) < 1


def _supports_xhigh_reasoning(model: str) -> bool:
    if "gpt-5.1-codex-max" in model:
        return True
    match = _GPT_5_VERSION_RE.match(model)
    if match is None:
        return False
    minor = match.group(1)
    return minor is not None and int(minor) > 1
