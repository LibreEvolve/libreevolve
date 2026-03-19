from __future__ import annotations
from dataclasses import dataclass, field
from math import inf
from uuid import uuid4

@dataclass
class Program:
    id:         str           = field(default_factory=lambda: uuid4().hex)
    code:       str           = ""
    fitness:    float         = -inf
    generation: int           = 0
    parent_id:  str | None    = None
    lineage:    list[str]     = field(default_factory=list)
    metadata:   dict          = field(default_factory=dict)
