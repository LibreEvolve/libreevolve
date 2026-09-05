# core/artifact_schema.py inventory

Evidence state: read-only Wave 1 report.

Measured shape is approximately 2,158 LOC and 23 module functions. The module
owns versioned records, artifact/manifest schemas, JSONL row contracts,
quarantine/retention validation, redaction-related boundaries, and compatibility
normalization across the run artifact family. It is coupled to database,
loop, CLI, prompt/meta-prompt, JSONL, provenance, and test fixtures.

The focused aggregate review reported 188 passed and two skipped across the
artifact-schema/runtime/CLI/meta/JSONL/redaction/LLM slices, with no failures;
this is a reported aggregate result, not a new root-side full-suite run.

The likely seam is a narrow schema registry/record-validation boundary. Keep
durable storage in `jsonl.py`, in-memory admission in `database.py`, and public
artifact compatibility wrappers stable. Child reviewer capacity was exhausted,
so the implementation barrier remains closed.
