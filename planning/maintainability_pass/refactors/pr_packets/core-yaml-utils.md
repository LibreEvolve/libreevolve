# PR packet — `core-yaml-utils`

- Primary: `libreevolve/core/yaml_utils.py`; proposed branch `refactor/core-yaml-utils`; external PR not opened.
- Allowlist: `libreevolve/core/yaml_utils.py`, `tests/core/test_yaml_utils_characterization.py`.
- Status: no-op; no writer authorized. Dependencies: none.
- Measurements: 67 physical LOC, one class, four functions; no post-refactor value because this is a small pure parser façade.
- Evidence: Windows focused `54 passed in 0.50s`; loader/boundary record `339 passed, 8 skipped`; verifier `01a06fa4-eef1-7722-96c0-27a8f34a05be` accepts the no-op; compile passes.
- Preserved contract: duplicate-key detection, safe-load errors, redaction, and caller-owned configuration/problem policy remain in place.
- Risks/rollback: no production patch; future edge characterization may cover unknown tags, multi-document YAML, merge keys, and unhashable keys. No unrelated paths staged.

