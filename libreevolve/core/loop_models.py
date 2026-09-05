"""Immutable value records used by the core evolution loop."""
from __future__ import annotations

from concurrent.futures import Future
from dataclasses import dataclass

from libreevolve.core.async_evaluator import AsyncEvaluationOutcome
from libreevolve.core.async_sampler import AsyncLLMSamplerOutcome
from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.evaluator import EvaluationResult
from libreevolve.core.meta_prompt import PromptProgram
from libreevolve.population.program import Program


@dataclass(frozen=True)
class _PreparedCandidate:
    submission_order: int
    loop_generation_index: int
    proposal_index: int
    proposals_per_generation: int
    candidate_generation: int
    parent: Program
    child_workspace: CandidateWorkspace
    diff_error: object | None
    candidate_id: str
    retained_prompt: dict
    diff: str
    prompt_diagnostics: dict
    proposal_metadata: dict
    explanatory_preamble: dict
    backend_idx: int
    critique_metadata: dict | None
    parent_selection_metadata: dict
    inspiration_selection_metadata: dict
    plugin_context: list[dict]
    prompt_program: PromptProgram
    mutation_mode: str
    mutation_mode_selection: dict
    mutation_llm_call: dict | None
    proposal_llm_calls: list[dict]
    async_llm_sampler: dict | None = None


@dataclass(frozen=True)
class _PreparedMutationRequest:
    submission_order: int
    loop_generation_index: int
    proposal_index: int
    proposals_per_generation: int
    candidate_generation: int
    parent: Program
    parent_selection_metadata: dict
    prompt_program: PromptProgram
    mutation_mode: str
    mutation_mode_selection: dict
    proposal_metadata_enabled: bool
    prompt: str
    prompt_diagnostics: dict
    prompt_context_text: str
    inspiration_selection_metadata: dict
    plugin_context: list[dict]


@dataclass(frozen=True)
class _PendingAsyncMutation:
    request: _PreparedMutationRequest
    future: Future[AsyncLLMSamplerOutcome]


@dataclass(frozen=True)
class _PendingCandidateEvaluation:
    prepared: _PreparedCandidate
    source: str
    future: Future[AsyncEvaluationOutcome] | None = None
    immediate_result: EvaluationResult | None = None
    cache_key_sha256: str | None = None
    source_submission_order: int | None = None
