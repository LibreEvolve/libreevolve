# `core/meta_prompt.py` refactor disposition

Primary path: `libreevolve/core/meta_prompt.py`.

Status: dependency-blocked; no production writer authorized in this wave. The
lane has characterization evidence, but it does not have an accepted seam
whose ownership and persistence behavior are sufficiently independent to
move safely. No production or support-file refactor is recorded here.

## Measured shape

The existing inventory is a static, read-only measurement of 919 physical LOC,
836 nonblank LOC, three classes, 29 top-level functions, and 15 methods.
`PromptDatabase` is approximately 411 LOC. The largest or most consequential
symbols include `record_result`, `parse_prompt_mutation_response`, `mutate`,
and `_program_from_history_record`. These measurements describe the current
shape; they are not evidence of a reduction or an improvement after a
refactor.

The module currently combines these responsibilities:

- prompt-program identity, lineage, selection, scoring, mutation, and
  deterministic IDs;
- template/context-policy validation and mutation-response parsing;
- history replay, schema/hash checks, defensive snapshots, quarantine, and
  redacted reference/rejection records; and
- penalty/reward state transitions with rollback when append operations fail.

## Decision and ownership boundary

The safe current disposition is a no-op for production code. A broad split of
`PromptDatabase`, parser code, and history storage would cross several
behavioral boundaries at once. In particular:

- `core/prompt.py` supplies the template and context-policy contracts and
  their validation/hash behavior. `meta_prompt.py` must not create a second
  policy authority or alter the compatibility exception/API surface.
- `core/loop.py` owns provider context assembly, synchronous/asynchronous
  orchestration, provider requests, runtime joins, and prompt diagnostics. It
  consumes the prompt mutation result and links prompt-program IDs and policy
  metadata into candidate history. Those provider-context and `last_*` prompt
  handoffs are not database helpers and must remain outside a future pure
  lifecycle seam.
- `core/jsonl.py`, `core/artifact_schema.py`, redaction, and database/history
  consumers provide adjacent persistence and record contracts. Moving their
  writes into a new prompt module could change quarantine ordering, schema
  envelopes, redaction, or the rollback guarantee for reward and penalty
  updates.

The candidate for a later, narrow seam is a dependency-light prompt-arm
lifecycle/record contract: value validation, immutable snapshot/transition
semantics, and deterministic identity inputs. It is not a provider adapter,
prompt renderer, loop scheduler, JSONL writer, or generalized persistence
layer. The candidate remains blocked until the `core/prompt.py` policy seam
and the `core/loop.py` handoff are explicitly reconciled, and the artifact/
JSONL ownership of prompt-history records is settled.

## Future seam acceptance criteria

A future writer may proceed only when all of the following are documented and
verified in an isolated worktree:

1. The new module has a one-way import boundary to value-level policy/schema
   contracts and does not import `core.loop`, an LLM/provider adapter, or
   perform file I/O, redaction, hooks, or runtime joins.
2. `PromptProgram`, `PromptDatabase`, `parse_prompt_mutation_response`, and
   `validate_prompt_program` retain their public/private compatibility
   imports, signatures, tuple shape, exception identity, copy behavior, and
   deterministic ID results. Any moved value type is re-exported so existing
   patch points and callers continue to resolve to the same object.
3. Prompt context-policy inheritance and diagnostics remain owned by the
   prompt/loop boundary. The seam does not consume provider context or mutate
   PromptSampler's RNG, `last_context_text`, or `last_metadata` channels.
4. History replay, schema/hash validation, quarantine and redaction, append
   ordering, reward/penalty persistence, and in-memory rollback remain in an
   explicit façade/storage boundary with byte- and record-level compatibility
   tests.
5. Characterization covers valid and malformed mutation responses, empty and
   unterminated history, replay hash/mean drift, duplicate/unknown parents,
   deterministic IDs, UTF-8, defensive copies, and write-failure rollback.
   The focused meta-prompt, prompt, and relevant loop suites pass before and
   after movement, with an independent non-authoring verifier checking AST,
   imports, signatures, and alias identity.
6. The resulting primary file has a measured improvement or a clearly bounded
   ownership benefit; moving code into a support file merely to reduce a line
   count is insufficient.

## Rollback and no-op disposition

Nothing was moved, staged, committed, or opened as a PR for this lane. The
current no-op is therefore already the rollback point and leaves the shared
checkout's existing dirty paths untouched. If a future isolated attempt fails,
roll back only that attempt's new support module and compatibility-import
edits, restore the primary module, and rerun the characterization and focused
loop/prompt gates. Do not reset, clean, stash, or broadly revert the shared
checkout.
