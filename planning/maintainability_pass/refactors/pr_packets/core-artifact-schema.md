# PR packet — `core-artifact-schema`

- Primary: `libreevolve/core/artifact_schema.py`; proposed branch `refactor/core-artifact-schema`; external PR not opened.
- Allowlist: `libreevolve/core/artifact_schema.py`, `libreevolve/core/artifact_schema_record_contracts.py`, `tests/core/test_artifact_schema_characterization.py`.
- Scope: move JSONL/quarantine record-family declarations only; schema constants, validation, redaction, materialization, and inventory stay in the façade.
- Dependency PRs: `core-loop`, `core-jsonl`. Uniform measurements: 2,158/2,096 → 2,138/2,076 primary physical/nonblank LOC; support 97/89; decision proxy 155 → 155.
- Evidence: combined focused artifact/JSONL `86 passed`; AST, identity, schema equality, and durability ownership checks pass; verifier `01a06a52-8400-7352-beee-81d08ccb012b` PASS.
- Preserved contract: serialized keys, versions, record families, redaction, quarantine paths, and ownership. No unrelated paths staged.
- Risks/rollback: remove only the declaration delegation/support file. Full repository/runtime evidence remains separate.
