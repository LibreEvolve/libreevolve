# Core component report: evaluation and validator policy

Status: integrated root fix; focused verification passed; independent verifier
incomplete.

Owned paths: `libreevolve/core/evaluator.py`,
`libreevolve/core/validator_policy.py`.

Agent: `01a06255-fc9c-78c3-8500-78c9420f9441`. Conditional verifier:
`01a0625c-b85a-75d2-a664-c022e2407b17`; its test run was interrupted. The
independent cross-platform review found no new defect in this component.

Change: top-level declared evaluator data include/exclude policy is forwarded
through direct evaluator preflight, with an import-time regression test.

Evidence: `tests/core/test_evaluator.py` and validator-policy slice passed
`283 passed in 28.75s`. An adjacent candidate-language failure was tracked
separately; no hostile-code sandbox or live runner claim is made.
