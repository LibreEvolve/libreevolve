# `core/meta_prompt.py` verification

Fresh independent non-authoring verifier: `01a06fa4-e97e-7833-a413-f4e8718b7db3`.
Verdict: **blocked/no-op accepted for this wave**. Windows focused tests pass
`94 passed in 1.25s`; static shape and scoped-diff checks pass. The prompt/loop
lifecycle and JSONL/quarantine ownership contract remains unresolved.

Verdict: `BLOCKED / NO-WRITER`.

This report verifies the characterization and the decision not to move
production code. It is not a refactor-pass report: no production seam was
implemented, so there is no after-movement regression or structural proof to
claim.

## Evidence ledger

| claim | evidence class | result | boundary |
|---|---|---|---|
| Current module shape | static/source-derived | 919 physical LOC, 836 nonblank LOC, 3 classes, 29 top-level functions, 15 methods; `PromptDatabase` about 411 LOC | Inventory measurement, not a maintainability improvement claim |
| Prompt lifecycle behavior | test-derived | Focused `tests/core/test_meta_prompt.py`: 94 passed in the existing Windows Python 3.12 run | Tests exercise the current implementation; no code was moved |
| Added characterization cases | test-derived | Test-only wave added 209 lines covering normal seed/select/score/restore, malformed responses, parser routing, empty history, replay drift, rollback, deterministic IDs, UTF-8, and unterminated JSONL | Test expectations were corrected for the current non-JSON path and explicit schema error |
| Provider/loop handoff | unverified for a future seam | Not accepted as an independent contract | `core/loop.py` owns provider context, orchestration, async joins, prompt linkage, and runtime diagnostics |
| Prompt side-channel compatibility | unverified for a future seam | No movement proof exists | `core/prompt.py` owns template/context policy behavior; RNG and `last_*` channels must remain stable |
| Persistence/rollback boundary | unverified for a future seam | No new storage or lifecycle boundary was tested | JSONL/schema/quarantine/redaction ordering and write-failure rollback remain in the current implementation |
| Provider/network/distributed/e2e behavior | unverified | No such evidence was produced by this lane | Focused local tests do not establish these claims |

## Characterization gate

The existing characterization reports a focused Windows Python 3.12 run of
`tests/core/test_meta_prompt.py` with `94 passed`; the corrected invalid-
response subset reports `8 passed, 86 deselected`. The cases include:

- normal seed, selection, scoring, mutation, restoration, and replay;
- malformed response shapes and the leading-brace JSON routing boundary;
- empty history, unterminated JSONL, replay hash/mean drift, and schema checks;
- score/penalty persistence failure with in-memory rollback;
- deterministic IDs, UTF-8, duplicate and unknown-parent rejection, and
  defensive copies; and
- prompt context-policy inheritance and mutation metadata.

These are test-derived observations of the current source. They establish a
useful behavior baseline but do not establish that a future module boundary
is correct, that the full repository non-integration suite is green, or that
provider/runtime behavior works outside the local test process.

## Blocking dependencies and verification required

The lane remains blocked pending a written contract for the handoff among
`meta_prompt.py`, `prompt.py`, and `loop.py`. A verifier must specifically
check that parsing still returns the same `(template, context_policy,
metadata)` contract, policy inheritance and diagnostics are unchanged, and
loop callers retain prompt-program IDs and provider-context provenance.

The verifier must also prove that a proposed lifecycle seam does not move
JSONL append/quarantine responsibility without preserving schema envelopes,
redaction, ordering, replay validation, and state rollback. Import-order,
private patch-point, exception-identity, deterministic-ID, and defensive-copy
checks are required. The verifier must be independent of the writer and must
separate source/static, test, build, runtime, and end-to-end evidence.

## No-writer disposition

No production writer ran for this lane, and no production or support path was
changed for it. Consequently, there is no branch, PR, build artifact, or
after-refactor test result to verify. The disposition is reversible and
complete for the current wave: retain `core/meta_prompt.py` until the future
seam acceptance criteria in `REFACTOR.md` are met.
