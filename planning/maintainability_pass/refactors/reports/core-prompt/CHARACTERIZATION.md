# core/prompt.py characterization

Evidence state: characterization complete; production seam remains blocked
pending a final contract reconciliation and independent writer gate.

The replacement test-only specialist added
`tests/core/test_prompt_characterization.py` with four tests for
`last_context_text`/`last_metadata` overwrite and eager-copy behavior, policy
hash determinism, and run-owned/global RNG isolation; all four passed. The
existing focused prompt module independently reports `386 passed`.

Required cases are default/variant template assembly, strict versus
compatibility semantics, context-policy schema/hash and ordering, exact token
and character boundaries, required-section overflow, bounded feedback and
failure memory, deterministic RNG/ranking, malformed parents/artifacts, and
`last_metadata`/`last_context_text` side-channel behavior through loop callers.
The coupling review recommends extracting only the pure context-policy
contract into `core/prompt_context_policy.py`, while retaining PromptSampler's
rendering, RNG, and `last_*` channels. No production writer is authorized until
the new tests are integrated with the existing prompt/loop suite and the
compatibility re-export/exception identity plan is recorded.
