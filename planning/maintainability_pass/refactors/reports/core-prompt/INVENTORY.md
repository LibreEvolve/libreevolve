# core/prompt.py inventory

Evidence state: measured/read-only Wave 1 report.

Measured shape: 11,952 physical LOC, 11,251 logical/noncomment LOC, 342
function nodes, three classes, 4,543 statement nodes, and an aggregate
complexity proxy of 2,303. `PromptSampler` spans lines 466-1097; the largest
areas are context-policy normalization/application, token/section budgeting,
feedback/diagnostics, and failure-memory rendering.

Production consumers are loop, meta-prompt, and config. `last_metadata` and
`last_context_text` are mutable last-call side channels read by loop, while
meta-prompt owns prompt-history persistence/replay and provider telemetry lives
in the LLM ensemble. The proposed seam is a pure
`prompt_context_policy.py` contract with compatibility re-exports; it must
preserve exception identity, normalized key order, policy hashes, metadata
shapes, and async/sync caller behavior.
