# Paper manifest slice specialist reviews

Lane: `paper-manifest`
Primary: `libreevolve/tools/paper_manifest.py` (15,441 current physical lines)
Reviews: `01a0705b-6aee-7203-9f9f-ef79cf64ab2f` (inventory/claims),
`01a0705b-6de5-71c0-b633-f00517e5ef0f` (rehydration/atomicity), and
`01a07081-d6cf-74f2-8173-5da90648377c` (sidecar/source authority)

## Inventory and claim orchestration

The module imports roughly 270 authority/benchmark modules and owns the ordered
manifest, PDF, status, benchmark, sidecar, artifact, and freshness fan-out.
`validate_paper_manifest` is 1840–2301; status and benchmark inventory builders
are 2304–2782; the generic sidecar/authority family spans approximately
2785–12974; rehydration and CLI are 12977–13105; loaders and security helpers
are 13112–15437.

Public callers are the module CLI, `tests/test_paper_manifest.py`, and
`tests/test_follow_on_sources.py`; docs and CI invoke the module as a command.
Direction is `README/docs/CI/tests -> CLI -> manifest validator/rehydrator ->
PDF/manifest helpers -> authority modules -> papers/sidecars`. New authority
modules must not depend back on the orchestration module.

The manifest requires synchronized JSON/CSV rows, safe relative PDF paths,
allowed HTTPS URLs, canonical SHA-256, and structurally valid local PDFs. The
current inventory has 53 rows and 53 local matching PDFs; only the explicit
AlphaEvolve PDF is Git-tracked. Claim inventories are structural and explicitly
do not prove semantic status, freshness, benchmark reproduction, or owner
signoff.

## Rehydration and transaction slice

`rehydrate_paper_cache` dispatches row loading, existing-cache validation, and
download/temporary-file validation before `os.replace()`. Existing matching
PDFs and downloaded PDFs now receive structural validation, and invalid
downloads preserve the target. However, the read-only audit found that
`_load_rehydrate_rows` does not itself reject unsafe `file` values before
`rehydrate_paper_cache` computes `target = root / file_value`; existing unsafe
path coverage is for full manifest validation, not rehydration. This is a
deferred high-priority safety finding, not a silently accepted refactor.

Other unresolved boundaries include response closure for exceptions raised
before a response object exists, broken symlink/parent reparse handling,
TOCTOU between validation and replacement, absent fsync/directory durability,
unbounded download size, redirect-host validation, timeout semantics, and
Git subprocess timeout/error classification.

Recommended future seams are (1) manifest/JSON/CSV loader plus safe-path
preflight, (2) pure local-PDF inspector, (3) download transaction/transport,
and (4) CLI/report adapter. Preserve `urlopen`, `Request`, `os.replace`, hash,
PDF, `Path`, and subprocess monkeypatch seams until characterization expands.

Evidence: manifest source inspection found 15,441 lines and 53/53 local PDFs;
the current focused paper lane has `9` focused source/README tests and the
full `tests/test_paper_manifest.py` module later passed `717` tests. This
specialist review itself ran no new runtime validation and does not prove
native, network, or release behavior.
## Additional sidecar/source-authority specialist — Mendel

Agent `01a07081-d6cf-74f2-8173-5da90648377c` completed a read-only source
review with no tests or edits. The slice covers `validate_paper_manifest`,
the source/sidecar adapters, authority-root semantics, sidecar fallback,
download-row reconciliation, and ordered issue prefixes. The recommended
boundary keeps authority modules independent and centralizes adapter selection
only after root injection and issue order are characterized. Open questions
include `_repo_root()` versus injected validation roots, inconsistent missing-
sidecar policy, and unsafe source-row target construction. It is the fourth
paper-manifest review required for this large file; it does not authorize a
writer.
