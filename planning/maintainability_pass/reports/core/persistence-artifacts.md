# Core component report: persistence and artifacts

Status: stopped-after-safety-stop; no shared product patch integrated.

Owned paths: `core/database.py`, `core/jsonl.py`, `core/artifact_schema.py`,
`core/best_artifacts.py`, and `core/budget.py`.

Agent: `01a06256-014d-71b3-ba15-11e353a76c40`. Independent verifier: none.

Evidence: the isolated lane was stopped before its persistence/artifact report
and verifier were available. Existing static measurements put `database.py` at
about 11,841 lines and its largest class at about 1,008 lines. No schema,
atomicity, promotion, or budget refactor is claimed.

Disposition: open/deferred pending characterization tests and a complete
module-level persistence slice.
