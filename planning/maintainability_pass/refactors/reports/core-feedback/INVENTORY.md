# core/feedback.py inventory

Evidence state: read-only Wave 1 report.

The module is approximately 1,312 LOC with 52 functions. `apply_llm_feedback`
is about 238 lines and has a branch/decision complexity proxy of 221. It
combines feedback normalization, diagnostic rendering, truncation/redaction,
evaluator-facing context, and compatibility handling. It is coupled to loop,
prompt, evaluator, plugin, artifact, and test paths.

The proposed seam is a pure feedback-boundary value/diagnostic renderer that
returns bounded, redacted records. Keep evaluator execution, prompt assembly,
plugin ordering, and persistence ownership outside it. The lane must reconcile
the source policy with documentation that may incorrectly imply verbatim
feedback retention.
