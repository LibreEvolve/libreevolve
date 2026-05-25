from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

from libreevolve.core.jsonl import append_strict_jsonl
from libreevolve.core.prompt import (
    DEFAULT_TEMPLATE,
    PromptTemplateError,
    validate_prompt_template,
)


@dataclass
class PromptProgram:
    template: str
    id: str = field(default_factory=lambda: uuid4().hex)
    parent_id: str | None = None
    generation: int = 0
    uses: int = 0
    reward_sum: float = 0.0
    metadata: dict = field(default_factory=dict)

    @property
    def mean_reward(self) -> float:
        return self.reward_sum / self.uses if self.uses else 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "template": self.template,
            "parent_id": self.parent_id,
            "generation": self.generation,
            "uses": self.uses,
            "reward_sum": self.reward_sum,
            "mean_reward": self.mean_reward,
            "metadata": self.metadata,
        }


class PromptDatabase:
    """Small evolutionary database for prompt templates.

    This is intentionally local and deterministic. It gives prompt instructions
    identity, lineage, selection, scoring, and append-only logs so future
    mutation strategies can evolve prompts without changing the rest of the
    loop.
    """

    def __init__(self, log_dir: str | Path, templates: list[str] | None = None):
        self._programs: dict[str, PromptProgram] = {}
        self._log_path = Path(log_dir) / "prompt_history.jsonl"
        self._quarantine_path = Path(log_dir) / "prompt_history_invalid.jsonl"
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        seed_templates = templates or [DEFAULT_TEMPLATE]
        for template in seed_templates:
            self.add(PromptProgram(template=template, metadata={"source": "seed"}))

    def add(self, program: PromptProgram) -> PromptProgram:
        validate_prompt_template(program.template)
        self._write("add", program)
        self._programs[program.id] = program
        return program

    def select(self) -> PromptProgram:
        untried = [p for p in self._programs.values() if p.uses == 0]
        if untried:
            return sorted(untried, key=lambda p: p.id)[0]
        total = sum(p.uses for p in self._programs.values())
        return max(
            self._programs.values(),
            key=lambda p: p.mean_reward + math.sqrt(math.log(total + 1) / p.uses),
        )

    def record_result(self, prompt_id: str, reward: float, metadata: dict | None = None) -> None:
        program = self._programs[prompt_id]
        previous_uses = program.uses
        previous_reward_sum = program.reward_sum
        previous_metadata = dict(program.metadata)
        program.uses += 1
        program.reward_sum += reward
        if metadata:
            program.metadata.update(metadata)
        try:
            self._write("score", program)
        except Exception:
            program.uses = previous_uses
            program.reward_sum = previous_reward_sum
            program.metadata = previous_metadata
            raise

    def mutate(
        self,
        parent_id: str,
        template: str,
        generation: int,
        metadata: dict | None = None,
    ) -> PromptProgram | None:
        parent = self._programs[parent_id]
        try:
            validate_prompt_template(template)
        except PromptTemplateError as exc:
            self._reject_mutation(parent, template, generation, str(exc), metadata)
            return None
        child = PromptProgram(
            template=template,
            parent_id=parent.id,
            generation=generation,
            metadata=metadata or {"source": "mutation"},
        )
        return self.add(child)

    def all(self) -> list[PromptProgram]:
        return list(self._programs.values())

    def _write(self, event: str, program: PromptProgram) -> None:
        append_strict_jsonl(
            self._log_path,
            {"event": event, "program": program.to_dict()},
            quarantine_path=self._quarantine_path,
        )

    def _reject_mutation(
        self,
        parent: PromptProgram,
        template: str,
        generation: int,
        error: str,
        metadata: dict | None,
    ) -> None:
        parent.reward_sum -= 1.0
        rejected = list(parent.metadata.get("rejected_prompt_mutations", []))
        rejected.append({"generation": generation, "error": error})
        parent.metadata = dict(parent.metadata)
        parent.metadata["rejected_prompt_mutations"] = rejected
        append_strict_jsonl(
            self._quarantine_path,
            {
                "event": "reject",
                "parent_id": parent.id,
                "generation": generation,
                "template": template,
                "error": error,
                "metadata": metadata or {"source": "mutation"},
            },
        )
        self._write("penalty", parent)
