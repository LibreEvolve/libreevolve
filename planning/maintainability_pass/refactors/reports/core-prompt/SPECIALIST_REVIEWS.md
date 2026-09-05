# Core prompt slice specialist reviews

Lane: `core-prompt`
Primary: `libreevolve/core/prompt.py` (8,134 current physical lines)
Reviews: `01a0705b-646b-7f61-9286-fdb8bd846df4` (policy/context),
`01a0705b-679a-7b90-a897-7348639b8ee6` (feedback/failure/RNG), and
`01a07081-d3d6-7521-8323-65fb75adcafb` (template/context/budget)

## State and callers

`PromptSampler` and `build()` occupy 467–1099. The loop constructs one sampler
with the run-owned RNG at 933–948, calls it synchronously at 1343–1350 and
through async preparation at 2593–2603; the convenience wrapper is 393–401.
`build()` assigns `last_context_text` at 592 before later render/pack steps and
commits `last_metadata` at 1098. The sampler owns injected `random.Random`,
normalized variants/format options, and exposed mutable `last_*` values.

RNG draws for variant and format selection share the loop's run RNG, so moving
prompt draws can change deterministic parent-selection order. Async jobs carry
rendered prompts and copied diagnostics; the async snapshot does not include
sampler `last_*` or RNG state.

## Policy, rendering, and failure slices

Policy validation/application is at `prompt.py` 1303–1603 and the extracted
pure implementation is `prompt_context_policy.py` 496–1314. Template/input
validation is 1129–1212 and 2537–2842. Context ingestion/rendering is
2844–3511. Parent-code rendering is 3871–4252. Feedback rendering is
4255–6871, failure selection/policy accounting is 7105–7907, and failure-line
rendering is 7919–8134.

Current dependency direction is:

```text
candidate / redaction / metrics -> prompt_context_policy -> prompt renderer
-> PromptSampler.build -> loop / meta_prompt / config
```

`PromptSampler` preserves template channels, required-section packing, section
budget schema `libreevolve.prompt_section_budget.v1`, context-source metadata,
redaction/path boundaries, and shared `PromptTemplateError` identity. Feedback
selection filters have a fixed order (required/excluded errors, changed files,
stages, terms, repetition, score); legacy two-item failure tuples remain
accepted. Provider-facing prompt content and persisted/redacted history are
distinct contracts.

The safest next seam is failure selection/policy accounting behind a normalized
failure record. Context rendering and section budgeting are viable separate
seams. Feedback rendering and a transactional immutable build result are higher
coupling and require exact section ordering, caps, truncation, privacy, async,
and RNG characterization first.

Characterization: existing prompt evidence reports `390` focused passes,
including `last_*` update timing, defensive policy copying/hash stability,
supplied-RNG ordering, and process-global RNG isolation. Unresolved questions
include the public policy-facade signature/constant duplication, failed-build
mixed state, shallow metadata copies, provider-token overflow, raw-versus-
persisted context privacy, and thread/reentrancy ownership.
## Additional template/context/section-budget specialist — Pauli

Agent `01a07081-d3d6-7521-8323-65fb75adcafb` completed a read-only source
review with no tests or edits. The slice covers template field/format
validation, context filtering/ranking/rendering, section packing and budget
reports, plus `PromptSampler.build()` callers and `last_*` state. Candidate
pure seams require injected RNG/token counters, while the façade must retain
RNG order and mutable side-channel ownership. Open questions include atomic
`last_*` commits, duplicate template parsers, section-boundary truncation,
heuristic versus provider token counts, raw-context privacy, and async
reentrancy. It is the fourth prompt review required for this large file; it
does not authorize a writer.
