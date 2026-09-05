# `core/prompt.py` implementation record

Primary path: `libreevolve/core/prompt.py`.

Support path: `libreevolve/core/prompt_context_policy.py`.

Status: narrow context-policy extraction is present in the shared checkout;
independent verifier `01a06a72-9795-7fe1-b247-2c60c1fdac70` returned `PASS` for
the final current source. This is an implementation record, not a full-suite,
clean-checkout, or runtime success claim. The broad prompt/feedback/rendering
split remains deferred.

## Implemented decision

The extracted seam is the context-policy schema, normalization, and validation
family. `prompt_context_policy.py` contains the policy constants/defaults,
`validate_prompt_context_policy`, and the 119 top-level
`_validate_prompt_context_*` validators. It owns validation of policy fields
for section disabling and priority, mutation-instruction controls, parent
metrics/code selection, inspiration selection, feedback and diagnostic field
caps, validator/artifact/output policy, prompt-format weights, recent-failure
selection, and plugin-context controls.

The following remain in `prompt.py`: `PromptSampler`, template and format
rendering, `apply_prompt_context_policy`, section packing and token/character
budgets, feedback/diagnostic/artifact rendering, inspiration rendering,
failure-memory rendering, `prompt_context_policy_sha256`, and all mutable
last-call state. The extraction therefore moves policy validation only; it
does not move provider calls, loop orchestration, persistence, evaluator
authority, plugin hooks, or prompt rendering.

The support module has no `Problem`, `PromptSampler`, loop, LLM, filesystem,
or persistence dependency. Its ordinary validation dependencies are
`normalize_candidate_path`, `redact_sensitive_text`,
`validate_program_metrics`, `math`, `re`, and `Mapping`.

## Compatibility boundary

The public façade keeps the original
`validate_prompt_context_policy(value)` signature in `prompt.py`. The façade
wildcard-imports the support module's exported constants and private policy
validators, then aliases the support entry point as
`_validate_prompt_context_policy`. The façade wrapper pre-validates the three
context-dependent path channels with the existing prompt-owned grammar:

- `context_source_paths`;
- `recent_failure_required_changed_files`; and
- `recent_failure_excluded_changed_files`.

Those normalized lists are passed to the support entry point through its
keyword-only `validated_context_source_paths`,
`validated_recent_failure_required_changed_files`, and
`validated_recent_failure_excluded_changed_files` arguments. The support
module uses `_VALIDATED_CONTEXT_POLICY_PATHS_UNSET` to reject non-empty raw
values that bypass the façade. This replaces the intermediate mutable direct-
context callback: direct-context validation remains in `prompt.py`, while
the policy module receives explicit normalized data.

`PromptTemplateError` is support-owned and re-exported by the façade. The
support module defines the single `ValueError` subclass without importing the
façade, while `prompt.py` imports and exposes that same object. This preserves
exception identity for support-first and façade-first imports without a
configuration callback or import cycle. The guarded support binding also keeps
the exception and validated-path sentinel stable across support-module reload.

`__all__` in the support module exports the policy constants, the policy entry
point, and the `_validate_prompt_context_*` family. Existing consumers still
import from `libreevolve.core.prompt`; no consumer was redirected to the
support module.

## Preserved prompt contracts

The `PromptSampler` dataclass fields and `build` call shape remain in
`prompt.py`. Its injected `random.Random` remains the only sampler RNG:
variant selection and format-option selection continue to consume
`self.rng` in the existing order, with no process-global RNG ownership added.

`build` still overwrites `last_context_text` after context rendering and
`last_metadata` after the complete metadata record is assembled. Policy
normalization continues to make defensive lists/dictionaries, policy hashes
remain produced by the façade's canonical `prompt_context_policy_sha256`, and
the rendered prompt, policy metadata, section-budget metadata, feedback and
failure-memory field names, caps, ordering, redaction, and hashes remain
owned by the existing renderer. Synchronous and asynchronous loop callers
continue to observe the same `last_*` side channels; the loop still copies
those records at its existing handoff points.

These are preserved-by-design contracts and characterization targets. They
are not independently verified by this record.

## Changed paths and repair history

The implementation writer and repair writer changed only these production
paths for this lane:

- `libreevolve/core/prompt.py` — support import, compatibility alias/wrapper,
  and the existing prompt-owned path validators retained around the moved
  policy block;
- `libreevolve/core/prompt_context_policy.py` — new policy validation module.

The separate characterization specialist added
`tests/core/test_prompt_characterization.py`; it is test evidence, not part
of the production implementation path. This record does not modify that
test, the existing prompt tests, or any other lane.

The coupling review first rejected a broad extraction and recommended only a
pure context-policy seam, with RNG, rendering, and `last_*` state retained in
the façade. During the first implementation attempt, an intermediate support
snapshot had an empty `_redact_sensitive_text` function body, producing an
`IndentationError` during imports and blocking feedback/meta-prompt/JSONL
collection. Repair agent `01a06a4c-6dd2-7803-baf3-b950bb143d89` restored the
policy validators, removed the misplaced dependency implementations, and
then replaced the mutable direct-context callback with the explicit
normalized-path arguments described above. A final repair guarded the
reload-sensitive validated-path sentinel. Independent verifier
`01a06a72-9795-7fe1-b247-2c60c1fdac70` then recorded compilation, `390 passed`,
support-first/facade-first reload identity, path/error safety, and AST/import
checks as PASS.

## Measurements

The `before` column is the Wave 1 `INVENTORY.md` measurement from `HEAD`.
The after columns are recalculated from the current post-repair files. The
support module's extra compatibility arguments and façade wrapper account
for a small combined AST increase; these numbers do not establish a net
maintainability or complexity improvement.

| metric | before (`HEAD`) | after primary | after support | combined |
|---|---:|---:|---:|---:|
| physical LOC | 11,952 | 8,259 | 4,156 | 12,415 |
| logical/non-comment LOC | 11,251 | 7,794 | 3,901 | 11,695 |
| function nodes | 342 | 223 | 122 | 345 |
| classes | 3 | 3 | 1 | 4 |
| statement AST nodes | 4,543 | 2,838 | 1,792 | 4,630 |
| largest function | `validate_prompt_context_policy`, 807 | `build`, 579 | `validate_prompt_context_policy`, 819 | same, 819 |

The inventory's aggregate complexity proxy is 2,303. The current raw
structural decision counts are 1,144 for the primary and 670 for the support
module, but the historical aggregate proxy method is not documented well
enough to claim those are comparable after-values. Complexity reconciliation
is pending; no complexity reduction is claimed.

## Dependency edges and ownership limits

- `core.loop` remains the main runtime consumer of `PromptSampler`, policy
  metadata, `PromptTemplateError`, and `last_*` records. It owns synchronous
  and asynchronous proposal/evaluation handoffs, not policy validation.
- `core.meta_prompt` continues to import policy validation, policy hashing,
  template validation, and `PromptTemplateError` from `core.prompt`; it also
  owns prompt-program identity, history persistence, replay, and mutation
  parsing.
- `core.config` retains its lazy prompt imports and exception translation.
- `core.prompt` still depends on candidate path rules, redaction, `Program`,
  and `Problem`; only the narrow validation family is delegated to the
  support module.
- JSONL/artifact schemas, failure-history persistence, evaluator metric
  authority, plugin scoring, provider roles, and loop scheduling remain in
  their owning lanes. No new persistence or runtime boundary is introduced.

The support module's direct-call sentinel behavior and the explicit normalized
path handoff were independently checked for reload stability, error-message
compatibility, and traversal safety. Direct support callers must either
provide the three normalized path channels or use empty/`None` values for
them; the façade remains the compatibility entry point. Rendering constants,
RNG ownership, and mutable `last_*` state remain façade-owned.

## Evidence limitations and next gate

The characterization evidence consists of four added tests covering defensive
policy copies and deterministic hashes, `last_context_text`/`last_metadata`
overwrite behavior, run-owned RNG draw order, and process-global RNG
isolation. The existing focused prompt module reported `386 passed` before
the added cases; the final focused result is `390 passed`. Independent
verifier `01a06a72-9795-7fe1-b247-2c60c1fdac70` independently confirmed the
current final diff, import/reload identity, path safety, and AST/import
ownership constraints.

Still unverified are the full non-integration suite as a source-stable root
gate, native-only behavior, package/build gates, provider behavior,
OCI/security-sandbox behavior, distributed execution, and end-to-end
host/provider integration. No branch, PR, commit, or merge is recorded for
this lane.

The verifier gate must compare public and compatibility-private signatures,
normalized policy values and hashes, all three path-validation handoffs,
exception identity, RNG state/draw order, `last_*` eager-copy behavior,
rendered section/metadata contracts, and prompt/loop/meta-prompt/config test
results. It must label any dirty-checkout attribution and keep static,
focused-test, build, runtime, and end-to-end evidence separate.

## Rollback

The implementation is reversible as a two-path change: remove the support
import/alias/wrapper from `prompt.py`, restore the policy validation block to
its original façade location, and remove the new support module in an
isolated lane. Keep the characterization test and its evidence as historical
coverage. Do not reset, clean, stash, or broadly revert the shared checkout;
any rollback must be path-scoped and reviewed against the dirty-path ledger.
