# LLM component report: ensemble and scheduling

Status: stopped-after-safety-stop; no shared patch integrated; verifier absent.

Owned paths: `ensemble.py`, `provider_retry.py`, `feedback_calibration.py`.

Agent: `01a06257-001f-7e10-b1a5-bd2fb9c08508`. Independent verifier: none.

Evidence: no complete component report or verifier result was returned. UCB
accounting, retry fairness, stochasticity, and budget behavior remain
source-derived/test-derived only from pre-existing coverage.

Disposition: open; add deterministic fake-provider characterization tests
before scheduling refactoring.
