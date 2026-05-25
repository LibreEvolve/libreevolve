from __future__ import annotations

import random
import re
import string
from dataclasses import dataclass, field

from libreevolve.population.program import Program
from libreevolve.problems.loader import Problem


PROMPT_TEMPLATE_FIELDS = {
    "task",
    "context",
    "parent_score",
    "parent_metrics",
    "parent_feedback",
    "parent_code",
    "inspirations",
    "extra_context",
    "recent_failures",
    "mutation_mode",
    "mutation_instructions",
}
REQUIRED_PROMPT_TEMPLATE_FIELDS = {"task"}
_MAX_FEEDBACK_TEXT_CHARS = 1200
_MAX_FEEDBACK_FIELD_CHARS = 400
_MAX_FEEDBACK_ITEMS = 3
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)(api[_-]?key|token|secret|password)(\s*[:=]\s*)(['\"]?)[^\s,'\"]+"
)
_SECRET_TOKEN = re.compile(r"\b(?:sk|sk-proj|ghp|gho|github_pat)_[A-Za-z0-9_\-]{12,}\b")


class PromptTemplateError(ValueError):
    """Raised when a configured or evolved prompt template is not renderable."""


@dataclass
class PromptSampler:
    """Configurable prompt sampler for AlphaEvolve-style context assembly."""

    variants: list[str] = field(default_factory=list)
    rng: random.Random = field(default_factory=random.Random)

    def build(
        self,
        parent: Program,
        inspirations: list[Program],
        problem: Problem,
        extra_context: str,
        recent_failures: list[dict | tuple[str, float]] | None = None,
        template: str | None = None,
        mutation_mode: str = "diff",
        capture_proposal_metadata: bool = False,
    ) -> str:
        variant = template or (self.rng.choice(self.variants) if self.variants else _DEFAULT_TEMPLATE)
        validate_prompt_template(variant)
        return variant.format(
            task=problem.task_description,
            context=_render_context(problem),
            parent_score=parent.fitness,
            parent_metrics=_render_metrics(parent),
            parent_feedback=_render_feedback(parent),
            parent_code=_render_program_files(parent),
            inspirations=_render_inspirations(inspirations),
            extra_context=extra_context,
            recent_failures=_render_failures(recent_failures),
            mutation_mode=mutation_mode,
            mutation_instructions=_render_mutation_instructions(
                mutation_mode,
                capture_proposal_metadata=capture_proposal_metadata,
            ),
        )


DEFAULT_TEMPLATE = """[SYSTEM]
You are an expert programmer evolving solutions for: {task}

[EXPLICIT CONTEXT]
{context}

[CURRENT PROGRAM - normalized fitness: {parent_score:.4f}]
Metrics: {parent_metrics}
Evaluation feedback:
{parent_feedback}
{parent_code}

[INSPIRATION PROGRAMS]
{inspirations}

[EXTRA CONTEXT]
{extra_context}
{recent_failures}
[TASK]
Propose a targeted improvement.
Mutation mode: {mutation_mode}
{mutation_instructions}
"""

_DEFAULT_TEMPLATE = DEFAULT_TEMPLATE


def validate_prompt_template(template: str) -> None:
    if not isinstance(template, str) or not template.strip():
        raise PromptTemplateError("prompt template must be a non-empty string")
    fields: set[str] = set()
    try:
        parsed = list(string.Formatter().parse(template))
    except ValueError as exc:
        raise PromptTemplateError(f"malformed prompt template: {exc}") from exc
    for _, field_name, _, _ in parsed:
        if field_name is None:
            continue
        if not field_name:
            raise PromptTemplateError("prompt template contains an empty placeholder")
        root = field_name.split(".", 1)[0].split("[", 1)[0]
        if root != field_name:
            raise PromptTemplateError(
                f"prompt template field {field_name!r} must be a simple placeholder"
            )
        if field_name not in PROMPT_TEMPLATE_FIELDS:
            raise PromptTemplateError(f"unknown prompt template field {field_name!r}")
        fields.add(field_name)
    missing = sorted(REQUIRED_PROMPT_TEMPLATE_FIELDS - fields)
    if missing:
        raise PromptTemplateError(f"missing required prompt template fields {missing}")


def _render_context(problem: Problem) -> str:
    if not problem.context_files:
        return "(none)"
    sources = {
        source.get("path"): source
        for source in getattr(problem, "context_sources", [])
        if isinstance(source, dict)
    }
    return "\n\n".join(
        f"{_render_context_header(name, sources.get(name))}\n{content}"
        for name, content in problem.context_files.items()
    )


def _render_context_header(name: str, source: dict | None) -> str:
    if not source:
        return f"--- CONTEXT SOURCE: {name} ---"
    sha = str(source.get("sha256", ""))[:12] or "unknown"
    span = f"{source.get('excerpt_start', 0)}:{source.get('excerpt_end', '?')}"
    status = source.get("extraction_status", "unknown")
    return (
        f"--- CONTEXT SOURCE: {name} "
        f"(sha256={sha}, chars={source.get('chars_original', '?')}, "
        f"excerpt={span}, status={status}) ---"
    )


def _render_mutation_instructions(
    mutation_mode: str, capture_proposal_metadata: bool = False
) -> str:
    proposal = ""
    if capture_proposal_metadata:
        proposal = """Before the patch, include up to three short metadata sections:
IDEA: one sentence naming the proposed improvement.
RATIONALE: one sentence explaining why it should help.
HYPOTHESIS: one sentence predicting the measured effect.
Then include the patch in the required format.
"""
    if mutation_mode == "full":
        return proposal + """Return full replacement code, not SEARCH/REPLACE diffs.
For multi-file candidates, wrap each changed file as:
<<<FILE path/to/file.py
complete replacement file content
>>>FILE
Use topology commands when needed:
<<<FILE DELETE path/to/obsolete.py
>>>FILE
<<<FILE MOVE old/path.py -> new/path.py
>>>FILE
<<<FILE PRIMARY path/to/main.py
>>>FILE
For a single-file candidate without evolve blocks, return only the complete
replacement primary file. If the file has one evolve block, return only the
replacement block body. If it has multiple evolve blocks, return one section per
changed block:
<<<BLOCK block_name
replacement block body
>>>BLOCK
Rules: No markdown fences. No extra explanation. No SEARCH/REPLACE blocks."""
    return proposal + """For multi-file candidates, wrap each file edit in
`<<<FILE path ... >>>FILE`; otherwise edit the current primary file.
Use either compact `<<<SEARCH` / `>>>REPLACE` fences or AlphaEvolve-style
`<<<<<<< SEARCH` / `>>>>>>> REPLACE` fences.
For workspace topology changes, use command file sections such as
`<<<FILE DELETE path/to/file.py ... >>>FILE`,
`<<<FILE MOVE old/path.py -> new/path.py ... >>>FILE`, or
`<<<FILE PRIMARY path/to/main.py ... >>>FILE`.
Rules: No comments inside the patch. No markdown fences. No extra explanation.
If metadata sections are requested, keep them outside the patch.

Example format (do NOT copy this, use actual code from the program above):
<<<SEARCH
def foo():
    return 1
===
def foo():
    return 2
>>>REPLACE"""


def _render_metrics(program: Program) -> str:
    return ", ".join(f"{k}={v}" for k, v in program.metrics.items()) or "(none)"


def _render_proposal(program: Program) -> str:
    proposal = program.metadata.get("proposal") if isinstance(program.metadata, dict) else None
    if not isinstance(proposal, dict):
        return ""
    lines = []
    for field_name in ("idea", "rationale", "hypothesis"):
        value = _short(proposal.get(field_name), max_chars=240)
        if value:
            lines.append(f"- {field_name}: {value}")
    return "\n".join(lines)


def _render_program_files(program: Program) -> str:
    workspace = program.workspace()
    if len(workspace.files) == 1:
        return f"```python\n{workspace.code}\n```"
    rendered = []
    for path, content in sorted(workspace.files.items()):
        fence = "python" if path.endswith(".py") else ""
        rendered.append(f"--- FILE {path} ---\n```{fence}\n{content}\n```")
    return "\n\n".join(rendered)


def _render_feedback(program: Program) -> str:
    evaluation = program.evaluation or {}
    stages = evaluation.get("stages", [])
    metadata = evaluation.get("metadata") if isinstance(evaluation.get("metadata"), dict) else {}
    sections: list[str] = []
    proposal = _render_proposal(program)
    if proposal:
        sections.append("[proposal]\n" + proposal)
    if stages:
        lines = []
        for stage in stages[-_MAX_FEEDBACK_ITEMS:]:
            if not isinstance(stage, dict):
                continue
            status = "passed" if stage.get("passed") else "failed"
            error = stage.get("error")
            suffix = f", error={_short(error)}" if error else ""
            lines.append(f"- {stage.get('name')}: {status}, score={stage.get('score')}{suffix}")
            stage_io = _render_io_summary(stage)
            if stage_io:
                lines.append(stage_io)
        if lines:
            sections.append("[stage summary]\n" + "\n".join(lines))
    top_io = _render_io_summary(evaluation)
    if top_io:
        sections.append("[execution output]\n" + top_io)
    attempts = _render_attempts(metadata.get("attempts"))
    if attempts:
        sections.append("[sample/retry diagnostics]\n" + attempts)
    artifacts = _render_artifacts(metadata.get("artifacts"))
    if artifacts:
        sections.append("[validator artifacts]\n" + artifacts)
    feedback = _render_llm_feedback(metadata.get("llm_feedback"))
    if feedback:
        sections.append("[llm grader feedback]\n" + feedback)
    if not sections:
        return "(none)"
    return _truncate_text("\n".join(sections), _MAX_FEEDBACK_TEXT_CHARS)


def _render_io_summary(record: dict) -> str:
    lines = []
    stdout = _short(record.get("stdout"))
    stderr = _short(record.get("stderr"))
    if stdout:
        lines.append(f"  stdout: {stdout}")
    if stderr:
        lines.append(f"  stderr: {stderr}")
    error = _short(record.get("error"))
    if error and not lines:
        lines.append(f"  error: {error}")
    return "\n".join(lines)


def _render_attempts(attempts: object) -> str:
    if not isinstance(attempts, list) or not attempts:
        return ""
    lines = []
    for attempt in attempts[-_MAX_FEEDBACK_ITEMS:]:
        if not isinstance(attempt, dict):
            continue
        status = "passed" if attempt.get("passed") else "failed"
        stage_record = attempt.get("stage")
        stage = stage_record.get("name") if isinstance(stage_record, dict) else attempt.get("stage_name")
        sample = (
            stage_record.get("sample_index")
            if isinstance(stage_record, dict)
            else attempt.get("sample_index")
        )
        attempt_index = attempt.get("attempt")
        detail = [
            f"stage={stage}" if stage is not None else "",
            f"sample={sample}" if sample is not None else "",
            f"attempt={attempt_index}" if attempt_index is not None else "",
        ]
        prefix = ", ".join(item for item in detail if item)
        prefix = f" ({prefix})" if prefix else ""
        error = _short(attempt.get("error"))
        suffix = f", error={error}" if error else ""
        lines.append(f"- {status}{prefix}, fitness={attempt.get('fitness')}{suffix}")
    return "\n".join(lines)


def _render_artifacts(artifacts: object) -> str:
    if not isinstance(artifacts, dict):
        return ""
    files = artifacts.get("files")
    if not isinstance(files, list) or not files:
        return ""
    lines = []
    for artifact in files[:_MAX_FEEDBACK_ITEMS]:
        if not isinstance(artifact, dict):
            continue
        source = artifact.get("source_path") or artifact.get("relative_path") or artifact.get("path")
        stored = artifact.get("artifact_path") or artifact.get("stored_path")
        sha = str(artifact.get("sha256", ""))[:12]
        redacted = artifact.get("redacted")
        parts = [f"path={source}"]
        if stored:
            parts.append(f"stored={stored}")
        if sha:
            parts.append(f"sha256={sha}")
        if redacted is not None:
            parts.append(f"redacted={redacted}")
        lines.append("- " + ", ".join(parts))
    skipped = artifacts.get("skipped") or artifacts.get("skipped_files")
    if skipped:
        lines.append(f"- skipped_files={skipped}")
    return "\n".join(lines)


def _render_llm_feedback(records: object) -> str:
    if not isinstance(records, list) or not records:
        return ""
    lines = []
    for record in records[-_MAX_FEEDBACK_ITEMS:]:
        if not isinstance(record, dict):
            continue
        name = record.get("name") or record.get("metric") or "grader"
        score = record.get("score")
        discarded = record.get("discard")
        error = _short(record.get("error"))
        feedback = _short(record.get("feedback") or record.get("raw_response"))
        parts = [f"name={name}"]
        if score is not None:
            parts.append(f"score={score}")
        if discarded is not None:
            parts.append(f"discard={discarded}")
        if error:
            parts.append(f"error={error}")
        if feedback:
            parts.append(f"feedback={feedback}")
        lines.append("- " + ", ".join(parts))
    return "\n".join(lines)


def _short(value: object, max_chars: int = _MAX_FEEDBACK_FIELD_CHARS) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r\n", "\n").strip()
    if not text:
        return ""
    text = _redact_sensitive_text(text)
    return _truncate_text(text, max_chars).replace("\n", "\\n")


def _truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    notice = f"...[truncated {len(text) - max_chars} chars]"
    keep = max(0, max_chars - len(notice))
    return text[:keep] + notice


def _redact_sensitive_text(text: str) -> str:
    text = _SECRET_ASSIGNMENT.sub(r"\1\2\3[REDACTED]", text)
    return _SECRET_TOKEN.sub("[REDACTED]", text)


def _render_inspirations(inspirations: list[Program]) -> str:
    if not inspirations:
        return "(none)"
    rendered = []
    for i, inspiration in enumerate(inspirations):
        proposal = _render_proposal(inspiration)
        proposal_text = f"Proposal:\n{proposal}\n" if proposal else ""
        rendered.append(
            f"\n--- Inspiration {i + 1} "
            f"(fitness {inspiration.fitness:.4f}; metrics: {_render_metrics(inspiration)}) ---\n"
            f"{proposal_text}{_render_program_files(inspiration)}\n"
        )
    return "".join(rendered)


def _render_failures(recent_failures: list[dict | tuple[str, float]] | None) -> str:
    if not recent_failures:
        return ""
    lines = "\n".join(_render_failure_line(failure) for failure in recent_failures)
    return f"\n[RECENTLY FAILED - do NOT repeat these]\n{lines}\n"


def _render_failure_line(failure: dict | tuple[str, float]) -> str:
    if not isinstance(failure, dict):
        code, score = failure
        return f"  Score {score:.2f}: {code}"
    score = failure.get("score")
    score_text = f"{float(score):.2f}" if isinstance(score, (int, float)) else "unknown"
    error = failure.get("error") or failure.get("diff_error") or "invalid"
    diff_error = failure.get("diff_error")
    changed = failure.get("changed_files") or []
    changed_text = ",".join(changed) if changed else "(none)"
    repeat = failure.get("repetition_count", 1)
    mutation = str(failure.get("mutation_text", "")).replace("\n", " ")[:160]
    suffix = f"; diff_error={diff_error}" if diff_error else ""
    return (
        f"  Score {score_text}: error={error}{suffix}; "
        f"changed_files={changed_text}; repeats={repeat}; mutation={mutation}"
    )
