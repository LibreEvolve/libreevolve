# `core/loop.py` refactor

Primary path: `libreevolve/core/loop.py`.
Support paths: `libreevolve/core/loop_models.py`,
`tests/core/test_loop_characterization.py`.

Design: move only `_PreparedCandidate`, `_PreparedMutationRequest`,
`_PendingAsyncMutation`, and `_PendingCandidateEvaluation` into a frozen,
data-only module. Keep `evolve()`, all orchestration phases, mutable state,
queues, persistence, hooks, and finalization in `loop.py`.

Measurements from the lane snapshot:

| metric | before (`HEAD`) | after primary | after with support |
|---|---:|---:|---:|
| physical LOC | 49,605 | 49,548 | 49,625 |
| logical non-comment LOC | 47,916 | 47,865 | 47,932 |
| functions | 804 | 804 | 804 |
| classes | 11 | 7 | 11 |
| decision proxy | 8,008 | 8,008 | 8,008 |
| largest function | `evolve`, 1,196 | `evolve`, 1,196 | `evolve`, 1,196 |

The combined LOC increase is the explicit value-module boundary; the primary
file is smaller and its orchestration AST is unchanged. The new module has
one production importer and no callable or side-effect code. Public/private
class identity and signatures are preserved through compatibility imports.

Evidence: characterization `11 passed`; full loop regression `465 passed, 2
skipped`; independent verifier `01a06a0e-41ef-7393-a012-c8da889ab98c` PASS.
Async evidence is local-process only. No PR was opened and no Git staging or
commit occurred.
