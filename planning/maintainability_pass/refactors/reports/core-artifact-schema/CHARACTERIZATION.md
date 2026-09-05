# core/artifact_schema.py characterization

Evidence state: characterization complete; implementation barrier remains
conditional on coupling review and a narrow policy-only seam.

The test-only specialist added
`tests/core/test_artifact_schema_characterization.py`. It reports `24 passed`
for the characterization module and `50 passed` with the narrow artifact and
documentation boundary tests; compilation and whitespace checks passed.
JSONL append durability remains separately owned by the JSONL lane.

Before extraction, characterize every versioned record family, legacy-v0
restore path, malformed marker/error taxonomy, redaction and retention mode,
unknown-field policy, and CLI/meta-prompt artifact round trip. Preserve the
distinction between schema validation and JSONL durability. Do not schedule a
writer until the independent coupling review closes this gap and the seam
preserves schema policy authority.
