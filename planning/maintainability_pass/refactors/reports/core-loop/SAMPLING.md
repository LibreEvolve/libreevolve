# `core/loop.py` Sampling and Mutation Slice

Agent: `01a069ce-a8c8-7513-8649-3b816ad53101`
Status: Wave 1 read-only inventory complete; tests not executed; evidence
`source-derived`, `test-derived` (assertions inspected), `proposed`,
`unverified`.

Stable anchors are `evolve()` (about line 856), `_PreparedCandidate` (207),
`_PreparedMutationRequest` (236), `_run_async_sampler_generation` (2054),
`_select_mutation_mode` (2308), `_apply_selected_workspace_mutation` (2425),
`_prepare_async_mutation_request` (2506),
`_prepare_candidate_from_async_mutation` (2755), and
`_commit_evaluated_candidate` (3034). Identity/cache helpers are near 46230,
46316, and 46458.

The run-owned RNG is shared with the database/islands and prompt sampler.
`mixed` parent selection consumes one draw for the 30% explore/70% exploit
decision; explicit strategies bypass that decision. Sequential proposals can
observe preceding state, while async sibling preparation merges in submission
order and cross-generation windows use pre-drain state. Exact-workspace cache
reuse and in-flight coalescing are distinct from candidate identity and
cross-run replay. Adaptive mutation records selected/effective modes and may
use opposite-format parser fallback.

Proposed seams are a shared request-preparation result and a shared response
normalization result. Keep `evolve()` responsible for budget checks, hooks,
evaluation, admission, rewards, persistence, and async merge ownership. Do
not move RNG creation, archive mutation, prompt reward, or worker merge policy
into extracted helpers.

Required characterization includes exact RNG draws, explicit-strategy bypass,
sync/async request metadata, cache-key invalidation and `diff_error` bypass,
mutation fallback metadata, partial batch ordering, candidate/parent/prompt
identity, call/reward order, admission order, and final RNG snapshot hash.
