from __future__ import annotations
from dataclasses import dataclass, field
from math import inf
from uuid import uuid4
from libreevolve.core.candidate import CandidateWorkspace

@dataclass
class Program:
    id:         str           = field(default_factory=lambda: uuid4().hex)
    code:       str           = ""
    fitness:    float         = -inf
    generation: int           = 0
    parent_id:  str | None    = None
    lineage:    list[str]     = field(default_factory=list)
    metadata:   dict          = field(default_factory=dict)
    metrics:    dict[str, float | bool | str | int] = field(default_factory=dict)
    evaluation: dict          = field(default_factory=dict)
    files:      dict[str, str] = field(default_factory=dict)
    primary_file: str          = "main.py"

    def __post_init__(self) -> None:
        if self.files and not self.code:
            ws = CandidateWorkspace(self.files, self.primary_file)
            self.files = dict(ws.files)
            self.primary_file = ws.primary_file
            self.code = ws.code
        elif self.code and not self.files:
            ws = CandidateWorkspace.from_code(self.code, self.primary_file)
            self.files = dict(ws.files)
            self.primary_file = ws.primary_file

    def workspace(self) -> CandidateWorkspace:
        if self.files:
            return CandidateWorkspace(self.files, self.primary_file)
        return CandidateWorkspace.from_code(self.code, self.primary_file)
