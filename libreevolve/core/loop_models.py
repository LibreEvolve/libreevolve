"""Immutable value records used by the core evolution loop."""
from __future__ import annotations

from dataclasses import dataclass

from libreevolve.core.candidate import CandidateWorkspace
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
    parent_selection_metadata: dict
    inspiration_selection_metadata: dict
    prompt_program: PromptProgram
    mutation_mode: str
    mutation_mode_selection: dict
    mutation_llm_call: dict | None
    proposal_llm_calls: list[dict]
