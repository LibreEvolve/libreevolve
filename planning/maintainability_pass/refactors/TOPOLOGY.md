# Maintainability delegation topology and scheduler record

Captured: 2026-09-05
Coordinator: `root-coordinator` (primary thread)

## Limits and observed hierarchy

The governing prompt permits at most 50 active child slots and nesting depth 3
with the root at depth 0. The lane matrix records one file lead and one
implementation writer per primary file. Specialists and verifiers have empty
write scopes; generated artifacts have their own primary lane when they need a
separate authorization.

The agent tool exposed direct root dispatch for this run. The observed
execution hierarchy is therefore:

```text
root coordinator (depth 0)
  └── lane lead / specialist / writer / verifier (depth 1)
```

No descendant agent spawned another agent, so the observed maximum depth is 1
(within the allowed depth 3). Module/family ownership and dependency order are
represented by `FILE_MATRIX.json`; this is a shallower execution realization
of the prompt's root → family lead → file lead → specialist roles, not a claim
that hidden module-lead processes existed.

The scheduler rule is: one writer for one primary path, disjoint write scopes,
fresh non-authoring verifier after a writer, and no integration/publication
without explicit authorization. Queue state and terminal evidence live in
`FILE_MATRIX.json`, `PR_INDEX.jsonl`, and `AGENT_REGISTRY.jsonl`.

## Family and file ownership

| Family | File lanes |
| --- | --- |
| core-orchestration | `core-loop` |
| persistence-artifact | `core-database`, `core-jsonl`, `core-artifact-schema`, `core-best-artifacts`, `core-budget` |
| prompt-feedback | `core-prompt`, `core-feedback`, `core-meta-prompt` |
| evidence-tooling | `paper-manifest`, `cli` |
| benchmark-contract | `benchmark-matrix` |
| configuration-contract | `core-config`, `core-yaml-utils`, `problem-loader` |
| docs-evidence-boundary | `roadmap-non-goal-sidecar`, `roadmap-non-goal-boundary` |

The first 15 rows are the original target lanes from the orchestration prompt.
The two roadmap rows are an explicitly recorded auxiliary gate: the source/test
lane depends on the separately authorized generated sidecar lane.

## Current scheduler assignments

Each row below is coordination-derived from the matrix and registry. The
registry is the authoritative append-only event history for status transitions.

| Lane | Lead | Writer | Fresh verifier | Dependencies | State |
| --- | --- | --- | --- | --- | --- |
| `core-loop` | `01a069e6-7bbd-7532-acae-c77b833df979` | `01a06a06-fddb-7b13-9676-4af41fea53ea` | `01a06a0e-41ef-7393-a012-c8da889ab98c` | — | verified pass |
| `core-database` | `01a069d0-7a2a-7472-a199-788b5c8c167c` | none | `01a06fa4-e0a3-7d43-aaea-9ea8dddc5a9d` | loop | characterized no-op; four read-only reviews complete |
| `core-jsonl` | `01a069d0-8e77-7a41-8169-7e897d880583` | `01a06a4e-76e8-7513-a6f1-619cb9c4e768` | `01a06a52-807e-7a62-879f-7894ec8c55f7` | loop | verified conditional |
| `core-artifact-schema` | `01a069d0-976e-7423-836d-d80aa4c39372` | `01a06a4a-ce96-7a53-afc9-f679c0e72c33` | `01a06a52-8400-7352-beee-81d08ccb012b` | loop, jsonl | verified pass |
| `core-best-artifacts` | `01a069d0-a260-78c0-b21c-c3bfab37997c` | none | `01a06fa4-e367-7830-877a-fdc499cb07cf` | loop, schema | characterized no-op |
| `core-budget` | `01a069d0-bd55-7090-a9bd-5cd88ee10c22` | `01a06a4f-2635-7671-b141-26772442bf9f` | `01a06a63-4b58-7661-a978-272442b9961e` | loop | verified conditional |
| `core-prompt` | `01a069d0-aa0b-7242-9e8f-52f9a6682f5e` | `01a06a4c-6dd2-7803-baf3-b950bb143d89` | `01a06a72-9795-7fe1-b247-2c60c1fdac70` | loop | verified pass; four read-only reviews complete |
| `core-feedback` | `01a069d0-b10b-7001-84a2-de1b63fd8efb` | none | `01a06fa4-e69a-7f23-b4e8-ddd61649f309` | prompt | deferred/no-op |
| `core-meta-prompt` | `01a069d0-d7fa-7042-88a5-7b2ca4f3111d` | none | `01a06fa4-e97e-7833-a413-f4e8718b7db3` | prompt, loop | dependency-blocked/no-op |
| `paper-manifest` | `01a069d0-ccfc-7072-b92d-aea5c8f9e79f` | `01a06a9b-b505-77d1-a33c-71b8fb56fad1` | `01a06fa4-c3c2-7d41-bfb0-aba5f355cfa9` | matrix | verified conditional; four read-only reviews complete |
| `cli` | `01a069d0-e7ae-7bc3-b1eb-b622d737f40f` | `01a06afc-5d03-7b21-8b36-60e0c5bdc9a9` | `01a06fcd-6417-7233-9dbf-b28509dd70a2` | loop, config, loader | verified conditional |
| `benchmark-matrix` | `01a069d0-f946-7381-9805-0d1ae33abdff` | `01a06a03-f527-7f42-a4b9-e7aa8a19f665` | `01a06a07-ad4d-7641-aa55-fe6b0e6690c9` | — | verified conditional |
| `core-config` | `01a069d1-1bf6-7720-8a6d-912ffcad6a7a` | none | `01a06fa4-ec39-7cb2-b357-a0fd6b25f14d` | yaml, loader | characterized no-op |
| `core-yaml-utils` | `01a069d1-2ef9-7e61-bb9c-d646589ed973` | none | `01a06fa4-eef1-7722-96c0-27a8f34a05be` | — | characterized no-op |
| `problem-loader` | `01a069d1-42de-7d13-b044-267056f2a5a1` | `01a069ea-e070-77e1-8a17-132b974077a5` | `01a069f4-5cec-7bc2-bb61-dc6d2204337a` | config, yaml | verified pass |
| `roadmap-non-goal-sidecar` | `01a0704f-ad08-74c1-8d59-a8f6bb53b08c` | `01a07060-9573-70f0-937d-4d0cf4b9abff` | `01a07064-4df3-7441-a5e4-0030d92383b4` | — | verified pass; EOL-qualified |
| `roadmap-non-goal-boundary` | `01a0704f-ad08-74c1-8d59-a8f6bb53b08c` | `01a07049-c76f-7020-9816-c6e3aed63c4f` | `01a07071-1c53-78b2-80e0-32690ebcc5d9` | sidecar | source verifier PASS, EOL-qualified |

## Parallel work and queue evidence

The continuation dispatched nine large-file specialists (three explicit
specialists plus the inventory review for each of database, prompt, and
paper-manifest), giving four reviews per oversized primary file. Their write
scopes were empty and their lane assignments were disjoint. All nine completed
read-only reviews. The sidecar writer completed before its verifier was
dispatched. The first slice-schema writer shut down without a result and was
explicitly replaced by `01a07068-7b65-7dc1-93b4-a50fc0cc61dd`; its lifecycle
closure is retained in the append-only registry.

The registry records the observed agent lifecycle, including closures,
shutdown/replacement, read-only specialist results, and conditional red-team
results. Scheduler assertions, capacity/depth replay, and the quiescent latest
status audit are in `SCHEDULER_AUDIT.md`; no claim of completion is made solely
from queued assignments.

## Boundary of this record

This file proves coordination structure and ownership bookkeeping, not code
correctness. Static, build, runtime, native-Windows, provider, OCI, and
end-to-end evidence remain separate gates in `FINAL_REPORT.md`.
