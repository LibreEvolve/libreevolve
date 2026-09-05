# PR packet — `paper-manifest`

- Primary: `libreevolve/tools/paper_manifest.py`; proposed branch `refactor/paper-manifest`; external PR not opened.
- Allowlist: `libreevolve/tools/paper_manifest.py`, `tests/test_paper_manifest.py`.
- Scope: MR-007 behavior-fix prerequisite only: validate downloaded temporary PDFs before replacement and validate matching existing caches before `verified_existing`; later sidecar extraction remains deferred.
- Dependency PR: `benchmark-matrix`; baseline HEAD `7983544e28e478eb6a0f5c35e4af5a86b125cea2`.
- Measurements: full primary remains the large evidence-tooling module; no extraction after-measurement is claimed. Current focused selection `9 passed, 708 deselected in 38.35s`; full 717-test module completed `717 passed in 1:18:55`.
- Evidence: writer `01a06a9b-b505-77d1-a33c-71b8fb56fad1`; fresh verifier `01a06fa4-c3c2-7d41-bfb0-aba5f355cfa9` focused PASS; compile/diff scope pass.
- Preserved contract: valid cache/download status, response closure, redacted diagnostics, temporary cleanup, link checks, and same-filesystem replacement semantics. Risks: parsing overhead and concurrent TOCTOU remain.
- Rollback: revert only the two MR-007 hunks after preserving the dirty-path ledger. No unrelated paths staged.
