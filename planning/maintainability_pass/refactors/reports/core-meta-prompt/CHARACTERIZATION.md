# core/meta_prompt.py characterization

Evidence state: focused characterization gate passed; production refactor is
still blocked by adjacent prompt/loop handoffs.

The shared test-only wave added 209 lines to
`tests/core/test_meta_prompt.py`. Two initial expectation defects were found
and corrected in that test file only: a list input follows the current
non-JSON template path, and a wrong schema uses the explicit schema error.
The root-side Windows run now reports `94 passed` for the full focused module
(`8 passed, 86 deselected` for the corrected invalid-response subset).

Required cases cover normal seed/select/score/restore, malformed response
shapes, leading-brace parser routing, empty history, replay hash/mean drift,
rollback on score/penalty persistence failure, deterministic IDs, UTF-8, and
unterminated JSONL. No production writer is authorized in this wave because
the proposed seam still requires an explicit provider-context handoff with
`loop.py` and the test-only change must remain isolated from production code.
